# Liste du matériel

## Composants principaux

| Composant | Modèle recommandé | Prix indicatif | Où trouver |
|---|---|---|---|
| Raspberry Pi | Pi Zero 2 W ou Pi 4 (voir ci-dessous) | 15–40 € | raspberrypi.com, Amazon, Kubii |
| Carte microSD | Classe A1, 8 Go minimum | 5–10 € | Amazon, Fnac |
| Alimentation | Officielle Raspberry Pi (5 V) | 8–12 € | Kubii, Amazon |
| Combiné téléphonique | Socotel S63 | 5–20 € | Leboncoin, Vinted, brocantes |
| Dongle audio USB | Tout dongle USB Audio Class (UAC) | 5–10 € | Amazon (ex : UGREEN, Sabrent, générique) |
| Clé USB | 8 Go minimum | 5 € | Partout |

## Composants optionnels

| Composant | Utilité | Prix | Où trouver |
|---|---|---|---|
| Écran OLED SSD1306 128×64 I2C | Affichage du statut et du compteur de messages | 3–5 € | AliExpress, Amazon |
| Hub USB OTG (Pi Zero 2 W uniquement) | Permet de brancher dongle + clé USB simultanément | 5–10 € | Amazon (ex : Waveshare USB HUB HAT) |
| Boîtier imprimé 3D | Montage propre | — | À imprimer, fichiers à venir |

---

## Choisir son Raspberry Pi

### Pi 4 — configuration simple (recommandée pour débuter)

Le Pi 4 dispose de **4 ports USB-A natifs** : pas besoin de hub.
Brancher directement le dongle audio et la clé USB.

```
  Pi 4
  ┌──────────────────┐
  │ [USB-A] ← Dongle audio
  │ [USB-A] ← Clé USB
  │ [USB-A]   (libre)
  │ [USB-A]   (libre)
  │ [USB-C] ← Alimentation
  └──────────────────┘
```

Inconvénient : plus grand (85 × 56 mm), plus difficile à loger dans un boîtier de téléphone.

---

### Pi Zero 2 W — configuration compacte (recommandée pour l'intégration)

Le Pi Zero 2 W n'a qu'**un seul port micro-USB OTG**. Il faut un hub USB OTG pour brancher à la fois le dongle audio et la clé USB.

```
  Pi Zero 2 W
  ┌───────────────────┐
  │ [µUSB Power] ← Alimentation
  │ [µUSB OTG]  ← Hub USB OTG
  │                   │
  └───────────────────┘
                  Hub USB OTG
                  ┌──────────────┐
                  │ [USB-A] ← Dongle audio
                  │ [USB-A] ← Clé USB
                  └──────────────┘
```

> **Hub recommandé** : Waveshare USB HUB HAT, ou tout hub micro-USB OTG avec alimentation externe (~5–10 €).  
> Certains hubs OTG se branchent directement sur les pins GPIO pour l'alimentation, évitant un câble USB-C séparé.

Avantage : très compact (65 × 30 mm), s'intègre facilement dans un combiné ou un boîtier.

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
