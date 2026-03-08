# Documentation `LiquidityCurve` (tradinggame-py)

## Fichier source
- [LiquidityCurve.py](/home/jellilm/Desktop/MStanley/tradinggame-py/app/lib/exchange/LiquidityCurve.py)

## Objectif
Le module `LiquidityCurve` génère une **courbe cible de liquidité** autour du prix courant (`mid`), sous forme:

`{price_level: target_quantity}`

Cette courbe est utilisée par `NPCManager` pour savoir:
- quels niveaux de prix doivent exister dans le carnet,
- avec quelle quantité de liquidité NPC à chaque niveau.

---

## Origine et adaptation

### Inspiré du repo2
Le design est inspiré du générateur de courbe du repo `tradingGame-main`:
- [LiquidityCurve.py](/home/jellilm/Desktop/MStanley/tradingGame-main./tradingGame-main/ExchangeStructure/LiquidityGenerator/LiquidityCurve.py)

### Adaptation locale
La version `tradinggame-py` garde la même logique générale (bimodale, skew, bruit), avec des paramètres calibrés pour le repo1 et l’intégration avec le `NPCManager` local.

---

## Fonctions privées

### `_x_for_probability(probability, mean, stddev)`
Retourne la valeur `x` d’une loi normale pour une probabilité cumulée donnée.

Techniquement:
- utilise `norm.ppf(...)`.

Usage:
- sert à calculer une distance “raisonnable” autour du mid en fonction de `min_pdf`.

---

### `_peak_distance_for_min_pdf(mid_price, stddev, min_pdf)`
Calcule la distance des pics de liquidité autour du mid.

Idée:
1. transforme `min_pdf` en seuil de queue,
2. récupère la borne supérieure correspondante sur la normale,
3. retourne la distance à `mid_price`.

Usage:
- cette distance est ensuite modulée par `trough_depth` pour placer les deux pics de la bimodalité.

---

### `_custom_price_levels(mid, min_price, max_price, num_levels, density_shape=1)`
Génère les niveaux de prix discrets entre `min_price` et `max_price`.

Paramètre clé:
- `density_shape` contrôle la densité des niveaux:
  - `0`: distribution uniforme,
  - `>0`: plus dense au centre,
  - `<0`: plus dense sur les bords.

Sortie:
- liste ordonnée de niveaux de prix.

---

## Fonction principale

### `generate_bimodal_liquidity_curve(...)`
Construit la courbe de liquidité finale (prix -> quantité).

### Signature
```python
generate_bimodal_liquidity_curve(
    mid,
    min_price,
    max_price,
    num_levels=40,
    total_liquidity=600_000,
    stddevperc=0.02,
    trough_depth=0.4,
    liquidity_skew=0.0,
    density_shape=0.0,
    noise_level=0.02,
    min_pdf=0.0001,
    decimal_places=5,
)
```

### Étapes internes
1. Calcule `stddev = stddevperc * mid`.
2. Clamp:
   - `trough_depth` dans `[0,1]`,
   - `density_shape` dans `[-1,1]`.
3. Génère les niveaux de prix (`prices`) via `_custom_price_levels`.
4. Calcule la distance des pics via `_peak_distance_for_min_pdf`.
5. Place deux pics:
   - `peak1 = mid - distance`,
   - `peak2 = mid + distance`.
6. Évalue deux PDF `skewnorm` (ici symétriques, `a=0`), centrées sur ces pics.
7. Applique `liquidity_skew` si non nul (biais gauche/droite).
8. Combine les deux PDF avec `max(pdf1, pdf2)` pour obtenir une forme bimodale.
9. Normalise la PDF (`sum=1`) puis multiplie par `total_liquidity`.
10. Ajoute un bruit gaussien contrôlé (`noise_level`), en gardant des quantités non négatives.
11. Convertit en entiers, arrondit les prix (`decimal_places`).
12. Retourne un dictionnaire sans niveaux à quantité nulle.

### Sortie
Un `dict` Python:
- clé: prix (`float` arrondi),
- valeur: quantité cible (`int`).

Exemple de forme:
```python
{
  0.86870: 3626,
  0.87316: 4465,
  0.87763: 6329,
  ...
}
```

---

## Paramètres importants (interprétation pratique)
- `num_levels`: profondeur discrète de la courbe.
- `total_liquidity`: masse totale de liquidité à répartir.
- `trough_depth`: profondeur du creux au centre entre les 2 pics.
- `liquidity_skew`: asymétrie gauche/droite (bids vs asks).
- `density_shape`: répartition des niveaux de prix (centre vs bords).
- `noise_level`: variabilité aléatoire pour éviter un carnet trop “parfait”.

---

## Intégration dans le système
- `NPCManager._build_curve(...)` appelle `generate_bimodal_liquidity_curve(...)`.
- `NPCManager` aligne ensuite le carnet réel sur cette cible:
  - annulation des niveaux NPC invalides,
  - remplissage des quantités manquantes.

---

## Pourquoi ce module est utile
1. Donne un carnet plus réaliste qu’une rampe linéaire fixe.
2. Permet d’ajuster facilement la “personnalité” du marché simulé via paramètres.
3. Fournit une base robuste pour tester des stratégies d’exécution (impact, slippage, timing).
