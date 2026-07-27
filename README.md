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
3. **Compare all** — headless strategy table on one scenario
4. Apartment traffic: morning / evening / midday + interfloor %
5. Metrics: avg/max wait, empty travel, ticks
