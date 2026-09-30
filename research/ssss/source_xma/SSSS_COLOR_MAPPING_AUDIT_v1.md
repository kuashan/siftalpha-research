# SSSS Color Mapping Audit v1

Status: **IMPLEMENTED_AND_VERIFIED**

Date: 2026-09-29

## Purpose

Resolve the rendered color semantics of the original SSSS fast XMA state band
from the preserved `SSSS.ftindex` source, rather than inferring colors from
screenshots.

## Source

Preserved original:
`research/ssss/source_xma/source_indicators/SSSS.ftindex.b64`

Original SSSS SHA-256 recorded in `SOURCE_MANIFEST.md`:
`25f8c56075c0021dd2d0567401d37def25d6a9b895f139b3a8a9abc376fecaa7`

## Raw drawing statements recovered from SSSS.ftindex

```text
STICKLINE(GZB12=1,GZB10,GZB11,5,0),COLOR000066;
STICKLINE(GZB13=1,GZB10,GZB11,5,0),COLOR003300;
STICKLINE(GZB14=1,GZB10,GZB11,5,0),COLOR555555;

STICKLINE(1=1,GZB3,GZB4,5,0),COLORLIGRAY;
```

The fast colored band spans:
- upper = GZB10 / ZK1
- lower = GZB11 / ZD1

The slow background band spans:
- GZB3 .. GZB4

## Color-code interpretation

The custom formula convention uses `COLORbbggrr`, not CSS-style RRGGBB.

Therefore:

- `COLOR000066` = RGB(102,0,0) = **dark red**
- `COLOR003300` = RGB(0,51,0) = **dark green**
- `COLOR555555` = RGB(85,85,85) = **dark gray**
- `COLORLIGRAY` = **light gray**

## State-to-color mapping

Raw SSSS state definitions:

```text
GZB12 := GZB11 >= GZB9 AND GZB10 >= GZB8
GZB13 := GZB10 <= GZB8 AND GZB11 <= GZB9
GZB14 := GZB11 >= GZB9 AND GZB10 <= GZB8
```

Research interpretation:

| Source state | Geometry | Rendered fast-band color |
|---|---|---|
| GZB12 | fast channel shifted upward vs slow structure | **dark red** |
| GZB13 | fast channel shifted downward vs slow structure | **dark green** |
| GZB14 | fast channel contained inside slow structure / range | **dark gray** |

Thus the intended visual semantics are:

- **dark red fast band = UP_STATE**
- **dark green fast band = DOWN_STATE**
- **dark gray fast band = RANGE_STATE**

## Fourth topology

Canonical research also recognizes:

```text
GZB11 < GZB9
AND
GZB10 > GZB8
```

as `EXPANSION_STRADDLE`.

The original SSSS source contains **no fourth STICKLINE color instruction**
for this topology.

Therefore, when this fourth topology occurs, none of the three fast-band
state STICKLINE conditions is responsible for painting a state color.

Research convention:
- store it explicitly as `EXPANSION_STRADDLE`;
- do not invent a fourth color;
- distinguish "no original fast-band state color" from dark gray RANGE.

## Other explicit source colors

The original source also confirms:

```text
ZK1: ... ,DOTLINE,COLORWHITE;
ZD1: ... ,DOTLINE,COLORWHITE;
BS:  ... ,DOTLINE,COLORRED;
BD:  ... ,DOTLINE,COLORGREEN;
```

So:
- FastUpper / ZK1 = white dotted line
- FastLower / ZD1 = white dotted line
- BS outer upper rail = red dotted line by formula/source
- BD outer lower rail = green dotted line by formula/source

The fast midpoint `GZB18=(ZK1+ZD1)/2` is calculated but is not explicitly
drawn by the recovered source formula.

## Research consequence

All future SSSS/XMA analysis should store both:
1. underlying state id / geometry;
2. rendered color.

Do not treat the color itself as the mathematical definition.

For canonical research:
- UP_STATE -> dark red
- DOWN_STATE -> dark green
- RANGE_STATE -> dark gray
- EXPANSION_STRADDLE -> no original SSSS fast-band color
- slow GZB3..GZB4 band -> light gray

Closure:
`SSSS_COLOR_MAPPING = IMPLEMENTED_AND_VERIFIED`
