#!/usr/bin/env python3
"""Retrieve recordings from USB (or local) and upload to cloud for client delivery.

Usage:
    python scripts/retrieve_and_upload.py                  # auto-detect USB
    python scripts/retrieve_and_upload.py --dir /path/to/  # explicit directory
    python scripts/retrieve_and_upload.py --local          # use local recordings/
    python scripts/retrieve_and_upload.py --no-upload      # pack ZIP only, no upload

Requires:
    pip install requests
    Environment variable WETRANSFER_API_KEY (or passed via --api-key)
"""

import argparse
import getpass
import json
import os
import shutil
import sys
import time
import zipfile
from pathlib import Path

_BASE_DIR = Path(__file__).resolve().parent.parent
_CONFIG_DIR = _BASE_DIR / "config"


def find_usb_recordings() -> Path | None:
    user = getpass.getuser()
    base = Path("/media") / user
    if not base.is_dir():
        return None
    for entry in base.iterdir():
        candidate = entry / "enregistrements"
        if entry.is_mount() and candidate.is_dir():
            return candidate
    return None


def load_event_name() -> str:
    config_path = _CONFIG_DIR / "config.event.json"
    if config_path.exists():
        with open(config_path) as f:
            data = json.load(f)
        return data.get("event", {}).get("couple_name", "evenement")
    return "evenement"


def build_zip(recordings_dir: Path, couple_name: str) -> Path:
    wav_files = sorted(recordings_dir.glob("message_*.wav"))
    if not wav_files:
        print("ERREUR : aucun enregistrement trouvé dans", recordings_dir)
        sys.exit(1)

    safe_name = couple_name.replace(" ", "_").replace("&", "et").replace("/", "-")
    zip_path = _BASE_DIR / f"livraison_{safe_name}.zip"

    print(f"Création du ZIP ({len(wav_files)} message(s))…")
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for idx, wav in enumerate(wav_files, start=1):
            # Rename for readability: 01_message.wav, 02_message.wav…
            ts = wav.stem.replace("message_", "")
            arcname = f"{idx:02d}_{ts}.wav"
            zf.write(wav, arcname)
        # Include a text index
        index_lines = [f"{i:02d}. {f.stem.replace('message_', '')}" for i, f in enumerate(wav_files, 1)]
        zf.writestr("index.txt", "\n".join(index_lines))

    size_mb = zip_path.stat().st_size / (1024 * 1024)
    print(f"ZIP créé : {zip_path.name} ({size_mb:.1f} Mo)")
    return zip_path


def upload_wetransfer(zip_path: Path, couple_name: str, api_key: str) -> str:
    try:
        import requests
    except ImportError:
        print("ERREUR : installe requests avec : pip install requests")
        sys.exit(1)

    base_url = "https://wetransfer.com/api/v2"
    headers = {
        "Content-Type": "application/json",
        "x-api-key": api_key,
    }

    # Step 1: Authorize
    r = requests.post(f"{base_url}/authorize", headers=headers, timeout=30)
    r.raise_for_status()
    token = r.json()["token"]
    headers["Authorization"] = f"Bearer {token}"

    # Step 2: Create transfer
    payload = {
        "message": f"Livre d'or audio — {couple_name}",
        "files": [{"name": zip_path.name, "size": zip_path.stat().st_size}],
    }
    r = requests.post(f"{base_url}/transfers", json=payload, headers=headers, timeout=30)
    r.raise_for_status()
    transfer = r.json()
    transfer_id = transfer["id"]
    file_id = transfer["files"][0]["id"]
    multipart_upload = transfer["files"][0]["multipart"]["upload_url"]

    # Step 3: Upload file (single-part for files < 6 GB)
    print("Upload en cours…")
    with open(zip_path, "rb") as f:
        data = f.read()
    r = requests.put(multipart_upload, data=data, timeout=300)
    r.raise_for_status()

    # Step 4: Mark upload complete
    r = requests.put(
        f"{base_url}/transfers/{transfer_id}/files/{file_id}/upload-complete",
        headers=headers, timeout=30,
    )
    r.raise_for_status()

    # Step 5: Finalize transfer
    r = requests.put(f"{base_url}/transfers/{transfer_id}/finalize", headers=headers, timeout=30)
    r.raise_for_status()

    # Poll until URL is ready (max 60s)
    for _ in range(12):
        r = requests.get(f"{base_url}/transfers/{transfer_id}", headers=headers, timeout=30)
        r.raise_for_status()
        info = r.json()
        if info.get("url"):
            return info["url"]
        time.sleep(5)

    raise RuntimeError("WeTransfer : URL non disponible après 60s")


def main() -> None:
    parser = argparse.ArgumentParser(description="Récupère les messages et les envoie au client")
    parser.add_argument("--dir", default=None, help="Répertoire d'enregistrements explicite")
    parser.add_argument("--local", action="store_true", help="Utiliser recordings/ local")
    parser.add_argument("--no-upload", action="store_true", help="Ne pas uploader, créer le ZIP seulement")
    parser.add_argument("--api-key", default=None, help="Clé API WeTransfer (ou env WETRANSFER_API_KEY)")
    args = parser.parse_args()

    # Locate recordings
    if args.dir:
        recordings_dir = Path(args.dir)
    elif args.local:
        recordings_dir = _BASE_DIR / "recordings"
    else:
        recordings_dir = find_usb_recordings()
        if not recordings_dir:
            print("Aucune clé USB détectée, utilisation du dossier local recordings/")
            recordings_dir = _BASE_DIR / "recordings"

    if not recordings_dir.exists():
        print(f"ERREUR : dossier introuvable : {recordings_dir}")
        sys.exit(1)

    couple_name = load_event_name() or "evenement"
    zip_path = build_zip(recordings_dir, couple_name)

    if args.no_upload:
        print(f"\nZIP prêt (upload désactivé) : {zip_path}")
        return

    api_key = args.api_key or os.environ.get("WETRANSFER_API_KEY")
    if not api_key:
        print("\nPas de clé API WeTransfer. Définir WETRANSFER_API_KEY ou passer --api-key.")
        print(f"ZIP disponible localement : {zip_path}")
        return

    try:
        url = upload_wetransfer(zip_path, couple_name, api_key)
        print(f"\n✓ Lien de téléchargement pour {couple_name} :")
        print(f"  {url}")
        print("\nEnvoie ce lien au couple par email ou SMS.")
    except Exception as exc:
        print(f"ERREUR upload WeTransfer : {exc}")
        print(f"ZIP disponible localement : {zip_path}")
        sys.exit(1)


if __name__ == "__main__":
    main()
