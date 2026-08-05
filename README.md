# Elevator Parking Simulator

Tick-based simulator for **where idle elevators should wait** in an **apartment** building.

Forked from [boarding-sim](https://codingapple1.github.io/boarding-sim/) UI patterns.

## Run

Open `index.html` in a browser (no build step).

### Hosting

- Portfolio: `/elevator/index.html` on the Vercel site
- Permanent Pages: enable GitHub Actions Pages when ready (`.github/workflows/pages.yml`)

## Features

1. Parking strategies: Stay / Lobby / Mid / Spread / Demand
2. **Fixed scenario seed** — same passenger stream across runs
3. **Compare all** — headless strategy table on one scenario (browser-side, instant)
4. Apartment traffic: morning / evening / midday + interfloor %
5. Building view: **Out** (alighted) · shafts · **Hall** (waiting), hover tooltips
6. Collective / SCAN boarding — finish one direction before reversing (e.g. down calls 7→6→4→3→1)
7. Metrics: avg/max wait (ticks), empty travel (floors), **IdleFrac** (saturation), ticks, completed
8. **Batch N** — Monte Carlo over many seeds; CSV log + summary ranking
9. Controls split into **Policy** (parking; future zoning) vs **Environment** (building/traffic/seed) vs **Playback**
10. **[Operational insight tree](INSIGHTS.md)** — parking vs zoning, IdleFrac, sticky dispatch, Batch (each with an example)

## Strategy catalog

There is **no universal optimal parking strategy**. Like airplane boarding methods (WilMA, back-to-front, random), elevator idle placement is a catalog of policies whose ranking depends on traffic regime.

### Baselines in this demo

| Strategy | Idle cars go to… | Typical fit |
| --- | --- | --- |
| **Stay** | Last stop (no reposition) | Reactive baseline; cheap empty travel |
| **Lobby** | Floor 1 | Up-peak / evening ingress |
| **Mid** | Building midpoint | Generic compromise |
| **Spread** | Even home floors along the shaft | Down-peak / egress — cover upper arrivals |
| **Demand** | Recent call-heat floors (spread coverage) | Adaptive heuristic toward busy landings |

### Research / industry directions (not all coded)

| Approach | Idea | Notes |
| --- | --- | --- |
| Arrival-probability parking | Park proportional to expected origin mass (INC/INT/OUT weighted) | Generalizes lobby vs spread by traffic mix |
| MDP / DP lobby count | How *many* cars to keep at lobby in up-peak | Rate- and height-dependent (MERL-style) |
| Proactive standby score | Balance expected wait vs energy to choose standby floors | Complements any dispatcher |
| **Service zoning** | Odd/even or low/high banks | Dominates when saturated — cars rarely park |

Modern practice is **regime-aware**: park under light/medium idle time; **zone** when the bank is always busy. Use **Batch N** to rank baselines over many seeds for a fixed traffic setting.

## Traffic parameters

These three knobs shape the **passenger OD stream** (with the scenario seed). Changing any of them regenerates the scenario.

### Traffic period

Chooses **where trips start** (origin mix). Destinations still follow apartment rules (lobby ↔ upper, plus interfloor).

| Period | Origin mix (approx.) | Typical story |
| --- | --- | --- |
| **Morning egress** | ~90% upper floors, ~10% lobby | Residents leave for work |
| **Evening ingress** | ~90% lobby, ~10% upper | Residents come home |
| **Midday / off-peak** | ~45% lobby, ~55% upper | Mixed daytime traffic |

### Arrival rate

Per-tick probability that **one new passenger** appears (Bernoulli trial). Default **15%** ≈ one arrival every ~6.7 ticks on average. At most one arrival per tick. This is a discrete-time stand-in for a Poisson arrival process; it is **not** exponential inter-arrival sampling.

Higher rate → denser hall calls and more contention between cars.

### Interfloor trips

When a trip starts on an **upper floor**, this is the chance the destination is **another upper floor** instead of the lobby. Default **10%**.

- Lobby origins always go to an upper floor (apartment ingress).
- Upper origins: `(1 − interfloor%)` → lobby, `interfloor%` → other residential floor.

Use a low value for “mostly go downstairs / come home”; raise it to stress mid-building stops.

## Insights (summary)

Canonical wrap-up: **[INSIGHTS.md](INSIGHTS.md)** · **[한국어](INSIGHTS.ko.md)** — takeaways, limitations, interview Q&A, Batch A/B, scope freeze.

Regime evidence (evening / morning / saturated): **[benchmarks/REGIME.md](benchmarks/REGIME.md)** — `npm run batch:morning` · `npm run batch:higharrival`.

1. **No universal parking winner** — evening Lobby, morning Spread; gaps collapse when IdleFrac is saturated.
2. **IdleFrac** tells parking-sensitive vs saturated (then zoning, not parking).
3. **Dispatch ≠ parking** — SCAN / same-dir boarding under the hood; sticky orphans vs reassign thrash (Mid worse on N=100).
4. **Batch before/after** one Policy change; stop before over-processing dispatch.

**Limitations:** synthetic Bernoulli arrivals, tick abstraction, distance+load cost (not group ETA), no real-building calibration — see INSIGHTS.

### When parking matters

Parking strategies matter when cars spend time **idle**. **IdleFrac** = IDLE|PARKING car-ticks / (ticks × elevators): ≥25% parking-sensitive, &lt;10% saturated. Raise arrival → Compare-all gaps and IdleFrac often fall.

### Sticky vs reassign

**Sticky** keeps the first car; **Reassign** rescores each tick. Seed 42 Stay: E1 holds `#76@16` while E3/E4 IDLE@20. Evening Batch N=100: Stay max wait improves under reassign; Mid mean wait worsens — myopic idle steal. Details + table in [INSIGHTS.md](INSIGHTS.md).

### Batch experiment

**Batch N** (default 100) over seeds `base…base+N−1`; CSV + Rank-by. CLI: `npm run batch:sticky` / `batch:reassign`.

## Ideas / later (not in progress)

- Service zoning, arrival-probability parking, MDP lobby count, hall capacity, office OD — only if the portfolio story needs them.
