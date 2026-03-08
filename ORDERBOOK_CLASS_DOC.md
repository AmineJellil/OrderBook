# Documentation `OrderBook` (repo `tradinggame-py`)

## Fichier source
- [OrderBook.py](/home/jellilm/Desktop/MStanley/tradinggame-py/app/lib/exchange/OrderBook.py)

## Vue d'ensemble
La classe `OrderBook` gère un carnet d'ordres en mémoire pour un symbole (ex: `EURGBP`), avec:
- stockage des ordres `bid` (achat) et `ask` (vente),
- insertion triée par prix,
- annulation/filtrage,
- extraction de snapshot pour l'API/GUI,
- exécution des ordres market contre la liquidité disponible.

Le carnet est protégé par un verrou (`Lock`) pour éviter les incohérences en accès concurrent.

---

## Modèle de données

### `BookOrder` (`@dataclass`)
Représente un ordre dans le carnet.

Champs:
- `order_id: int` identifiant unique de l'ordre.
- `trader_id: str` identifiant du propriétaire de l'ordre (`NPC` pour la liquidité bot).
- `side: Side` côté de l'ordre (`Side.BUY` ou `Side.SELL`).
- `quantity: int` quantité restante.
- `price: float` prix limite.

---

## Classe `OrderBook`

### `__init__(self, symbol: str)`
Initialise le carnet.

État créé:
- `self.symbol` symbole du produit.
- `self._bids` liste des ordres achat.
- `self._asks` liste des ordres vente.
- `self._next_order_id` compteur d'ID (démarre à `1`).
- `self._lock` verrou de synchronisation.

---

### `_new_order_id(self) -> int`
Génère un nouvel `order_id` auto-incrémenté.

Logique:
1. lit `self._next_order_id`,
2. incrémente le compteur,
3. retourne la valeur initiale.

---

### `_insert_order(self, order: BookOrder) -> None`
Insère un ordre dans le bon côté du carnet, puis trie.

Règles de tri:
- `BUY`: tri décroissant par prix (`best bid` en tête).
- `SELL`: tri croissant par prix (`best ask` en tête).

---

### `_purge_npc_orders(self) -> None`
Supprime du carnet tous les ordres `trader_id == "NPC"` des deux côtés.

Usage:
- utilitaire pour reconstruire une liquidité bot propre.

---

### `add_limit_order(self, trader_id: str, side: Side, quantity: int, price: float) -> BookOrder`
Ajoute un ordre limite dans le carnet.

Entrées:
- `trader_id` propriétaire de l'ordre.
- `side` côté achat/vente.
- `quantity` quantité (cast en `int`).
- `price` prix limite (cast en `float`).

Traitement:
1. prend le verrou,
2. crée un `BookOrder` avec nouvel ID,
3. insère via `_insert_order`.

Sortie:
- l'objet `BookOrder` créé.

---

### `get_orders(self, trader_id=None, side=None) -> list[BookOrder]`
Retourne une vue filtrée des ordres du carnet.

Filtres optionnels:
- `trader_id`: conserve uniquement les ordres de ce propriétaire.
- `side`: conserve uniquement `BUY` ou `SELL`.

Sortie:
- liste (copie) d'ordres correspondant aux filtres.

---

### `cancel_order(self, order_id) -> bool`
Annule un ordre par son identifiant.

Traitement:
1. parcourt `bids` puis `asks`,
2. supprime l'ordre si trouvé.

Sortie:
- `True` si suppression effectuée,
- `False` si ID introuvable.

---

### `cancel_orders_at_price(self, price: float, side: Side, trader_id=None) -> None`
Supprime les ordres d'un côté donné à un prix donné.

Comportement:
- travaille sur `bids` si `side=BUY`, sinon sur `asks`,
- si `trader_id` est fourni, supprime seulement les ordres de ce trader,
- sinon supprime tous les ordres à ce prix sur ce côté.

---

### `quantity_at_price(self, price: float, side: Side, trader_id=None) -> int`
Calcule la quantité totale à un niveau de prix.

Comportement:
- côté choisi (`BUY` ou `SELL`),
- somme des quantités des ordres au prix exact,
- optionnellement filtré par `trader_id`.

Sortie:
- quantité totale (entier).

---

### `snapshot(self, levels=24) -> dict`
Construit un snapshot du carnet (pour API/GUI).

Entrée:
- `levels`: nombre maximal de niveaux retournés par côté.

Sortie (dict):
- `bids`: liste des `levels` premiers bids, format `(order_id, price, quantity)`.
- `asks`: liste des `levels` premiers asks, format `(order_id, price, quantity)`.
- `best_bid`: meilleur prix acheteur (ou `None` si vide).
- `best_ask`: meilleur prix vendeur (ou `None` si vide).

Notes:
- c'est une photo instantanée, pas un historique.

---

### `execute_market(self, side: Side, quantity: int) -> dict`
Exécute un ordre market contre la meilleure liquidité disponible.

Entrées:
- `side`: côté de l'ordre entrant.
  - `BUY` consomme les `asks`,
  - `SELL` consomme les `bids`.
- `quantity`: quantité demandée.

Logique:
1. sélectionne le côté opposé (`resting`),
2. consomme niveau par niveau en partiel/complet,
3. met à jour les quantités restantes,
4. supprime un niveau quand sa quantité atteint `0`,
5. calcule le prix moyen pondéré.

Sortie (dict):
- `filled_quantity`: quantité exécutée.
- `remaining_quantity`: quantité non exécutée.
- `average_price`: prix moyen d'exécution.
- `status`:
  - `FILLED` si tout exécuté,
  - `PARTIAL` si exécution partielle,
  - `FAILED` si rien exécuté.

---

## Invariants importants
- `bids` triés du plus haut au plus bas.
- `asks` triés du plus bas au plus haut.
- `best_bid` est toujours `bids[0].price` si `bids` non vide.
- `best_ask` est toujours `asks[0].price` si `asks` non vide.
- Toute mutation se fait sous verrou (`self._lock`).

---

## Intégration avec le reste du système
- `Exchange.try_trade(...)` appelle `execute_market(...)` pour exécuter les trades.
- `OrderBookEndpoint` appelle `Exchange.get_order_book_snapshot(...)`, qui utilise `snapshot(...)`.
- Le GUI consomme ce snapshot via `Client.get_order_book(...)`.
