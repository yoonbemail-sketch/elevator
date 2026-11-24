#!/usr/bin/env python3
"""
p-median parking optimizer for the elevator simulator.

For each traffic period (morning / evening / midday), building height F and
number of idle cars k, choose k parking floors that minimize the expected
travel distance (floors) from the nearest parked car to the origin of the
next hall call. Origin weights replicate pickOrigin() in script.js exactly.

    min   sum_i sum_j w_i * |i - j| * x_ij
    s.t.  sum_j x_ij = 1            for every origin floor i
          x_ij <= y_j               for every i, j
          sum_j y_j = k
          x_ij >= 0, y_j in {0,1}

Usage:
    .venv/bin/python tools/optimize_parking.py            # writes data/optimized-parking.{json,js}
    .venv/bin/python tools/optimize_parking.py --out-dir data --min-floors 8 --max-floors 40 --max-k 8

Outputs
    data/optimized-parking.json  canonical result (read by tools/run-batch.mjs)
    data/optimized-parking.js    same data as `globalThis.OPTIMIZED_PARKING_DATA = …`
                                 so index.html also works when opened via file://
                                 (browsers block fetch() of local JSON there).
"""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

import gurobipy as gp
from gurobipy import GRB

LOBBY = 1

# Share of arrivals that start at the lobby, per pickOrigin() in script.js.
# The remainder is uniform over upper floors 2..F (randInt(2, floors)).
LOBBY_SHARE = {
    "morning": 0.10,
    "evening": 0.90,
    "midday": 0.45,
}

# UI ranges in index.html (floors-range 8..40, elevators-range 1..8)
DEFAULT_MIN_FLOORS = 8
DEFAULT_MAX_FLOORS = 40
DEFAULT_MAX_K = 8


def origin_weights(period: str, floors: int) -> dict[int, float]:
    lobby = LOBBY_SHARE[period]
    upper = (1.0 - lobby) / (floors - 1)
    return {f: (lobby if f == LOBBY else upper) for f in range(1, floors + 1)}


def build_model(weights: dict[int, float], env: gp.Env):
    """One model per (period, F); k is changed via the cardinality RHS."""
    floors = sorted(weights)
    m = gp.Model("p_median_parking", env=env)
    y = m.addVars(floors, vtype=GRB.BINARY, name="park")
    x = m.addVars(floors, floors, lb=0.0, ub=1.0, name="serve")
    m.setObjective(
        gp.quicksum(weights[i] * abs(i - j) * x[i, j] for i in floors for j in floors),
        GRB.MINIMIZE,
    )
    m.addConstrs((x.sum(i, "*") == 1 for i in floors), name="cover")
    m.addConstrs((x[i, j] <= y[j] for i in floors for j in floors), name="link")
    card = m.addConstr(y.sum() == 1, name="k_cars")
    return m, y, card


def solve_period_height(period: str, floors: int, max_k: int, env: gp.Env) -> dict[str, dict]:
    weights = origin_weights(period, floors)
    m, y, card = build_model(weights, env)
    out = {}
    for k in range(1, min(max_k, floors) + 1):
        card.RHS = k
        m.optimize()
        if m.Status != GRB.OPTIMAL:
            raise RuntimeError(f"{period} F={floors} k={k}: status {m.Status}")
        chosen = sorted(j for j in y if y[j].X > 0.5)
        out[str(k)] = {
            "floors": chosen,
            "expectedDistance": round(m.ObjVal, 6),
        }
    return out


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out-dir", default=str(Path(__file__).resolve().parent.parent / "data"))
    ap.add_argument("--min-floors", type=int, default=DEFAULT_MIN_FLOORS)
    ap.add_argument("--max-floors", type=int, default=DEFAULT_MAX_FLOORS)
    ap.add_argument("--max-k", type=int, default=DEFAULT_MAX_K)
    args = ap.parse_args()

    env = gp.Env(empty=True)
    env.setParam("OutputFlag", 0)
    env.setParam("Threads", 1)  # deterministic tie-breaking across machines
    env.start()

    solutions: dict[str, dict] = {}
    for period in LOBBY_SHARE:
        solutions[period] = {}
        for floors in range(args.min_floors, args.max_floors + 1):
            solutions[period][str(floors)] = solve_period_height(period, floors, args.max_k, env)
        sample = solutions[period].get("20", {}).get("4")
        if sample:
            print(f"{period:8s} F=20 k=4 → {sample['floors']}  E[dist]={sample['expectedDistance']:.3f}")

    data = {
        "model": "p-median",
        "objective": "min expected |origin - nearest parked car| (floors)",
        "generatedBy": "tools/optimize_parking.py",
        "generatedAt": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "solver": "gurobi " + ".".join(map(str, gp.gurobi.version())),
        "originMix": {
            p: {"lobby": s, "upperUniform": round(1 - s, 6)} for p, s in LOBBY_SHARE.items()
        },
        "floorsRange": [args.min_floors, args.max_floors],
        "maxK": args.max_k,
        "solutions": solutions,
    }

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(data, separators=(",", ":"))
    (out_dir / "optimized-parking.json").write_text(payload + "\n")
    (out_dir / "optimized-parking.js").write_text(
        "// Generated by tools/optimize_parking.py — mirror of optimized-parking.json "
        "for file:// loading. Do not edit.\n"
        f"globalThis.OPTIMIZED_PARKING_DATA = {payload};\n"
    )
    print(f"wrote {out_dir / 'optimized-parking.json'} and .js mirror")


if __name__ == "__main__":
    main()
