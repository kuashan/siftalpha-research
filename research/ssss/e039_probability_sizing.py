"""E039 15m probability-sizing research configuration.

Discovery result only. Nothing in this file is a validated production action.
"""

STARTER_EXPOSURE = 0.30
ADD_EXPOSURE_DELTA = 0.10
MAX_EXPOSURE = 0.50

# User-requested REDUCE semantics: sell 15% of CURRENT position quantity.
REDUCE_CURRENT_POSITION_FRACTION = 0.15

# E039 Discovery did NOT validate probability-driven actions.
TREND_ADD_ENABLED = False
LOSS_ADD_ENABLED = False
PROFIT_RISK_REDUCE_ENABLED = False
LOSS_RISK_REDUCE_ENABLED = False

# Provisional Discovery-only LOSS_ADD research zone.
# -6% was the least sparse level with positive mean/median/PF>1.25,
# but had only 7 events versus the required minimum of 8.
LOSS_ADD_CANDIDATE_THRESHOLD = -0.06
LOSS_ADD_CANDIDATE_BAND = (-0.07, -0.06)

# No active probability cutoffs survived E039.
P_UP_HIGH_ACTIVE = None
P_DD4H_HIGH_ACTIVE = None

STATUS = "DISCOVERY_ONLY_INACTIVE"
