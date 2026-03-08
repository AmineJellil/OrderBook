---
output:
  pdf_document: default
  html_document: default
---
# Avancement Intégration Repo2 -> Repo1 (tradinggame-py)

## 1) Objectif
Intégrer les fonctionnalités clés du repo2 (limit order book + logique NPC) dans le repo1 (`tradinggame-py`) sans casser les endpoints/GUI existants.

## 2) Ce qui est fait

### A. Intégration du moteur Order Book dans repo1
- Ajout d'un carnet d'ordres (`bids` / `asks`) avec tri des prix.
- Exécution des ordres market contre le carnet (matching + prix moyen d'exécution).
- Snapshot du carnet (best bid / best ask / profondeur).

Fichiers:
- `app/lib/exchange/OrderBook.py`
- `app/lib/exchange/Exchange.py`

### B. Endpoint API Order Book
- Ajout de `GET /orderbook/<product>?levels=N`.
- Retourne `bids`, `asks`, `best_bid`, `best_ask`, `current_price`.

Fichiers:
- `app/lib/api/OrderBookEndpoint.py`
- `app/sbin/api-server.py`

### C. Affichage GUI en temps réel
- Ajout d'un panneau "Order Book" dans Dash.
- Rafraîchissement périodique.
- Affichage: niveaux bid/ask + best bid/best ask + spread.

Fichiers:
- `app/cbin/gui/Client.py`
- `app/cbin/gui/Window.py`
- `app/cbin/gui/assets/style.css`

### D. Portage inspiré du repo2 pour la liquidité NPC
- Remplacement de la logique NPC simpliste par un modèle inspiré du repo2:
  - courbe de liquidité bimodale,
  - annulation des ordres NPC invalides,
  - remplissage de la liquidité manquante niveau par niveau.

Fichiers:
- `app/lib/exchange/LiquidityCurve.py`
- `app/lib/exchange/NPCManager.py`
- `app/lib/exchange/Exchange.py`
- `app/lib/exchange/OrderBook.py`

### E. Correctif de cohérence book
- Correction du problème de carnet croisé (spread négatif observé en GUI).
- Vérification: `best_bid <= best_ask` sur les snapshots testés.

## 3) Ce qui reste à faire

1. Support complet des limit orders équipes (pas uniquement market).
2. Exposer la provenance des niveaux (`NPC` vs équipe) dans le snapshot/GUI.
3. Ajouter des tests unitaires/API (matching, cohérence spread, partial fills).
4. Ajuster/calibrer les paramètres de courbe NPC avec les auteurs des repos.

## 4) Impact fonctionnel actuel
- Les trades passent maintenant par le carnet et non plus par un prix "infini".
- Le prix d'exécution dépend de la profondeur (impact marché simulé).
- La GUI montre un carnet vivant, cohérent, et mis à jour en continu.

## 5) Risques / points d'alignement à valider en réunion
- Niveau de fidélité attendu vs repo2 (strict parity ou adaptation pragmatique).
- Paramétrage NPC (profondeur, skew, bruit, total liquidity).
- Priorité produit: limit orders complets vs stabilisation/tests.

---

## Message court à envoyer au binôme

J'ai intégré la base order book de repo2 dans `tradinggame-py`: moteur book + matching market, endpoint `/orderbook`, affichage live dans la GUI, et logique NPC inspirée repo2 (courbe bimodale + cancel/fill).  
Le spread négatif est corrigé (book cohérent).  
Il reste surtout à faire le support complet des limit orders équipes + tests API/unitaires.  
Si tu veux, tu peux prendre le lot "limit orders + endpoint" pendant que je prends "tests + calibrage NPC".
