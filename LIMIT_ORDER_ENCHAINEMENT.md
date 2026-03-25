---
output:
  html_document: default
  pdf_document: default
---
# Enchainement Limit Orders (EURGBP)

## Vue rapide
1. Une equipe envoie un ordre (`POST /trade/EURGBP`) avec `price` => ordre **LIMIT**.
2. `Exchange.try_trade(...)` met a jour la liquidite NPC puis tente le matching.
3. Si le prix limite croise deja le carnet, l'ordre est execute (total/partiel).
4. Sinon, le reliquat est place en **resting order** dans l'order book.
5. Quand une autre equipe envoie un **market order**, elle consomme les meilleures offres.
6. Les deux cotes du trade sont comptabilises (agresseur + contrepartie passive).
7. Le GUI lit `/orderbook` et `/tradeHistory` pour afficher carnet + historique.

## Sequence textuelle (sans diagramme)
1. **Team A** envoie un `sell limit` via `POST /trade/EURGBP` avec `price`.
2. `TradeEndpoint` appelle `Exchange.try_trade(...)`.
3. `Exchange` met a jour le contexte de marche:
   - `NPCManager.update(current_price)`
   - `OrderBook.resolve_crossed_book()`
4. `Exchange` appelle `OrderBook.execute_limit(...)`.
5. Deux cas:
   - **crossing immediat**: execution totale/partielle au passage,
   - **pas de crossing**: ordre accepte et laisse en `resting order`.
6. Plus tard, **Team B** envoie un `buy market` (sans `price`).
7. `Exchange.try_trade(...)` appelle `OrderBook.execute_market(...)`.
8. Le market buy consomme les meilleures asks disponibles (priorite prix/temps).
9. `Exchange` enregistre:
   - le trade de l'agresseur (Team B),
   - la contrepartie passive (Team A) si son limit a ete touche.
10. La GUI lit `/orderbook` et `/tradeHistory` puis affiche le resultat.

## Message cle pour la reunion
- Un **limit order** n'est pas forcement un trade immediat.
- Il devient trade soit:
  - tout de suite s'il croise le carnet,
  - plus tard quand un market order vient le taper.
- Le matching se fait par priorite **meilleur prix puis ordre d'arrivee**.
- Dans l'etat actuel, les deux jambes (buyer et seller) sont bien mises a jour en position et historique.
