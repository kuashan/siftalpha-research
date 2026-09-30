# Source Indicator Manifest

Recorded: 2026-09-27

## Supplied originals

### SSSS.ftindex
- size: 5118 bytes
- SHA-256: `25f8c56075c0021dd2d0567401d37def25d6a9b895f139b3a8a9abc376fecaa7`
- original binary container preserved in this branch as `source_indicators/SSSS.ftindex.b64`

### ADKBY-E.ftindex
- size: 6328 bytes
- SHA-256: `7bbd62e04e0f529ff2040919f028416f5c892e9a00193d326556e36497d8ca5c`
- original binary container preserved in this branch as `source_indicators/ADKBY-E.ftindex.b64`

To reconstruct the exact original bytes:

```bash
base64 -d SSSS.ftindex.b64 > SSSS.ftindex
base64 -d ADKBY-E.ftindex.b64 > ADKBY-E.ftindex
```

Then verify the SHA-256 values above.

## Important formula relationship

Both indicators share:

```text
VL25_X = XMA(XMA(L,25),25)
VH25_X = XMA(XMA(H,25),25)
VDIFF  = VH25_X - VL25_X

upper = VH25_X + VDIFF
lower = VL25_X - VDIFF
```

ADKBY-E's normalized 20000/80000 levels correspond to this lower/upper geometry.

## Source differences that must remain visible

### SSSS slow weighted HIGH
The source omits lag 19 and uses lag 20 with weight 1, which keeps the written denominator 210 consistent with the listed weights.

### SSSS slow weighted LOW
The source uses `REF(H,11)` at the lag-11 term instead of `REF(L,11)`. This is preserved as source behavior and must not be silently corrected in an SSSS-source replay.

### ADKBY-E weighted HIGH/LOW
ADKBY-E uses both lag 19 and lag 20 with weight 1 while still dividing by 210.

That means the listed numerator weights sum to 211, not 210.

ADKBY-E also uses `REF(L,11)` in the low structure.

Therefore SSSS and ADKBY-E do **not** have identical slow 90-period structures even though they share the core 25-XMA band.

## Research rule

Do not decide which source is "correct" by editing one into the other.

Record both variants separately and test what information each contributes.


### HYS2.ftindex
- size: 4713 bytes
- SHA-256: `40936da053455c2e4d05d4bab3f28757e3c59c6cc92668e7c98dd443743799c3`
- market switch: `SCQH=0 A-share / 1 US / 2 crypto`
- extracted formula preserved as `source_indicators/HYS2_formula_extracted.txt`
- research status: CANDIDATE_FEATURE, not part of the XMA baseline
- detailed evaluation: `HYS2_EVALUATION.md`

Important: HYS2 was introduced after the January ABT decisions were frozen. January HYS2 analysis is post-hoc and cannot alter the original January paper result.


### FIVEGZ5SE.txt
- size: 93,201 bytes
- SHA-256: `61bc9f7cad7a2efb6374a187c680fa75789b2468824885e5127c5f70333400c9`
- source: user-supplied formula text
- comments/display words are not treated as semantic ground truth
- research status: CANDIDATE_STATE_ENGINE
- detailed evaluation: `FIVEGZ5SE_EVALUATION.md`
- ABT January post-hoc state log: `experiments/abt_2025_walkforward/fivegz5se_posthoc_jan2025.csv`
