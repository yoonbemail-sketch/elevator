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

## Ideas / later

- **Per-floor hall capacity** — limit how many waiting passengers can stack on each floor (lobby vs upper floors), so peak congestion and spillover become visible in metrics and the building view.
- Building type (office OD), floor population weights, car speed (floors/tick), batch arrivals, energy metrics
