---
topic_tags: [macro, cross-asset, impact, wire]
applies_to_reports: [daily_morning]
last_reviewed: 2026-09-16
provenance: "operator-curated from standard cross-asset relationships; refined during Session 3 MARKET WIRE build"
---

# Cross-asset impact matrix — reference for daily MARKET WIRE

This is the reference the LLM applies when it writes the "Impact" line of a
market-wire item. Directions are the DOMINANT first-order reaction, not
guarantees — the wire item must acknowledge exceptions when today's tape
contradicts the default (e.g. gold rallies on a hawkish surprise when the
move is small enough that safe-haven flows dominate the rate-differential
mechanism).

## Reading key

- `+` = the asset typically appreciates
- `−` = the asset typically depreciates
- `~` = mixed / requires more context / depends on magnitude

## Rates driver

### US 10Y or 30Y Treasury yield rises sharply
- USD: `+` — higher real yields attract foreign capital
- Gold: `−` — non-yielding asset loses on real-rate cost
- Stocks: `−` — discount rate up, growth multiples compress first (Nasdaq > S&P)
- Crypto: `−` — same duration-sensitivity as high-multiple growth
- Sectors: real estate `−−`, banks `+` (NIM), homebuilders `−`, tech growth `−`

### US 10Y yield falls sharply (bull steepening / recession bid)
- USD: `−` if driven by dovish Fed re-pricing; `+` if driven by global risk-off
- Gold: `+` — real-rate cost drops
- Stocks: `~` — bond-proxy sectors `+`, cyclicals `−` if recession-signal
- Crypto: `+` if risk-on interpretation, `−` if flight-to-quality

## Inflation driver

### CPI/PCE surprise HIGHER than consensus
- USD: `+` — repricing to more Fed hikes / delayed cuts
- Gold: `~` — usually `−` initially on rate repricing; `+` later if sticky-inflation regime confirmed
- Stocks: `−` — earnings multiple compression; growth harder-hit than value
- Crypto: `−` initially; `+` structurally if fiat-debasement narrative dominates
- Sectors: energy `+`, financials `+`, tech `−`, utilities `−`

### CPI/PCE surprise LOWER than consensus
- USD: `−` — dovish repricing
- Gold: `+` — real-rate relief
- Stocks: `+` — multiple expansion; growth outperforms value
- Crypto: `+` — same duration bid as growth stocks

## USD driver

### DXY breaks meaningfully higher
- Gold: `−` — dollar-priced commodity
- Oil: `−` — same dollar mechanism
- EM equities: `−` — dollar debt burden
- US large-cap: `~` — exporters `−`, domestic-facing `+`

### DXY breaks meaningfully lower
- Gold: `+`
- Oil: `+`
- EM equities: `+`
- US multinationals: `+` (FX translation tailwind)

## Fed policy driver

### Hawkish FOMC surprise (statement, dots, or Powell)
- USD: `+`
- Gold: `−`
- Stocks: `−` (growth `−−`, value `−`)
- Crypto: `−`
- Bonds: `−` (yields up)

### Dovish FOMC surprise
- USD: `−`
- Gold: `+`
- Stocks: `+`
- Crypto: `+`
- Bonds: `+` (yields down)

## Labor driver

### NFP HOT (payrolls or wages beat significantly)
- USD: `+` — hawkish repricing
- Gold: `−`
- Stocks: `~` — good-is-bad in restrictive regime; `+` in expansionary regime
- Crypto: `−`

### NFP COLD (payrolls or wages miss significantly, or unemployment rate up)
- USD: `−`
- Gold: `+`
- Stocks: `~` — bad-is-good in restrictive regime (rate-cut bid); `−` when recession signal dominates
- Crypto: `+`

## Growth / activity driver

### ISM Manufacturing / Services surprise HIGHER
- USD: `+`
- Gold: `~` (usually `−` on rate repricing)
- Stocks: `+` — cyclicals lead
- Crypto: `+`
- Sectors: industrials `+`, materials `+`, consumer discretionary `+`

### ISM surprise LOWER
- Reverse of above; watch for recession-fear regime flip

## Oil / commodity driver

### WTI or Brent breaks sharply higher (supply shock, OPEC cut, geopolitics)
- USD: `~` (usually `+` on inflation repricing)
- Gold: `+` — inflation hedge
- Stocks: `−` (energy `++`, transports `−`, consumer `−`)
- Crypto: `~`
- Bonds: `−` (yields up on inflation)

### Oil crashes lower (demand fear or supply glut)
- USD: `~`
- Gold: `~`
- Stocks: `+` if demand-supply-glut driven; `−` if demand-collapse driven
- Bonds: `+` (disinflation)

## Geopolitical / risk-off driver

### Major geopolitical escalation (war headline, tariff shock, sovereign crisis)
- USD: `+` — safe-haven bid
- Gold: `+` — traditional safe haven
- Stocks: `−` — flight from risk
- Crypto: `~` — narrative-dependent; usually `−` first, `+` if fiat-debasement lens
- Bonds (US Treasuries): `+` — safe-haven bid

### Geopolitical de-escalation / diplomatic breakthrough
- Reverse — risk-on across the board

## Treasury supply / auction driver

### Weak long-end auction (30Y or 10Y tails badly, low bid-to-cover)
- USD: `~` (usually `−` on fiscal-worry lens)
- Gold: `+` — fiscal-worry hedge bid
- Stocks: `−` (long-duration equities hit hardest)
- Bonds: `−` (yields up)

### Strong auction with foreign bid
- Reverse — duration bid, growth-equity bid

## Regime overrides

When today's regime is stressed (VIX > 20), FLIGHT-TO-QUALITY dominates the
above defaults:
- Any risk-off headline strengthens USD + Treasuries even when the mechanism
  would normally weaken them
- Gold decouples upward from real rates
- Crypto usually behaves like a high-beta risk asset (with USD strength), NOT
  as a safe haven

When today's regime is calm (VIX < 15), MEAN-REVERSION dominates the
above defaults:
- Small surprises produce smaller and faster-reverting moves
- Sector rotation matters more than index direction

## How to WRITE the impact line

Format: `💵 USD [+/−/~] · 🥇 Gold [+/−/~] · 📈 Stocks [+/−/~] · ₿ Crypto [+/−/~] · [optional key sector]`

- Pick each direction using the tables above, cross-referenced with the current
  regime label from the market snapshot
- If the mechanism is ambiguous or the magnitude is small, use `~` — do not
  invent a direction to sound confident
- The optional key-sector token names ONE sector where the second-order impact
  is loudest (e.g. `Real Estate −−` on a yields-up story; `Energy ++` on an
  oil supply shock)
- Never claim a direction the tables above don't support without explaining
  the regime override in the Significance line
