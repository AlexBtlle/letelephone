# Le Téléphone — Livre d'or audio pour mariages

Un vieux téléphone vintage branché à un Raspberry Pi. Les invités décrochent, entendent un mot du couple, et laissent leur message vocal. Les enregistrements sont sauvegardés automatiquement sur une clé USB.

---

## Comment ça marche

```
  L'invité décroche          Le message d'accueil       L'invité parle
  ───────────────            ──────────────────         ─────────────
       ↓                     du couple se joue              ↓
  L'écran passe en                    ↓              L'invité raccroche
  mode ENREGISTREMENT          C'est parti !                 ↓
                                                  Le fichier est sauvegardé
                                                  sur la clé USB
```

L'écran OLED (optionnel) affiche en permanence :

```
┌────────────────────────┐
│ Alice & Bob            │  ← nom du couple
│                        │
│ EN ATTENTE             │  ← statut en temps réel
│                        │
│ Messages : 7           │  ← nombre de messages enregistrés
└────────────────────────┘
```

---

## Deux configurations possibles

| | Configuration standard | Configuration compacte |
|---|---|---|
| **Carte** | Pi 3B+, Pi 4 ou Pi 5 | Pi Zero 2 WH |
| **Audio** | Dongle USB (~8€) | IQaudio Codec Zero HAT (~18€) |
| **Prix total** | ~80–100 € | ~60 € |
| **Encombrement** | Normal | Très petit |
| **Montage** | Simple | Simple (HAT emboîté) |

> Le Pi Zero 2 W avec Codec Zero est l'option la plus économique. Le script d'installation configure tout automatiquement.

Voir le [guide matériel complet](docs/materiel.md) pour la liste précise des composants et les liens d'achat.

---

## Documentation

| Guide | Pour qui | Contenu |
|---|---|---|
| [Matériel](docs/materiel.md) | Avant d'acheter | Listes de composants, prix, où acheter, conseils |
| [Câblage](docs/cablage.md) | Au moment de monter | Schémas fil à fil, photos de référence |
| [Installation](docs/installation.md) | Une seule fois | Mise en place du logiciel, étape par étape |
| [Utilisation](docs/utilisation.md) | Avant chaque événement | Préparer la clé USB, dépannage, récupérer les messages |

---

## Installation en 4 commandes

```bash
git clone https://github.com/AlexBtlle/letelephone.git
cd letelephone
sudo bash install.sh
sudo systemctl start letelephone
```

> Sur Pi Zero 2 W avec Codec Zero, le script détecte automatiquement la carte et configure le pilote audio. Un redémarrage est demandé si nécessaire.

---

## Fonctionnalités

- **Décrochage automatique** — détection du hook switch via GPIO, sans délai
- **Message d'accueil personnalisé** — fichier `welcome.wav` sur la clé USB (bip par défaut)
- **Normalisation audio** — tous les messages au même volume, sans intervention manuelle
- **Compression MP3** — les messages sont convertis en MP3 haute qualité, 5× plus légers que le WAV
- **Écran OLED** — affichage du statut et du compteur en temps réel (optionnel)
- **Bouton d'arrêt** — appui 3 secondes pour éteindre proprement le Pi (optionnel)
- **Sauvegarde USB automatique** — fallback local si la clé est absente
- **Auto-test au démarrage** — détecte les problèmes avant l'événement
- **Compatible Pi 3B+, Pi 4, Pi 5, Pi Zero 2 W** — un seul logiciel pour toutes les cartes

---

## Clé USB — workflow rapide

Deux fichiers à placer à la racine de la clé avant l'événement :

| Fichier | Rôle |
|---|---|
| `welcome.wav` | Message d'accueil enregistré par le couple |
| `couple.txt` | Nom affiché sur l'écran (`Alice & Bob`) |

Les messages sont sauvegardés automatiquement dans `enregistrements/` sur la clé, au format MP3.

---

## Licence

GNU GPL v3 — voir `LICENSE`.
