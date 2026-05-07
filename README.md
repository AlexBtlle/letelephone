# Livre d'Or Audio

Un **système de livre d'or audio** sur Raspberry Pi pour les mariages et événements. Les invités décrochent un combiné téléphonique vintage, entendent le message d'accueil du couple, puis enregistrent leur message vocal. Les fichiers sont sauvegardés sur une clé USB.

---

## Fonctionnalités

- **Détection du combiné** : hook switch GPIO, décrochage/raccrochage détectés automatiquement
- **Message d'accueil personnalisé** : `welcome.wav` à la racine de la clé USB, bip par défaut si absent
- **Afficheur OLED** : nom du couple, statut (en attente / enregistrement), compteur de messages (SSD1306 I2C)
- **Filtre durée** : enregistrements de moins de 1 seconde ignorés automatiquement
- **Enregistrement automatique** : démarre après l'annonce, s'arrête au raccrochage
- **Durée maximale** : configurable (défaut 3 minutes)
- **Sauvegarde sur clé USB** : dossier `enregistrements/`, fallback local si clé absente
- **Son d'erreur** : bip si le système ne peut pas enregistrer
- **Démarrage autonome** : service systemd, redémarrage automatique en cas de crash

---

## Architecture

```
letelephone/
├── src/
│   ├── main.py          # Boucle principale
│   ├── config.py        # Chargement de la configuration
│   ├── audio.py         # Lecture / enregistrement (auto-détection ALSA)
│   ├── hook.py          # Détection hook switch (GPIO)
│   ├── storage.py       # Gestion des chemins d'enregistrement
│   ├── usb.py           # Détection et gestion de la clé USB
│   └── selftest.py      # Contrôles au démarrage
├── config/
│   └── config.default.json   # Paramètres (GPIO, durée…)
├── assets/
│   ├── beep.wav              # Son d'accueil par défaut
│   └── error.wav             # Son d'erreur
├── systemd/
│   └── letelephone.service   # Service systemd
├── tests/
├── install.sh
└── pyproject.toml
```

---

## Branchements

### Hook switch (combiné Socotel S63 ou similaire)
- **GPIO BCM 17** (pin physique 11) → une borne de l'interrupteur hook
- GND (pin physique 9) → l'autre borne

### Circuit audio (dongle USB)
- **Sortie casque** du dongle → fil **speaker** du combiné
- **Entrée micro** du dongle → fil **microphone** du combiné
- **Masse** du dongle → fil **masse** du combiné

### Alimentation
- Raspberry Pi Zero 2 W ou Pi 4, alimenté en 5 V via l'alimentation officielle

---

## Installation

### Pré-requis

- Raspberry Pi avec Raspberry Pi OS (Lite recommandé)
- Connexion internet au moment de l'installation
- Dongle audio USB branché

### Installation en une commande

```bash
git clone https://github.com/AlexBtlle/letelephone.git
cd letelephone
sudo bash install.sh
```

### Démarrer le service

```bash
sudo systemctl start letelephone
sudo systemctl status letelephone
```

### Consulter les logs

```bash
journalctl -u letelephone -f
```

---

## Utilisation

### Préparer un événement

Copier ces fichiers à la **racine** de la clé USB avant de la brancher au Pi :

| Fichier | Rôle | Obligatoire |
|---|---|---|
| `welcome.wav` | Message d'accueil du couple (WAV mono 44100 Hz) | Non — bip par défaut |
| `couple.txt` | Nom du couple, ex. `Alice & Bob` | Non — écran vide sinon |

Convertir un enregistrement vocal si besoin :
```bash
ffmpeg -i welcome.m4a -ar 44100 -ac 1 welcome.wav
```

Le téléphone détecte tout automatiquement au boot. Pour un nouvel événement, remplacer simplement les fichiers sur la clé.

### Pendant l'événement

1. Brancher la clé USB dans le Pi → les enregistrements s'y sauvegardent dans `enregistrements/`
2. Tester : décrocher → message d'accueil → enregistrer → raccrocher
3. Vérifier que le fichier apparaît sur la clé

### Après l'événement

Récupérer la clé USB, zipper le dossier `enregistrements/` et envoyer via WeTransfer ou autre.

### Configuration avancée

Pour modifier le GPIO, la durée max, etc., éditer `config/config.default.json` :

```json
{
  "hook_pin": 17,
  "pre_beep_delay_sec": 2.0,
  "max_duration_sec": 180,
  "audio": { "sample_rate": 44100, "channels": 1 }
}
```

---

## Licence

Licence **GNU GPL v3**. Voir `LICENSE` pour plus de détails.
