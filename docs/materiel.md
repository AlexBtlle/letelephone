# Guide matériel

## Deux configurations au choix

---

### Configuration compacte — environ 60 €

Idéale pour réduire les coûts. Le Pi Zero 2 W est plus petit qu'une carte de crédit. L'IQaudio Codec Zero est un petit circuit imprimé qui se branche directement sur le Pi (pas de soudure, pas de dongle USB).

| Composant | Modèle | Prix | Où acheter |
|---|---|---|---|
| Raspberry Pi Zero 2 WH | Pi Zero 2 WH (avec les broches déjà soudées, prendre le **WH** pas le W) | ~15 € | kubii.fr, raspberrypi.com |
| IQaudio Codec Zero HAT | IQaudio Codec Zero | ~18 € | kubii.fr, raspberrypi.com |
| Carte microSD | 8 Go minimum, classe A1 | 5–8 € | Amazon, Fnac |
| Alimentation | Officielle Raspberry Pi Zero (5V, connecteur micro-USB) | 8 € | kubii.fr, Amazon |
| Combiné téléphonique | Socotel S63 (voir plus bas) | 5–20 € | Leboncoin, Vinted, brocantes |
| Clé USB | 8 Go minimum | 5 € | Partout |

> **Total estimé : 56–74 €**

Le Codec Zero se connecte directement sur les broches GPIO du Pi Zero 2 W. Il dispose d'une prise jack TRRS 3,5 mm (combiné micro + écouteur sur une seule fiche, comme les écouteurs de smartphone).

---

### Configuration standard — environ 80–100 €

Plus facile à trouver, plus de ports USB disponibles. Idéale si tu as déjà un Pi 3B+ ou Pi 4 sous la main.

| Composant | Modèle | Prix | Où acheter |
|---|---|---|---|
| Raspberry Pi | Pi 3B+, Pi 4 (2 ou 4 Go) ou Pi 5 | 20–80 € | kubii.fr, raspberrypi.com, Amazon |
| Carte microSD | 8 Go minimum, classe A1 | 5–8 € | Amazon, Fnac |
| Alimentation | Officielle Raspberry Pi (5 V) | 8–15 € | kubii.fr, Amazon |
| Dongle audio USB | Tout dongle USB Audio Class (UAC) | 5–10 € | Amazon (ex : UGREEN, Sabrent, Logilink) |
| Combiné téléphonique | Socotel S63 (voir plus bas) | 5–20 € | Leboncoin, Vinted, brocantes |
| Clé USB | 8 Go minimum | 5 € | Partout |

> **Total estimé : 48–118 €** (selon le Pi choisi)

---

### Composants optionnels (toutes configurations)

| Composant | Utilité | Prix | Où acheter |
|---|---|---|---|
| Écran OLED SSD1306 128×64 I2C | Affiche le statut et le compteur de messages | 3–5 € | AliExpress, Amazon |
| Bouton poussoir momentané | Arrêt propre du Pi en fin de soirée (appui 3 secondes) | 1–2 € | AliExpress, Conrad |
| Boîtier imprimé en 3D | Montage soigné dans le boîtier du S63 | — | À imprimer |

---

## Le combiné Socotel S63

Le Socotel S63 est le téléphone à cadran classique que l'on trouve partout en France. Il est robuste, esthétique, et son hook switch est très facile d'accès.

**Où en trouver :**
- Leboncoin, Vinted, Facebook Marketplace : 5–15 €
- Vide-greniers et brocantes : souvent 2–5 €
- Sites de déco rétro : 20–40 € (inutile de payer plus)

**Ce qu'il faut vérifier avant d'acheter :**
1. Le bouton-poussoir sous l'emplacement du combiné doit s'enfoncer et revenir librement (c'est le hook switch — si ce bouton coince, le téléphone ne fonctionnera pas)
2. Le câble spiralé du combiné doit être intact (pas de fils coupés ni arrachés)
3. L'écouteur et le microphone fonctionnent (pas indispensable à vérifier à l'achat — on peut les remplacer)

**Attention au microphone à charbon :**
Le microphone d'origine du S63 est un microphone à charbon, une technologie ancienne qui nécessite une légère alimentation électrique pour fonctionner. Certains dongles USB et le Codec Zero ne fournissent pas cette alimentation.

Si le son enregistré est faible ou inaudible, la solution est de remplacer l'insert microphone par un **insert à électret compatible** (environ 2–5 €, disponible sur AliExpress en cherchant "telephone electret insert"). Le remplacement prend 5 minutes : dévisser l'embout du combiné, sortir l'ancien insert, mettre le nouveau, refermer.

---

## Choisir son Raspberry Pi (configuration standard)

Tous les Pi 3B+, 4 et 5 utilisent le même câblage et le même logiciel. La différence est surtout le prix et la disponibilité.

| Modèle | Ports USB | Prix indicatif | Notes |
|---|---|---|---|
| Pi 3B+ | 4 × USB-A 2.0 | ~20 € | Bon choix si tu en as déjà un |
| Pi 4 (2 Go) | 2 × USB 2.0 + 2 × USB 3.0 | ~35–45 € | Recommandé, bien disponible |
| Pi 5 | 2 × USB 2.0 + 2 × USB 3.0 | ~60–80 € | Le plus puissant, pas nécessaire ici |

> Le Pi Zero 2 W n'a qu'un port micro-USB OTG. Avec le Codec Zero, pas besoin de brancher de dongle audio USB — le port est libre pour d'autres usages.

---

## Outils nécessaires pour le montage

- **Fer à souder + soudure** — pour relier les fils du combiné au câble audio
- **Multimètre** — indispensable pour identifier les fils (mode continuité : bip)
- **Tournevis cruciforme et plat** — pour ouvrir le Socotel (3 vis sous la base)
- **Pince coupante et pince à dénuder**
- **Gaine thermorétractable** (ou ruban isolant) — pour isoler les connexions

> Si tu n'as jamais soudé, une connexion avec des dominos de raccordement (Wago) fonctionne très bien pour les fils du combiné.
