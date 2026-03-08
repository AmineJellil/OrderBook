# Documentation `NPCManager` (tradinggame-py)

## Fichier source
- [NPCManager.py](/home/jellilm/Desktop/MStanley/tradinggame-py/app/lib/exchange/NPCManager.py)

## Objectif
`NPCManager` gère la liquidité artificielle (ordres bot `NPC`) dans le carnet pour le garder vivant et cohérent autour du prix courant.

Concrètement, à chaque update:
1. construit une courbe cible de liquidité autour du mid-price,
2. supprime les ordres NPC devenus invalides,
3. remplit les niveaux de prix manquants.

---

## Origine (repo2 vs adaptation locale)

### Inspiré du repo2 (`tradingGame-main`)
Le design est inspiré de:
- [NPCManager.py](/home/jellilm/Desktop/MStanley/tradingGame-main./tradingGame-main/ExchangeStructure/LiquidityManagers/NPCManager.py)
- [LiquidityCurve.py](/home/jellilm/Desktop/MStanley/tradingGame-main./tradingGame-main/ExchangeStructure/LiquidityGenerator/LiquidityCurve.py)

Éléments repris conceptuellement:
- logique `cancel invalid orders`,
- logique `fill missing liquidity`,
- liquidité target issue d'une courbe autour du mid-price.

### Adapté à `tradinggame-py`
Ce n'est pas un copier-coller 1:1:
- API interne différente (on utilise `OrderBook` local),
- paramètres simplifiés/calibrés pour repo1,
- implémentation orientée intégration rapide sans casser l'existant.

---

## Classe `NPCManager`

### `__init__(self, order_book)`
Associe un manager NPC à un carnet précis.

Entrée:
- `order_book`: instance de `OrderBook`.

Rôle:
- toutes les actions NPC (annulation/remplissage) s'appliquent sur ce carnet.

---

### `_build_curve(self, mid_price) -> dict[float, int]`
Construit la courbe cible de liquidité.

Rôle:
- appeler `generate_bimodal_liquidity_curve(...)` avec les paramètres NPC.

Entrée:
- `mid_price`: prix central courant.

Sortie:
- dictionnaire `{price: target_quantity}`.

Paramètres utilisés:
- borne autour du mid (`pct_bounds=0.1`),
- `num_levels`, `total_liquidity`,
- forme de densité (`trough_depth`, `density_shape`, `liquidity_skew`),
- bruit (`noise_level`),
- précision (`decimal_places=5`).

---

### `_cancel_invalid_orders(self, curve, mid_price) -> None`
Supprime les ordres NPC qui ne correspondent plus à la cible.

Règles d'invalidation:
1. prix absent de la courbe cible,
2. ordre du mauvais côté du mid:
   - un bid NPC doit être `< mid_price`,
   - un ask NPC doit être `> mid_price`.

Effet:
- nettoie le book des niveaux NPC obsolètes avant refill.

---

### `_fill_missing_liquidity(self, curve, mid_price) -> None`
Aligne la quantité NPC au target pour chaque niveau de la courbe.

Pour chaque `price` de la courbe:
1. détermine le côté:
   - `BUY` si `price < mid_price`,
   - `SELL` sinon.
2. calcule la quantité NPC actuelle sur ce prix (`quantity_at_price(..., trader_id="NPC")`).
3. compare à la quantité cible:
   - si identique: ne fait rien,
   - sinon: annule les ordres NPC à ce prix, puis recrée un ordre NPC avec la quantité cible.

Effet:
- la profondeur NPC suit la courbe voulue niveau par niveau.

---

### `update(self, mid_price) -> None`
Méthode orchestratrice appelée par l'Exchange.

Pipeline:
1. `curve = _build_curve(mid_price)`
2. `_cancel_invalid_orders(curve, mid_price)`
3. `_fill_missing_liquidity(curve, mid_price)`

Effet global:
- carnet NPC remis en cohérence avec le prix courant.

---

## Où `NPCManager` est appelé
- [Exchange.py](/home/jellilm/Desktop/MStanley/tradinggame-py/app/lib/exchange/Exchange.py)

Dans le flux:
1. `get_order_book_snapshot(...)` appelle `npc_manager.update(current_price)` avant de retourner le snapshot API.
2. `try_trade(...)` appelle aussi `npc_manager.update(current_price)` juste avant `execute_market(...)`.

Donc:
- la liquidité NPC est rafraîchie pour l'affichage,
- et aussi juste avant les exécutions de trade.

---

## Impact fonctionnel
1. Book plus réaliste qu'un profil linéaire fixe.
2. Moins de niveaux obsolètes.
3. Exécution market dépend d'une profondeur cohérente.
4. Base technique propre pour ajouter les limit orders équipes ensuite.

---

## Limites actuelles
1. Paramètres de courbe encore calibrés “dev” (à valider avec les auteurs).
2. Pas encore de tracking visuel explicite NPC vs équipe dans la GUI.
3. Le moteur limit orders équipes n'est pas encore complet.

---

## Résumé réunion (30 secondes)
`NPCManager` dans `tradinggame-py` est une adaptation inspirée du repo2: on calcule une courbe cible autour du mid-price, on supprime les ordres NPC invalides, puis on remplit les niveaux manquants.  
Il est branché dans les snapshots et juste avant les trades, ce qui rend la profondeur du carnet plus stable et plus réaliste.
