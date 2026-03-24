# Points À Venir - Réunion avec JP (repo2) et équipe repo1

## 1) Contexte actuel (ce qui est déjà intégré)

L'intégration actuelle dans `tradinggame-orderbook-integration-clean` couvre:
- un `OrderBook` (bids/asks triés),
- un endpoint `GET /orderbook/<product>?levels=N`,
- affichage live du carnet dans la GUI,
- un `NPCManager` inspiré du repo2,
- une `LiquidityCurve` bimodale pour cibler la profondeur,
- exécution des trades market contre le carnet (`execute_market`).

En clair: la base order book est posée et fonctionnelle.

---

## 2) Écart restant vs repo2 (JP)

## 2.1 Limit Orders complets (priorité haute)

### État actuel
- Le flux principal de trade reste orienté market (`/trade` -> `try_trade` -> `execute_market`).
- Le carnet contient surtout la liquidité NPC.

### Cible (repo2-like)
- Support complet des ordres limite équipes:
  - création d'ordre limite (resting order),
  - matching si crossing instantané,
  - maintien en carnet sinon,
  - annulation d'ordre équipe par `order_id`.

### Décision attendue en réunion
- API cible: étendre `/trade` ou créer `/order`.
- Format de réponse attendu (`FILLED`, `PARTIAL`, `ACCEPTED`, `CANCELLED`, etc.).

---

## 2.2 Lifecycle NPC et granularité du refill

### État actuel
- `npc_manager.update(current_price)` est appelé:
  - sur `/orderbook`,
  - juste avant `/trade`.

### Cible (repo2-like avancé)
- Ajuster la fréquence de refill pour mieux exposer l'impact marché.
- Éviter un refill trop agressif qui masque la consommation intra-tick.

### Décision attendue
- NPC update:
  - à chaque tick global exchange?
  - à chaque read API?
  - ou seulement à fréquence fixe?

---

## 2.3 Tracking des ordres (visibilité gameplay)

### État actuel
- Le snapshot renvoie prix/quantités.
- Pas de séparation claire affichée `NPC` vs `Team`.

### Cible
- Exposer métadonnées dans snapshot:
  - owner/type (`NPC`, `TEAM`),
  - éventuellement agrégation séparée.

### Impact
- meilleure pédagogie en event,
- debug plus simple des stratégies.

---

## 2.4 Tests de non-régression (priorité haute)

### À ajouter
- unit tests `OrderBook`:
  - tri bid/ask,
  - matching market,
  - partial fill / failed fill.
- unit tests `NPCManager`:
  - cancel invalid,
  - fill missing.
- tests API:
  - `/orderbook`,
  - `/trade`,
  - endpoints admin.

### Pourquoi
- stabiliser avant d'étendre (limit orders).

---

## 2.5 Paramétrage runtime (ops/event)

### État actuel
- plusieurs paramètres sont encore hardcodés (curve/NPC).

### Cible
- passer les paramètres clés en env vars:
  - `NUM_LEVELS`,
  - `TOTAL_LIQUIDITY`,
  - `NOISE_LEVEL`,
  - `NPC_UPDATE_MODE`.

### Bénéfice
- adaptation rapide par event sans modifier le code.

---

## 2.6 Documentation d’exploitation (facilitateur run)

### À finaliser
- mode local (ports API/GUI),
- mode event (enable/disable trading, reset, crash/bounce),
- runbook incident (book vide, PnL incohérent, API down).

---

## 3) Proposition de plan d’exécution (Sprints courts)

## Sprint 1 (immédiat)
1. Valider design API limit orders avec JP.
2. Implémenter limit orders minimal + cancel.
3. Ajouter tests unitaires matching.

## Sprint 2
1. Améliorer refill NPC (fréquence/config).
2. Exposer owner metadata dans snapshot.
3. Adapter GUI (filtres/lecture).

## Sprint 3
1. Durcir tests API end-to-end.
2. Paramétrage env complet.
3. Nettoyage final doc/runbook.

---

## 4) Questions à poser en réunion (checklist)

1. Voulez-vous une parité stricte avec repo2 ou une adaptation gameplay?
2. Quel comportement exact pour limit orders crossing/non-crossing?
3. Refill NPC: fréquence cible pour garder l'impact de marché visible?
4. Quels statuts de trade/order doivent être exposés à la GUI?
5. Quel niveau de détail souhaité dans `/orderbook` (agrégé vs ordres bruts)?
6. Priorité business: réalisme microstructure vs simplicité pédagogique?

---

## 5) Résumé 30 secondes

La base order book est intégrée et stable (API + GUI + NPC curve).  
Le prochain bloc prioritaire est le support complet des **limit orders équipes** avec tests.  
On doit ensuite calibrer la fréquence NPC pour préserver l’impact marché visible, et aligner les formats API avec les attentes repo2/JP.

