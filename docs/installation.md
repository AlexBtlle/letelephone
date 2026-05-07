# Installation logicielle

## Pré-requis

- Un Raspberry Pi Zero 2 W ou Pi 4 câblé selon le [guide de câblage](cablage.md)
- Une carte microSD (8 Go minimum, classe A1 recommandée)
- Une connexion internet (câble Ethernet via adaptateur, ou Wi-Fi configuré)
- Un ordinateur pour flasher la carte SD

---

## Étape 1 — Flasher Raspberry Pi OS

1. Télécharger **Raspberry Pi Imager** sur [raspberrypi.com/software](https://www.raspberrypi.com/software/)
2. Choisir **Raspberry Pi OS Lite (64-bit)** — pas d'interface graphique nécessaire
3. Avant de flasher, cliquer sur l'icône engrenage et configurer :
   - **Nom d'hôte** : `letelephone`
   - **Activer SSH** : oui
   - **Wi-Fi** : SSID et mot de passe de ton réseau
   - **Langue / clavier** : fr\_FR / French
4. Flasher la carte SD, l'insérer dans le Pi et démarrer

---

## Étape 2 — Se connecter en SSH

Depuis ton ordinateur (même réseau Wi-Fi) :

```bash
ssh pi@letelephone.local
# Mot de passe par défaut : raspberry (changer après connexion)
```

> Si `letelephone.local` ne fonctionne pas, trouver l'adresse IP du Pi via ton routeur ou avec `nmap -sn 192.168.1.0/24`.

---

## Étape 3 — Cloner le projet

```bash
git clone https://github.com/AlexBtlle/letelephone.git
cd letelephone
```

---

## Étape 4 — Lancer l'installation

```bash
sudo bash install.sh
```

Le script fait automatiquement :
1. Mise à jour de la liste des paquets (`apt-get update`)
2. Installation des dépendances système (`python3`, `alsa-utils`, `ffmpeg`)
3. Installation du paquet Python et ses dépendances (`gpiozero`, `luma.oled`)
4. Création des dossiers `recordings/` et `logs/`
5. Installation et activation du service systemd

---

## Étape 5 — Activer I2C (si écran OLED)

Si tu utilises l'écran OLED SSD1306 :

```bash
sudo raspi-config
# Interface Options → I2C → Enable → Finish
sudo reboot
```

Vérifier que l'écran est détecté :

```bash
i2cdetect -y 1
# Doit afficher "3c" dans la grille
```

---

## Étape 6 — Vérifier l'audio

Lister les périphériques audio détectés :

```bash
aplay -l   # périphériques de lecture
arecord -l # périphériques d'enregistrement
```

Le dongle USB doit apparaître comme "USB Audio" dans les deux listes.

Tester la lecture (remplacer `hw:X,Y` par les numéros affichés) :

```bash
aplay -D hw:1,0 assets/beep.wav
```

Tester l'enregistrement (5 secondes) :

```bash
arecord -D hw:1,0 -f S16_LE -r 44100 -c 1 -d 5 test.wav
aplay -D hw:1,0 test.wav
```

> Si plusieurs dongles sont présents, le logiciel sélectionne automatiquement le premier dongle "USB Audio" détecté. En cas de problème, forcer le périphérique dans `config/config.default.json` (voir [Configuration avancée](#configuration-avancée)).

---

## Étape 7 — Démarrer le service

```bash
sudo systemctl start letelephone
sudo systemctl status letelephone
```

Le système lance automatiquement un auto-test au démarrage. En cas d'échec (fichier `beep.wav` absent, aucune carte audio), le service ne démarre pas et le son d'erreur est joué.

---

## Étape 8 — Tester le fonctionnement

1. Brancher une clé USB
2. Décrocher le combiné
3. Attendre 2 secondes → le bip doit se jouer
4. Parler quelques secondes
5. Raccrocher
6. Vérifier qu'un fichier `message_*.wav` est apparu sur la clé USB dans le dossier `enregistrements/`

---

## Démarrage automatique

Le service est activé au démarrage grâce à systemd :

```bash
# Statut
sudo systemctl status letelephone

# Logs en temps réel
journalctl -u letelephone -f

# Redémarrer
sudo systemctl restart letelephone

# Désactiver le démarrage automatique
sudo systemctl disable letelephone
```

---

## Configuration avancée

Éditer `config/config.default.json` pour modifier les paramètres :

```json
{
  "hook_pin": 17,
  "poll_interval_sec": 0.05,
  "pre_beep_delay_sec": 2.0,
  "max_duration_sec": 180,
  "min_duration_sec": 1.0,
  "couple_name": "",
  "audio": {
    "sample_rate": 44100,
    "channels": 1
  }
}
```

| Paramètre | Description | Défaut |
|---|---|---|
| `hook_pin` | Numéro GPIO BCM du hook switch | `17` |
| `pre_beep_delay_sec` | Délai avant le bip après décrochage | `2.0` |
| `max_duration_sec` | Durée maximale d'un message | `180` (3 min) |
| `min_duration_sec` | Durée minimale pour sauvegarder | `1.0` |
| `couple_name` | Nom affiché sur l'écran (si pas de clé USB) | `""` |

Pour utiliser un GPIO différent ou des périphériques ALSA spécifiques, créer `config/config.event.json` :

```json
{
  "hook_pin": 27,
  "audio": {
    "sample_rate": 48000
  }
}
```

Relancer le service après modification :

```bash
sudo systemctl restart letelephone
```
