#!/usr/bin/env python3
"""Prepare a letelephone unit for an event.

Usage:
    python scripts/prepare_event.py "Alice & Bob" 2026-06-15 /path/to/welcome.m4a
    python scripts/prepare_event.py "Alice & Bob" 2026-06-15  # no custom audio, uses beep
"""

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path

_BASE_DIR = Path(__file__).resolve().parent.parent
_ASSETS_DIR = _BASE_DIR / "assets"
_CONFIG_DIR = _BASE_DIR / "config"


def convert_audio(source: Path, dest: Path) -> None:
    if not shutil.which("ffmpeg"):
        print("ERREUR : ffmpeg n'est pas installé. Installe-le avec : sudo apt install ffmpeg")
        sys.exit(1)
    print(f"Conversion audio : {source.name} → {dest.name}")
    subprocess.run(
        [
            "ffmpeg", "-y",
            "-i", str(source),
            "-ar", "44100",
            "-ac", "1",
            "-f", "wav",
            str(dest),
        ],
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )


def write_event_config(couple_name: str, date: str, welcome_filename: str) -> Path:
    config = {
        "event": {
            "couple_name": couple_name,
            "date": date,
            "welcome_audio": welcome_filename,
        }
    }
    path = _CONFIG_DIR / "config.event.json"
    _CONFIG_DIR.mkdir(exist_ok=True)
    path.write_text(json.dumps(config, ensure_ascii=False, indent=2))
    return path


def main() -> None:
    parser = argparse.ArgumentParser(description="Prépare un événement letelephone")
    parser.add_argument("couple_name", help='Nom du couple, ex: "Alice & Bob"')
    parser.add_argument("date", help="Date de l'événement, ex: 2026-06-15")
    parser.add_argument(
        "welcome_audio",
        nargs="?",
        default=None,
        help="Chemin vers le message d'accueil (mp3, m4a, wav…). Optionnel.",
    )
    args = parser.parse_args()

    welcome_filename = ""

    if args.welcome_audio:
        source = Path(args.welcome_audio)
        if not source.exists():
            print(f"ERREUR : fichier introuvable : {source}")
            sys.exit(1)
        safe_name = args.couple_name.lower().replace(" ", "_").replace("&", "et").replace("/", "-")
        dest = _ASSETS_DIR / f"welcome_{safe_name}.wav"
        convert_audio(source, dest)
        welcome_filename = dest.name
        print(f"Message d'accueil copié → {dest}")

    config_path = write_event_config(args.couple_name, args.date, welcome_filename)
    print(f"Config événement écrite → {config_path}")

    print()
    print("✓ Prêt. Lance 'sudo systemctl restart letelephone' pour appliquer.")


if __name__ == "__main__":
    main()
