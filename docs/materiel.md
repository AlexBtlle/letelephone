# Liste du matériel

## Composants principaux

| Composant | Modèle recommandé | Prix indicatif | Où trouver |
|---|---|---|---|
| Raspberry Pi | Pi 3B+, Pi 4 ou Pi 5 (voir ci-dessous) | 20–80 € | raspberrypi.com, Amazon, Kubii |
| Carte microSD | Classe A1, 8 Go minimum | 5–10 € | Amazon, Fnac |
| Alimentation | Officielle Raspberry Pi (5 V) | 8–15 € | Kubii, Amazon |
| Combiné téléphonique | Socotel S63 | 5–20 € | Leboncoin, Vinted, brocantes |
| Dongle audio USB | Tout dongle USB Audio Class (UAC) | 5–10 € | Amazon (ex : UGREEN, Sabrent, générique) |
| Clé USB | 8 Go minimum | 5 € | Partout |

## Composants optionnels

| Composant | Utilité | Prix | Où trouver |
|---|---|---|---|
| Écran OLED SSD1306 128×64 I2C | Affichage du statut et du compteur de messages | 3–5 € | AliExpress, Amazon |
| Boîtier imprimé 3D | Montage propre | — | À imprimer, fichiers à venir |

---

## Choisir son Raspberry Pi

Les Pi 3B+, 4 et 5 partagent tous le même connecteur GPIO 40 broches et disposent de **plusieurs ports USB-A natifs**, ce qui évite tout hub USB externe.

| Modèle | Ports USB-A | Dimensions | Prix indicatif | Notes |
|---|---|---|---|---|
| Pi 3B+ | 4 × USB-A 2.0 | 85 × 56 mm | ~20 € | Suffisant, plus difficile à trouver neuf |
| Pi 4 | 2 × USB-A 2.0 + 2 × USB-A 3.0 | 85 × 56 mm | 35–55 € | Recommandé, largement disponible |
| Pi 5 | 2 × USB-A 2.0 + 2 × USB-A 3.0 | 85 × 56 mm | 60–80 € | Plus puissant, GPIO via nouveau contrôleur RP1 |

```
  Pi 3B+ / Pi 4 / Pi 5
  ┌──────────────────┐
  │ [USB-A] ← Dongle audio
  │ [USB-A] ← Clé USB
  │ [USB-A]   (libre)
  │ [USB-A]   (libre)
  │ [USB-C] ← Alimentation (Pi 4/5) ou µUSB (Pi 3B+)
  └──────────────────┘
```

> **Pi 5 :** Le contrôleur GPIO RP1 nécessite le backend `lgpio` pour la bibliothèque gpiozero. Le script `install.sh` installe automatiquement `python3-lgpio` et le logiciel détecte le Pi 5 au démarrage pour configurer le bon backend.

---

## Le combiné Socotel S63

Le Socotel S63 est le téléphone à cadran le plus courant en France, facilement trouvable en brocante ou sur Leboncoin pour quelques euros.

**Pourquoi le S63 ?**
- Hook switch accessible et bien documenté
- Câble de combiné standardisé (4 fils)
- Boîtier en bakélite solide et esthétique

**Ce qu'il faut vérifier à l'achat :**
- Le hook switch fonctionne (le bouton-poussoir sous le combiné doit s'enfoncer et revenir)
- Les fils du combiné sont intacts (4 fils dans le câble spiralé)

> Le microphone d'origine du S63 est un microphone à charbon. Certains dongles audio USB ne délivrent pas la tension de polarisation nécessaire. Si le son capté est faible ou inexistant, remplacer l'insert microphone par un **insert à électret compatible** (environ 2–5 €, disponible sur AliExpress).

---

## Outils nécessaires

- Fer à souder + soudure (pour les connexions du combiné)
- Multimètre (pour identifier les fils et tester les connexions)
- Tournevis cruciforme et plat (pour ouvrir le Socotel)
- Pince coupante et pince à dénuder
- Gaine thermorétractable ou ruban isolant
