# Canonical Weighted Channel Specification v1

## Authoritative formula

```text
W20_H :=
(20*H+19*REF(H,1)+18*REF(H,2)+17*REF(H,3)+16*REF(H,4)
+15*REF(H,5)+14*REF(H,6)+13*REF(H,7)+12*REF(H,8)+11*REF(H,9)
+10*REF(H,10)+9*REF(H,11)+8*REF(H,12)+7*REF(H,13)+6*REF(H,14)
+5*REF(H,15)+4*REF(H,16)+3*REF(H,17)+2*REF(H,18)+REF(H,19))/210;

W20_L :=
(20*L+19*REF(L,1)+18*REF(L,2)+17*REF(L,3)+16*REF(L,4)
+15*REF(L,5)+14*REF(L,6)+13*REF(L,7)+12*REF(L,8)+11*REF(L,9)
+10*REF(L,10)+9*REF(L,11)+8*REF(L,12)+7*REF(L,13)+6*REF(L,14)
+5*REF(L,15)+4*REF(L,16)+3*REF(L,17)+2*REF(L,18)+REF(L,19))/210;
```

## Required use

SSSS:
- GZB1 = W20_H
- GZB2 = W20_L
- GZB5 = W20_H
- GZB6 = W20_L

ADKBY-E:
- 短高H = W20_H
- 短低L = W20_L

No lag-20 term is allowed in the canonical v1 weighted channel.
