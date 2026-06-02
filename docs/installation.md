# Installation logicielle

Ce guide explique comment installer le logiciel sur ton Raspberry Pi, étape par étape. Il n'est nécessaire de le faire **qu'une seule fois**.

---

## Ce dont tu as besoin

- Le Raspberry Pi câblé selon le [guide de câblage](cablage.md)
- Une carte microSD (8 Go minimum, classe A1)
- Un ordinateur pour flasher la carte SD
- Une connexion internet (Wi-Fi ou câble Ethernet)

---

## Étape 1 — Flasher Raspberry Pi OS sur la carte SD

C'est l'étape où l'on installe le système d'exploitation sur la carte microSD.

1. Sur ton ordinateur, télécharger **Raspberry Pi Imager** → [raspberrypi.com/software](https://www.raspberrypi.com/software/)
2. Insérer la carte microSD dans ton ordinateur
3. Ouvrir Raspberry Pi Imager et choisir :
   - **Appareil** : ton modèle de Pi (Pi Zero 2 W, Pi 4, etc.)
   - **OS** : *Raspberry Pi OS Lite (64-bit)* — Bookworm ou plus récent. La version "Lite" n'a pas d'interface graphique, c'est normal, on n'en a pas besoin.
   - **Stockage** : ta carte microSD
4. Avant de flasher, cliquer sur **Modifier les réglages** (l'engrenage) et configurer :
   - **Nom d'hôte** : `letelephone`
   - **Nom d'utilisateur** : `pi` — Mot de passe : choisir un mot de passe
   - **Wi-Fi** : entrer le nom et le mot de passe de ton réseau
   - **Langue** : `fr_FR` — Clavier : `fr`
   - **Activer SSH** : oui, avec authentification par mot de passe
5. Cliquer sur **Écrire** et attendre la fin (environ 5 minutes)
6. Insérer la carte microSD dans le Pi et le brancher sur le secteur

---

## Étape 2 — Se connecter en SSH

Le Pi démarre sans écran ni clavier. On le contrôle à distance depuis un ordinateur sur le même réseau Wi-Fi.

**Sur Mac ou Linux**, ouvrir le Terminal et taper :
```bash
ssh pi@letelephone.local
```

**Sur Windows**, télécharger [PuTTY](https://www.putty.org/) ou utiliser le Terminal de Windows 10/11 :
```
ssh pi@letelephone.local
```

Entrer le mot de passe choisi à l'étape 1. Si tout va bien, tu vois une ligne de commande `pi@letelephone:~$`.

> Si `letelephone.local` ne fonctionne pas : se connecter à la box internet (souvent sur 192.168.1.1 ou 192.168.0.1) et regarder la liste des appareils connectés pour trouver l'adresse IP du Pi. Utiliser cette adresse à la place : `ssh pi@192.168.1.XX`.

---

## Étape 3 — Télécharger le projet

Dans le terminal SSH, taper :

```bash
git clone https://github.com/AlexBtlle/letelephone.git
cd letelephone
```

---

## Étape 4 — Lancer l'installation

```bash
sudo bash install.sh
```

Le script fait tout automatiquement :
- Installe les logiciels nécessaires (`ffmpeg`, `alsa-utils`, etc.)
- Installe le programme en Python
- Crée les dossiers de données
- Installe le service qui démarre automatiquement au démarrage du Pi
- **Sur Pi Zero 2 W** : détecte la carte, configure le pilote audio Codec Zero, et demande un redémarrage si nécessaire

L'installation prend environ 3–5 minutes.

---

## Étape 5 — Redémarrer si nécessaire (Pi Zero 2 W uniquement)

Si tu utilises un **Pi Zero 2 W avec Codec Zero**, le script affiche à la fin un encadré jaune qui demande un redémarrage. C'est normal : le pilote audio doit être activé avant le premier démarrage du service.

```bash
sudo reboot
```

Attendre ~30 secondes, puis se reconnecter en SSH.

---

## Étape 6 — Activer I2C (si tu utilises l'écran OLED)

Si tu n'as pas d'écran OLED, passer directement à l'étape suivante.

```bash
sudo raspi-config
```

Dans le menu qui s'affiche :
- Aller dans **Interface Options**
- Puis **I2C**
- Sélectionner **Enable**
- Choisir **Finish**
- Redémarrer quand demandé

Vérifier que l'écran est bien détecté :
```bash
sudo apt install i2c-tools
i2cdetect -y 1
```
Une grille s'affiche. L'adresse `3c` doit apparaître dedans.

---

## Étape 7 — Vérifier l'audio

Lister les périphériques audio détectés :

```bash
aplay -l     # périphériques de lecture (écouteur)
arecord -l   # périphériques d'enregistrement (micro)
```

**Configuration standard (dongle USB) :** le dongle doit apparaître avec la mention `USB Audio` dans les deux listes.

**Configuration compacte (Codec Zero) :** la carte doit apparaître avec la mention `IQaudIO` ou `DA7212` dans les deux listes.

Tester la lecture d'un son (remplacer `hw:1,0` par les numéros affichés dans `aplay -l`) :
```bash
aplay -D hw:1,0 assets/beep.wav
```

Tester l'enregistrement (5 secondes) :
```bash
arecord -D hw:1,0 -f S16_LE -r 44100 -c 1 -d 5 test.wav && aplay -D hw:1,0 test.wav
```

> Si les numéros de carte sont différents, le logiciel les détecte automatiquement. Pas besoin de les configurer manuellement sauf cas particulier.

---

## Étape 8 — Démarrer le service

```bash
sudo systemctl start letelephone
sudo systemctl status letelephone
```

La dernière commande doit afficher `active (running)` en vert.

**Tester le fonctionnement :**
1. Brancher une clé USB
2. Décrocher le combiné → attendre 2 secondes → un bip doit se jouer
3. Parler quelques secondes
4. Raccrocher
5. Vérifier qu'un fichier `message_*.mp3` est apparu dans `enregistrements/` sur la clé USB

---

## Démarrage automatique

Le service démarre automatiquement à chaque allumage du Pi. Un auto-test est effectué au démarrage : s'il détecte un problème (carte audio absente, fichier beep.wav manquant, Codec Zero non configuré), le service ne démarre pas et joue un son d'erreur pour alerter.

Commandes utiles :

```bash
# Voir le statut du service
sudo systemctl status letelephone

# Suivre les logs en direct
journalctl -u letelephone -f

# Redémarrer le service
sudo systemctl restart letelephone

# Arrêter le service
sudo systemctl stop letelephone
```

---

## Configuration avancée

Le fichier `config/config.default.json` contient tous les réglages. On peut le modifier avec :

```bash
nano config/config.default.json
```

Puis redémarrer le service pour appliquer :
```bash
sudo systemctl restart letelephone
```

### Paramètres disponibles

| Paramètre | Rôle | Valeur par défaut |
|---|---|---|
| `hook_pin` | Numéro GPIO du hook switch | `17` |
| `pre_beep_delay_sec` | Délai (en secondes) entre le décrochage et le bip | `2.0` |
| `max_duration_sec` | Durée maximale d'un message | `180` (3 min) |
| `min_duration_sec` | Durée minimale pour sauvegarder un message | `1.0` |
| `couple_name` | Nom affiché sur l'écran si pas de clé USB | `""` |
| `normalize_audio` | Égalise le volume de tous les messages automatiquement | `true` |
| `compress_mp3.enabled` | Convertit les messages en MP3 (5× plus léger) | `true` |
| `compress_mp3.quality` | Qualité MP3 : 0 = meilleure, 9 = moindre | `0` |
| `shutdown_button.enabled` | Active le bouton d'arrêt GPIO | `false` |
| `shutdown_button.pin` | Numéro GPIO du bouton d'arrêt | `27` |
| `shutdown_button.hold_duration_sec` | Durée d'appui nécessaire pour éteindre (secondes) | `3.0` |

### Exemple : activer le bouton d'arrêt

```json
"shutdown_button": {
  "enabled": true,
  "pin": 27,
  "hold_duration_sec": 3.0
}
```

### Personnaliser pour un événement sans clé USB

Si tu veux forcer le nom du couple même sans clé USB :
```json
"couple_name": "Marie & Julien"
```

### Remplacer les réglages pour un événement spécifique

Pour ne pas modifier la config par défaut, créer un fichier `config/config.event.json` qui surcharge uniquement ce que tu veux changer. Par exemple :

```json
{
  "couple_name": "Marie & Julien",
  "pre_beep_delay_sec": 3.0
}
```

Ce fichier est prioritaire sur `config.default.json`, et il suffit de le supprimer pour revenir aux réglages de base.
