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

Canonical tree + examples: **[INSIGHTS.md](INSIGHTS.md)**  
`Environment → IdleFrac regime → Parking | Zoning` and orthogonal **sticky hall-call dispatch → reassignment**.

### When parking matters

Parking strategies matter when cars spend time **idle**. Under light or moderate traffic, empty-travel and wait times move with Stay / Lobby / Mid / Spread / Demand.

**IdleFrac** = (elevator-ticks in IDLE or PARKING) / (ticks × elevators). Live and Batch show this as a saturation diagnostic with a regime chip: **≥25%** → `parking-sensitive`, **&lt;10%** → `saturated` (zoning-sensitive hint), otherwise `mixed`. Ranking still uses avg wait (or the Rank-by toggle); IdleFrac is not an objective.

Under **saturated** traffic, cars are almost always busy — they rarely park — so parking policy has little room to act. The useful lever shifts to **service zoning** (e.g. odd/even floors, low/high banks).

**Example.** Same seed, raise arrival rate → Compare-all gaps shrink and IdleFrac drops.

### Sticky hall-call assignment

Dispatch is nearest-car cost at passenger arrival; **assignments stick**. A later closer IDLE does not steal the call. SCAN delays opposite-direction pickups until the assigned car finishes its current direction.

**Example** (seed 42, Stay, evening, tick 650, IdleFrac 62%): E1 MOVING @9↑ load 4 holds pickup `#76 @16→L1`, while **E3/E4 IDLE @20** are closer to 16. Cost *now* prefers E3/E4, but `#76` was assigned at `arr=619` and never moved. Full snapshot in [INSIGHTS.md §3](INSIGHTS.md#3-sticky-hall-call-assignment).

Parking and **call reassignment** are separate levers. High IdleFrac + long waits often means free cars exist, but sticky dispatch will not hand them the call.

### Batch experiment

**Batch N** (default 100) runs seeds `base … base+N−1` with current traffic knobs, each strategy headless, then shows mean wait / empty / Idle% / win-rate and downloads a CSV log. Re-run with the same base seed for a deterministic repeat. Use it to rank baselines *for this regime* (and try Rank-by empty vs wait).

## Ideas / later

- **Hall-call reassignment** — re-score unboarded assignments each tick so nearer idle cars can steal sticky calls
- **Arrival-probability parking** — park from INC/INT/OUT-weighted origin distribution
- **Dynamic lobby count** — MDP-style how many cars stay at lobby in up-peak
- **Service zoning** — odd/even or low/high floor banks for high-utilization buildings (complement to parking)
- **Per-floor hall capacity** — limit how many waiting passengers can stack on each floor (lobby vs upper floors), so peak congestion and spillover become visible in metrics and the building view.
- Building type (office OD), floor population weights, car speed (floors/tick), batch arrivals, energy metrics
