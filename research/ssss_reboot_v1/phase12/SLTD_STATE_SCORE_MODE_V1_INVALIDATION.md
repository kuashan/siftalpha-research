# SLTD State Score Mode v1 — Invalidation Notice

Status: **INVALIDATED_BEFORE_RESULT_USE**

This branch was started after the user clarified that state scoring must be a new,
standalone SLTD mode rather than an extension of V7.

During the required repository audit, an already-completed earlier branch was found:

`research/sltd-state-score-exposure-map-v1`
@ `29ceeeb73328e0f1b1108f01ab14179e858c7e5e`

That branch had already executed and closed an independent
`SLTD state -> score -> exposure` architecture on a Fresh24 universe.

Therefore the Fresh30 universe declared by this branch is **not actually untouched**:
several symbols overlap the already-consumed Fresh24 set.

Any workflow result from this branch is invalid for OOS admission and must not be used
to promote, reject, tune or compare a new SLTD mode.

The correct continuation point is the completed Phase12 exposure-map evidence,
not this duplicate branch.

`SLTD_STATE_SCORE_MODE_V1_DUPLICATE = INVALIDATED_NOT_ADMITTED`
