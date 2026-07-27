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
7. Metrics: avg/max wait (ticks), empty travel (floors), ticks, completed

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

## Insight: when parking matters

Parking strategies matter when cars spend time **idle**. Under light or moderate traffic, empty-travel and wait times move with Stay / Lobby / Mid / Spread / Demand.

Under **saturated** traffic, cars are almost always busy — they rarely park — so parking policy has little room to act. The useful lever shifts to **service zoning** (e.g. odd/even floors, low/high banks): fewer stops per trip, less door dwell waste, shorter round trips.

This demo isolates **parking** on a fixed passenger stream. Raise arrival rate in Compare all and you should often see strategy gaps shrink — a hint that zoning, not parking, is the next experiment when the building is always full.

## Ideas / later

- **Service zoning** — odd/even or low/high floor banks for high-utilization buildings (complement to parking)
- **Per-floor hall capacity** — limit how many waiting passengers can stack on each floor (lobby vs upper floors), so peak congestion and spillover become visible in metrics and the building view.
- Building type (office OD), floor population weights, car speed (floors/tick), batch arrivals, energy metrics
