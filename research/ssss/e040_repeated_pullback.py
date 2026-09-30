"""E040 repeated-pullback research configuration.

Discovery-only. No action in this file is production validated.
"""

STARTER_EXPOSURE = 0.30
ADD_EXPOSURE_DELTA = 0.10
MAX_EXPOSURE = 0.50
REDUCE_CURRENT_POSITION_FRACTION = 0.15
CORE_EXPOSURE_FLOOR = 0.30

# Discovery-only provisional repeated LOSS_ADD candidate.
LOSS_PULLBACK_ADD_ENABLED = False
LOSS_PULLBACK_STEP = 0.01
LOSS_PULLBACK_VALIDITY_FLOOR = "FAST_LOWER"
LOSS_PULLBACK_ALLOWED_STATES = ("GREEN", "RED")
LOSS_PULLBACK_REQUIRE_DSEP_POSITIVE = True
LOCAL_ANCHOR_RESET_AFTER_ACTION = True
ACTION_COOLDOWN_BARS = 4

# Same 1% rule is explicitly NOT supported for profitable-position ADD.
TREND_PULLBACK_ADD_ENABLED = False

# No repeated REDUCE threshold passed E040.
REPEATED_REDUCE_ENABLED = False

STATUS = "DISCOVERY_ONLY_INACTIVE"
