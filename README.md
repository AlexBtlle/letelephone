# Livre d'Or Audio

Un système de livre d'or audio sur Raspberry Pi pour les mariages et événements.  
Les invités décrochent un combiné téléphonique vintage, entendent le message d'accueil du couple, et enregistrent leur message vocal. Les fichiers sont sauvegardés sur une clé USB.

---

## Démonstration

```
┌────────────────────────┐
│ Alice & Bob            │  ← nom du couple (couple.txt sur la clé)
│                        │
│ EN ATTENTE             │  ← statut en temps réel
│                        │
│ Messages : 7           │  ← compteur automatique
└────────────────────────┘
```

1. L'invité décroche le combiné
2. Le message d'accueil du couple se joue (ou un bip)
3. L'invité enregistre son message et raccroche
4. Le fichier WAV est sauvegardé sur la clé USB

---

## Documentation

| Guide | Description |
|---|---|
| [Matériel](docs/materiel.md) | Liste des composants, prix, où acheter |
| [Câblage](docs/cablage.md) | Schémas de câblage complets (hook switch, audio, OLED) |
| [Installation](docs/installation.md) | Mise en place du logiciel pas à pas |
| [Utilisation](docs/utilisation.md) | Préparer un événement, gérer les enregistrements |

---

## Installation rapide

```bash
git clone https://github.com/AlexBtlle/letelephone.git
cd letelephone
sudo bash install.sh
sudo systemctl start letelephone
```

---

## Matériel requis

- Raspberry Pi 3B+, Pi 4 ou Pi 5
- Combiné téléphonique vintage avec hook switch (ex : Socotel S63)
- Dongle audio USB (tout modèle USB Audio Class)
- Clé USB pour stocker les enregistrements
- Écran OLED SSD1306 I2C 128×64 (optionnel)

Voir le [guide matériel complet](docs/materiel.md) pour les références et les prix.

---

## Architecture du projet

```
letelephone/
├── src/
│   ├── main.py          # Boucle principale
│   ├── config.py        # Chargement de la configuration
│   ├── audio.py         # Lecture / enregistrement (auto-détection ALSA)
│   ├── hook.py          # Détection hook switch (GPIO)
│   ├── display.py       # Afficheur OLED SSD1306 (optionnel)
│   ├── storage.py       # Gestion des chemins d'enregistrement
│   ├── usb.py           # Détection et gestion de la clé USB
│   └── selftest.py      # Contrôles au démarrage
├── config/
│   └── config.default.json   # Paramètres (GPIO, durée…)
├── assets/
│   ├── beep.wav              # Son d'accueil par défaut
│   └── error.wav             # Son d'erreur
├── docs/                     # Documentation complète
├── systemd/
│   └── letelephone.service
├── tests/                    # 94 tests pytest
├── install.sh
└── pyproject.toml
```

---

## Workflow clé USB

Deux fichiers optionnels à placer à la racine de la clé USB :

| Fichier | Rôle |
|---|---|
| `welcome.wav` | Message d'accueil du couple (WAV mono 44 100 Hz) |
| `couple.txt` | Nom du couple affiché sur l'écran |

Les enregistrements sont sauvegardés automatiquement dans `enregistrements/` sur la clé.

---

## Licence

Licence **GNU GPL v3**. Voir `LICENSE` pour plus de détails.
