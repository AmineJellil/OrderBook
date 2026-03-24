# Manuel Utilisateur - Commandes API/GUI

Ce guide donne les commandes essentielles pour utiliser le projet:
- lancer API + GUI,
- créer des équipes,
- trader,
- consulter prix/carnet/positions,
- utiliser les endpoints admin.

> Hypothèse: tu es dans le repo `tradinggame-orderbook-integration-clean`.

---

## 1) Pré-requis

1. Environnement Python + dépendances:
```bash
cd /home/jellilm/Desktop/MStanley/tradinggame-orderbook-integration-clean/app
python3 -m venv ../.venv
source ../.venv/bin/activate
pip install -r requirements.txt
```

2. Secret admin par défaut:
- `Hackathon19` (utilisé par les endpoints admin/trader management).

---

## 2) Lancer l’API

## Option A (script direct, port 443)
```bash
cd /home/jellilm/Desktop/MStanley/tradinggame-orderbook-integration-clean/app
source ../.venv/bin/activate
PYTHONPATH=/home/jellilm/Desktop/MStanley/tradinggame-orderbook-integration-clean/app python sbin/api-server.py
```

## Option B (recommandé local, port 5000)
```bash
cd /home/jellilm/Desktop/MStanley/tradinggame-orderbook-integration-clean
source .venv/bin/activate
PYTHONPATH=/home/jellilm/Desktop/MStanley/tradinggame-orderbook-integration-clean/app python -c "import runpy; ns=runpy.run_path('app/sbin/api-server.py', run_name='api_server'); ns['run_app'](debug=False, host='127.0.0.1', port=5000)"
```

Vérifier:
```bash
curl -s http://127.0.0.1:5000/productList
```

---

## 3) Lancer la GUI

```bash
cd /home/jellilm/Desktop/MStanley/tradinggame-orderbook-integration-clean
source .venv/bin/activate
API_URL=http://127.0.0.1:5000 GUI_PORT=8050 PYTHONPATH=/home/jellilm/Desktop/MStanley/tradinggame-orderbook-integration-clean/app python app/cbin/gui/gui-client.py
```

Accès navigateur:
- `http://127.0.0.1:8050`

---

## 4) Commandes de base API (curl)

Base URL locale:
```bash
BASE=http://127.0.0.1:5000
```

## 4.1 Lister les produits
```bash
curl -s "$BASE/productList"
```

## 4.2 Récupérer prix spot courant
```bash
curl -s "$BASE/price/EURGBP"
```

## 4.3 Récupérer historique des prix
```bash
curl -s "$BASE/priceHistory/EURGBP"
```

## 4.4 Récupérer le carnet (order book)
```bash
curl -s "$BASE/orderbook/EURGBP?levels=10"
```

---

## 5) Gestion des équipes (traders)

## 5.1 Créer une équipe
```bash
curl -s -X POST "$BASE/trader" \
  -H "Content-Type: application/json" \
  -d '{"user_name":"equipe_1","secret":"Hackathon19"}'
```

Réponse type:
```json
{"trader_id":"..."}
```

## 5.2 Retrouver l’ID d’une équipe
```bash
curl -s -X POST "$BASE/traderQuery" \
  -H "Content-Type: application/json" \
  -d '{"user_name":"equipe_1","secret":"Hackathon19"}'
```

## 5.3 Supprimer une équipe
```bash
curl -s -X DELETE "$BASE/deleteTrader" \
  -H "Content-Type: application/json" \
  -d '{"user_name":"equipe_1","secret":"Hackathon19"}'
```

---

## 6) Passer des trades

## 6.1 Buy market
```bash
TRADER_ID="<METTRE_TRADER_ID_ICI>"
curl -s -X POST "$BASE/trade/EURGBP" \
  -H "Content-Type: application/json" \
  -d "{\"trader_id\":\"$TRADER_ID\",\"quantity\":10000,\"side\":\"buy\"}"
```

## 6.2 Sell market
```bash
TRADER_ID="<METTRE_TRADER_ID_ICI>"
curl -s -X POST "$BASE/trade/EURGBP" \
  -H "Content-Type: application/json" \
  -d "{\"trader_id\":\"$TRADER_ID\",\"quantity\":10000,\"side\":\"sell\"}"
```

Réponse type:
```json
{"success":true,"price":"0.87..."}
```

Notes:
- `price` retourné = prix d'exécution moyen (`average_price`).
- quantité invalide (`<=0` ou trop grande) => `success:false`.

---

## 7) Consulter positions, capitaux, historique

## 7.1 Positions d’un trader
```bash
TRADER_ID="<METTRE_TRADER_ID_ICI>"
curl -s "$BASE/positions/$TRADER_ID"
```

## 7.2 Capitaux de tous les traders
```bash
curl -s "$BASE/capitals"
```

## 7.3 Capitaux normalisés (leaderboard)
```bash
curl -s "$BASE/normalizedCapitals"
```

## 7.4 Historique des trades
```bash
curl -s "$BASE/tradeHistory"
```

---

## 8) Endpoints admin utiles

## 8.1 Activer/Désactiver trading
```bash
curl -s -X POST "$BASE/enableTrading" \
  -H "Content-Type: application/json" \
  -d '{"secret":"Hackathon19","trading_enabled":"True"}'
```

```bash
curl -s -X POST "$BASE/enableTrading" \
  -H "Content-Type: application/json" \
  -d '{"secret":"Hackathon19","trading_enabled":"False"}'
```

## 8.2 Forcer un prix (price impact)
```bash
curl -s -X POST "$BASE/priceSetter/EURGBP" \
  -H "Content-Type: application/json" \
  -d '{"secret":"Hackathon19","price":"0.95"}'
```

## 8.3 Reset des prix
```bash
curl -s -X POST "$BASE/priceReset" \
  -H "Content-Type: application/json" \
  -d '{"secret":"Hackathon19"}'
```

## 8.4 Reset traders + historique
```bash
curl -s -X POST "$BASE/resetAllTraders" \
  -H "Content-Type: application/json" \
  -d '{"secret":"Hackathon19"}'
```

---

## 9) Swagger / découverte endpoints

Si API sur port 5000:
- `http://127.0.0.1:5000/api/specs.html`

Si API sur port 443:
- `http://127.0.0.1:443/api/specs.html`

---

## 10) Mini scénario de test rapide

1. Créer 2 équipes (`equipe_1`, `equipe_2`).
2. Lire `/orderbook/EURGBP?levels=10`.
3. Envoyer un `buy` pour `equipe_1`.
4. Relire `/orderbook`.
5. Vérifier `/tradeHistory`, `/positions/<id>`, `/normalizedCapitals`.

---

## 11) Dépannage rapide

## API ne répond pas
- Vérifier que le process API tourne.
- Vérifier le port (`443` vs `5000`).

## GUI vide au lancement
- Vérifier `API_URL` (doit pointer vers l’API active).

## `success:false` sur `/trade`
- `trader_id` invalide,
- quantité invalide,
- trading désactivé,
- capital/inventaire insuffisant,
- aucune liquidité exécutable côté opposé.

