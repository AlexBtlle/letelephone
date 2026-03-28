import time
from pathlib import Path

from audio import AudioController
from hook import HookSwitch
from storage import build_recording_path, ensure_recordings_dir


BASE_DIR = Path(__file__).resolve().parent.parent
ASSETS_DIR = BASE_DIR / "assets"
BEEP_FILE = ASSETS_DIR / "beep.wav"

HOOK_GPIO = 17
POLL_INTERVAL = 0.05

RECORDINGS_DIR = ensure_recordings_dir(BASE_DIR)


def main() -> None:
    hook = HookSwitch(gpio_pin=HOOK_GPIO, pull_up=True, bounce_time=0.05)
    audio = AudioController(
        playback_device="hw:2,0",
        capture_device="hw:3,0",
        sample_rate=48000,
        channels=1,
        max_duration_sec=180,
    )

    print("Système prêt. En attente du décrochage...")

    try:
        while True:
            if hook.is_off_hook():
                print("Décroché détecté.")

                try:
                    audio.play_beep(BEEP_FILE)
                except Exception as exc:
                    print(f"Erreur lecture bip : {exc}")
                    time.sleep(1)
                    continue

                output_file = build_recording_path(RECORDINGS_DIR)

                try:
                    audio.start_recording(output_file)
                    print(f"Enregistrement démarré : {output_file.name}")
                except Exception as exc:
                    print(f"Erreur démarrage enregistrement : {exc}")
                    time.sleep(1)
                    continue

                while hook.is_off_hook() and audio.is_recording():
                    time.sleep(POLL_INTERVAL)

                audio.stop_recording()
                print("Enregistrement arrêté.")

                while hook.is_off_hook():
                    time.sleep(POLL_INTERVAL)

                print("Retour en attente.")

            time.sleep(POLL_INTERVAL)

    except KeyboardInterrupt:
        print("\nArrêt demandé.")
    finally:
        audio.stop_recording()
        hook.close()


if __name__ == "__main__":
    main()