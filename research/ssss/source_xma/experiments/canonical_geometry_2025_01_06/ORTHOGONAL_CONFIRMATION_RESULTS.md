# Orthogonal Confirmation Results — Canonical XMA Geometry

Status: PHASE 5 DISCOVERY  
Protocol: ORTHOGONAL_CONFIRMATION_PROTOCOL.md

No additive score is used.

## Lower strict XMA episodes

Total: 28

### Volume Structure — 5 bars
```json
{
  "NEUTRAL": {
    "n": 16,
    "pos": 0.5625,
    "mean": -0.00294007980181947,
    "median": 0.004897219939277497
  },
  "NEGATIVE": {
    "n": 8,
    "pos": 0.625,
    "mean": 0.04495547927336763,
    "median": 0.05876358763078582
  },
  "POSITIVE": {
    "n": 4,
    "pos": 0,
    "mean": -0.08329435953860598,
    "median": -0.08525697287381151
  }
}
```

### Daily Volume Profile proxy — 5 bars
```json
{
  "BELOW_VAL": {
    "n": 22,
    "pos": 0.5909090909090909,
    "mean": 0.009006666226636817,
    "median": 0.006758040918319108
  },
  "INSIDE_VALUE": {
    "n": 6,
    "pos": 0.16666666666666666,
    "mean": -0.03645358963043407,
    "median": -0.031242576650368226
  }
}
```

### Breadth — 5 bars
```json
{
  "NEUTRAL": {
    "n": 20,
    "pos": 0.4,
    "mean": -0.015041190365879203,
    "median": -0.022683611659978453
  },
  "NEGATIVE": {
    "n": 8,
    "pos": 0.75,
    "mean": 0.035031115815123706,
    "median": 0.04790485382890419
  }
}
```

### VIX — 5 bars
```json
{
  "NEUTRAL": {
    "n": 28,
    "pos": 0.5,
    "mean": -0.0007348171713069436,
    "median": 0.00041514168578515864
  }
}
```

## Upper strict XMA episodes

Total: 10

### Volume Structure — 5 bars
```json
{
  "POSITIVE": {
    "n": 5,
    "pos": 0.2,
    "mean": -0.04472091398910825,
    "median": -0.05704540068339614
  },
  "NEUTRAL": {
    "n": 4,
    "pos": 0.5,
    "mean": -0.04433423999112324,
    "median": -0.043371071485364954
  },
  "NEGATIVE": {
    "n": 1,
    "pos": 0,
    "mean": -0.030655906970812108,
    "median": -0.030655906970812108
  }
}
```

### Daily Volume Profile proxy — 5 bars
```json
{
  "INSIDE_VALUE": {
    "n": 7,
    "pos": 0.2857142857142857,
    "mean": -0.03983666852619313,
    "median": -0.04614919718728416
  },
  "ABOVE_VAH": {
    "n": 3,
    "pos": 0.3333333333333333,
    "mean": -0.05091358573249812,
    "median": -0.05704540068339614
  }
}
```

### Breadth — 5 bars
```json
{
  "NEUTRAL": {
    "n": 8,
    "pos": 0.375,
    "mean": -0.0381880115057618,
    "median": -0.05159729893534015
  },
  "POSITIVE": {
    "n": 2,
    "pos": 0,
    "mean": -0.06304667241737594,
    "median": -0.06304667241737594
  }
}
```

### VIX — 5 bars
```json
{
  "NEUTRAL": {
    "n": 10,
    "pos": 0.3,
    "mean": -0.04315974368808463,
    "median": -0.05159729893534015
  }
}
```

## Interpretation rule

Because strict geometry episodes are relatively rare, subgroup sample sizes are often small.

No factor is promoted simply because one subgroup has a large mean.

Use minimum-sample discipline:
- <5 INCONCLUSIVE
- 5..9 OBSERVE
- >=10 candidate evidence

The purpose is to identify which auxiliary variable deserves a new forward-validation rule, not to optimize this window.
