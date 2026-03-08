import numpy as np
from scipy.stats import norm, skewnorm


def _x_for_probability(probability, mean, stddev):
    return norm.ppf(probability, loc=mean, scale=stddev)


def _peak_distance_for_min_pdf(mid_price, stddev, min_pdf):
    min_pdf = min_pdf / 2.0
    upper_bound = _x_for_probability(1 - min_pdf, mid_price, stddev)
    return upper_bound - mid_price


def _custom_price_levels(mid, min_price, max_price, num_levels, density_shape=1):
    x = np.linspace(-1, 1, num_levels)
    if density_shape == 0:
        x_non_linear = x
    elif density_shape > 0:
        x_non_linear = np.sign(x) * np.abs(x) ** (1 + density_shape)
    else:
        x_non_linear = np.sign(x) * (1 - (1 - np.abs(x)) ** (1 - density_shape))

    return list(mid + x_non_linear * (max_price - min_price) / 2)


def generate_bimodal_liquidity_curve(
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
):
    stddev = stddevperc * mid
    trough_depth = min(1, max(0, trough_depth))
    density_shape = min(1, max(-1, density_shape))

    prices = _custom_price_levels(mid, min_price, max_price, num_levels, density_shape)
    distance = _peak_distance_for_min_pdf(mid, stddev, min_pdf)
    distance = (1 - trough_depth) * distance

    peak1 = mid - distance
    peak2 = mid + distance

    pdf1 = skewnorm.pdf(prices, a=0, loc=peak1, scale=stddev)
    pdf2 = skewnorm.pdf(prices, a=0, loc=peak2, scale=stddev)

    if liquidity_skew != 0:
        pdf1 = pdf1 * (1 + liquidity_skew)
        pdf2 = pdf2 * (1 - liquidity_skew)

    pdf = np.maximum(pdf1, pdf2)
    pdf /= pdf.sum()

    liquidity = pdf * total_liquidity
    rng = np.random.default_rng()
    noise = rng.normal(loc=0, scale=noise_level * np.max(liquidity), size=liquidity.shape)
    liquidity = np.maximum(0, liquidity + noise).astype(int)

    return {
        round(float(price), decimal_places): int(qty)
        for price, qty in zip(prices, liquidity)
        if int(qty) > 0
    }
