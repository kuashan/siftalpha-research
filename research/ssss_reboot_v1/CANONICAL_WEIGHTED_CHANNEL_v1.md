# SSSS Reboot v1 — Canonical Weighted Channel v1

Status: **AUTHOR-CORRECTED / FROZEN FOR RECONSTRUCTION**
Date: 2026-10-02

## Purpose

This file freezes the corrected slow weighted channel to be used by all SSSS
Reboot v1 reconstruction and validation work.

The original .ftindex files remain unchanged for archival integrity.

## Canonical 20-term high series

```text
W_H :=
(
  20*H
+ 19*REF(H,1)
+ 18*REF(H,2)
+ 17*REF(H,3)
+ 16*REF(H,4)
+ 15*REF(H,5)
+ 14*REF(H,6)
+ 13*REF(H,7)
+ 12*REF(H,8)
+ 11*REF(H,9)
+ 10*REF(H,10)
+  9*REF(H,11)
+  8*REF(H,12)
+  7*REF(H,13)
+  6*REF(H,14)
+  5*REF(H,15)
+  4*REF(H,16)
+  3*REF(H,17)
+  2*REF(H,18)
+    REF(H,19)
) / 210;
```

## Canonical 20-term low series

```text
W_L :=
(
  20*L
+ 19*REF(L,1)
+ 18*REF(L,2)
+ 17*REF(L,3)
+ 16*REF(L,4)
+ 15*REF(L,5)
+ 14*REF(L,6)
+ 13*REF(L,7)
+ 12*REF(L,8)
+ 11*REF(L,9)
+ 10*REF(L,10)
+  9*REF(L,11)
+  8*REF(L,12)
+  7*REF(L,13)
+  6*REF(L,14)
+  5*REF(L,15)
+  4*REF(L,16)
+  3*REF(L,17)
+  2*REF(L,18)
+    REF(L,19)
) / 210;
```

## Weight proof

`20 + 19 + 18 + ... + 2 + 1 = 210`

Therefore the correct final lag is `REF(...,19)`.

A simultaneous extra `REF(...,20)` would make the numerator weight total 211
and is not part of the intended formula.

## Slow channel

`SLOW_TOP = EMA(W_H,90)`

`SLOW_BOTTOM = EMA(W_L,90)`

## Author-confirmed typo corrections

1. Low series lag 11 must be `REF(L,11)`, not `REF(H,11)`.
2. The weighted series is the 20-term 20..1 sequence totaling 210.
3. `REF(...,20)` is excluded from the canonical reconstructed formula.

## Research rule

All future SSSS Reboot v1 calculations must use this canonical version unless a
later explicitly versioned correction supersedes it.

Do not run the malformed raw-source weighted-channel variant as the main model.
