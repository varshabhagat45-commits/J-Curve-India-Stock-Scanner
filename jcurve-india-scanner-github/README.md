# J-Curve India — Live Stock Scanner

A static-first research dashboard for finding Indian companies at earnings inflection points.

## Sector scope

The sector filter is populated dynamically from whatever sectors exist in `data/stocks.json` — there is no hardcoded restriction. The shipped demo dataset currently covers 21 sectors:

Auto Components, Banking & Financials, Capital Goods & Engineering, Cement, Chemicals, Consumer Durables, Defence, Electronics / EMS, FMCG, IT Services, Insurance, Logistics & Infrastructure, Metals & Mining, Oil & Gas, Pharmaceuticals, Power Equipment, Railways, Realty, Renewable Energy, Telecom, Textiles.

To add or remove a sector, add/remove entries with that `sector` value in `data/stocks.json` — the dropdown and demo fallback pick it up automatically. Note: some sectors (Banking & Financials, IT Services, Insurance, Telecom) don't have a standard "EBITDA margin" or "ROCE" figure the same way manufacturing sectors do — for those rows `margin`/`roce` are set to `null` in the JSON and render as `—` in the UI.

## What is included

- J-Curve candidate ranking across the full tracked sector universe (47 candidates, 21 sectors in the demo set)
- Stage 1 / Stage 2 / Stage 3 classification, with Stage 2 flagged as the sweet spot
- The **six-step J-curve** shown explicitly above the scorecard (Trigger → Capacity → Revenue acceleration → Margin expansion → Profit acceleration → Re-rating), with steps 1–3 marked as "the edge" and 5–6 marked as already-obvious/too-late
- 9-point evidence framework (the score)
- **Seven-question check** per candidate — rendered live in the thesis panel from that candidate's own data (what changed, is the sector growing, invested ahead of demand, when does capacity contribute, can revenue run 20%+ for 2–3 years, are margins improving too, is there still price room). Per the source framework, the score is a summary; these seven questions are the actual analysis.
- **Fake J-curve / core-quality check** — each candidate carries a `redFlags` array. Empty means clean; a non-empty array (e.g. an inventory gain, a weak prior-year base, a one-off forex/tax item) renders as a flagged warning in the thesis panel and a ⚑ marker in the table row, so a Stage-3 name that "beat" mostly on non-core items doesn't get mistaken for a real inflection.
- Revenue / EBITDA / PAT acceleration chart
- Margin expansion and ROCE fields
- Capacity/utilization evidence
- Search, sector, score and stage filters
- Responsive dark research-terminal UI
- GitHub Pages deployment workflow

## Important: demo vs live data

The repository ships with clearly fictional demo companies so the UI works immediately.

GitHub Pages is static hosting. It is excellent for the frontend, but it should **not** contain broker/API secrets. GitHub Pages alone also cannot magically provide licensed NSE real-time market data.

For a genuine live version, use:

`Data provider / broker API → secure backend or scheduled worker → data/stocks.json or API endpoint → GitHub Pages frontend`

For NSE market data, check the applicable NSE Data & Analytics licensing and redistribution terms before publishing data. See the official NSE market-data policy.

## Recommended production architecture

### Option A — easiest
- Frontend: GitHub Pages
- Backend: Cloudflare Worker / Vercel Function / Render
- Database: Supabase/Postgres
- Market data: licensed provider or broker API
- Corporate filings/news: permitted feeds
- Scheduled refresh: GitHub Actions or backend cron

### Option B — personal research
- Frontend: GitHub Pages
- Data refresh: local Python script
- Output: `data/stocks.json`
- Push updated JSON to GitHub
- No secret keys in the browser

## J-Curve score

Suggested weighted model:

- Trigger: 15
- Capacity/utilization: 15
- Revenue acceleration: 15
- Margin expansion: 15
- Operating leverage: 10
- Profit acceleration: 5
- Sector tailwind: 10
- Valuation/price room: 10
- Management credibility: 5

Total = 100.

Penalties should be applied for one-offs, dilution, weak cash conversion, excessive valuation, or an unverified trigger — see the fake J-curve check below.

## Seven-question check and fake J-curve check (data schema)

Two fields drive the deeper analysis panels, both set per candidate in `data/stocks.json`:

- The **seven questions** are not stored as text — they're computed in `app.js` (`sevenQuestions()`) from fields already on each candidate: `trigger`, `evidence`, `capacity`, `rev`, `marginExp`, and `price`. If you add a real candidate with real figures, the seven-question panel updates automatically; you don't need to author it separately.
- `redFlags`: an array of strings, empty by default. Add a short factual note (e.g. `"Includes a one-time forex gain on export receivables this quarter."`) for any item that should make a viewer strip it out before trusting the profit jump — inventory gains, a weak year-ago base, exceptional/one-off income, currency or tax items, a single non-repeating order, or a commodity-price blip. A non-empty array renders as "Core check: Flagged" with each reason listed; an empty array renders as "Core check: Clean."

## GitHub Pages deployment

1. Create a GitHub repository.
2. Upload this folder.
3. Push to the default branch.
4. Open **Settings → Pages**.
5. Under **Build and deployment**, select **GitHub Actions**.
6. The included workflow deploys the static site.

GitHub's current documentation supports publishing a static site through GitHub Pages and GitHub Actions.

## Roadmap to a real scanner

1. Replace demo JSON with an authenticated market-data adapter.
2. Add NSE/BSE symbol master.
3. Import 8–12 quarters of financials.
4. Calculate sequential acceleration automatically.
5. Detect capacity/order-book/customer triggers from permitted filings.
6. Add valuation and earnings-estimate engine.
7. Add price/volume confirmation.
8. Add one-off normalization.
9. Back-test Stage-2 signals.
10. Add alerting.

This is a research tool, not investment advice.
