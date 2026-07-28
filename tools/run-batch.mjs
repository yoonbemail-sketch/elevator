#!/usr/bin/env node
/**
 * Headless Batch N runner for before/after dispatch benchmarks.
 * Usage:
 *   node tools/run-batch.mjs --dispatch sticky --n 100 --seed 42 --out benchmarks/sticky-n100
 *   node tools/run-batch.mjs --dispatch reassign --n 100 --seed 42 --out benchmarks/reassign-n100
 */
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';
import { parseHTML } from 'linkedom';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const root = path.resolve(__dirname, '..');

function parseArgs(argv) {
    const opts = {
        dispatch: 'sticky',
        n: 100,
        seed: 42,
        peak: 'evening',
        arrival: 0.15,
        interfloor: 0.10,
        floors: 20,
        elevators: 4,
        capacity: 8,
        dwell: 2,
        target: 80,
        out: null,
    };
    for (let i = 0; i < argv.length; i++) {
        const a = argv[i];
        const next = argv[i + 1];
        if (a === '--dispatch') { opts.dispatch = next; i++; }
        else if (a === '--n') { opts.n = Number(next); i++; }
        else if (a === '--seed') { opts.seed = Number(next); i++; }
        else if (a === '--peak') { opts.peak = next; i++; }
        else if (a === '--arrival') { opts.arrival = Number(next); i++; }
        else if (a === '--interfloor') { opts.interfloor = Number(next); i++; }
        else if (a === '--floors') { opts.floors = Number(next); i++; }
        else if (a === '--elevators') { opts.elevators = Number(next); i++; }
        else if (a === '--capacity') { opts.capacity = Number(next); i++; }
        else if (a === '--dwell') { opts.dwell = Number(next); i++; }
        else if (a === '--target') { opts.target = Number(next); i++; }
        else if (a === '--out') { opts.out = next; i++; }
    }
    if (!opts.out) {
        opts.out = path.join('benchmarks', `${opts.dispatch}-n${opts.n}-seed${opts.seed}`);
    }
    return opts;
}

function loadSim() {
    const html = fs.readFileSync(path.join(root, 'index.html'), 'utf8');
    const { window, document } = parseHTML(html);
    globalThis.window = window;
    globalThis.document = document;
    const nav = { clipboard: null };
    // Classic script expects browser globals
    const code = fs.readFileSync(path.join(root, 'script.js'), 'utf8');
    // eslint-disable-next-line no-new-func
    const run = new Function('window', 'document', 'navigator', 'globalThis', code + '\nreturn globalThis.ElevatorSim;');
    return run(window, document, nav, globalThis);
}

function main() {
    const opts = parseArgs(process.argv.slice(2));
    if (opts.dispatch !== 'sticky' && opts.dispatch !== 'reassign') {
        console.error('Invalid --dispatch (sticky|reassign)');
        process.exit(1);
    }

    const api = loadSim();
    api.applySettings({
        hallDispatch: opts.dispatch,
        scenarioSeed: opts.seed,
        peakMode: opts.peak,
        arrivalRate: opts.arrival,
        interfloorRate: opts.interfloor,
        floors: opts.floors,
        elevatorCount: opts.elevators,
        capacity: opts.capacity,
        doorDwell: opts.dwell,
        targetPassengers: opts.target,
    });

    const t0 = Date.now();
    console.error(`Running Batch N=${opts.n} dispatch=${opts.dispatch} baseSeed=${opts.seed}…`);
    const result = api.runBatchSync({ n: opts.n, baseSeed: opts.seed });
    const ms = Date.now() - t0;

    const outDir = path.isAbsolute(opts.out) ? opts.out : path.join(root, opts.out);
    fs.mkdirSync(outDir, { recursive: true });
    fs.writeFileSync(path.join(outDir, 'batch.csv'), result.csv);
    fs.writeFileSync(path.join(outDir, 'summary.txt'), result.text);
    const ranked = [...result.summary].sort((a, b) => a.meanWait - b.meanWait);
    const meta = {
        createdAt: new Date().toISOString(),
        elapsedMs: ms,
        settings: {
            hallDispatch: opts.dispatch,
            n: opts.n,
            baseSeed: opts.seed,
            peak: opts.peak,
            arrival: opts.arrival,
            interfloor: opts.interfloor,
            floors: opts.floors,
            elevators: opts.elevators,
            capacity: opts.capacity,
            dwell: opts.dwell,
            target: opts.target,
        },
        rankingByAvgWait: ranked.map((s, i) => ({
            rank: i + 1,
            strategy: s.strategy,
            meanWait: s.meanWait,
            stdWait: s.stdWait,
            meanMaxWait: s.meanMaxWait,
            meanEmpty: s.meanEmpty,
            meanIdleFrac: s.meanIdleFrac,
            meanTicks: s.meanTicks,
            winRate: s.winRate,
            incomplete: s.incomplete,
        })),
        overallIdleFrac: ranked[0]?.overallIdleFrac ?? null,
        overallRegime: ranked[0]?.overallRegime ?? null,
    };
    fs.writeFileSync(path.join(outDir, 'summary.json'), JSON.stringify(meta, null, 2) + '\n');

    console.error(`Done in ${(ms / 1000).toFixed(1)}s → ${outDir}`);
    console.log(result.text.trimEnd());
}

main();
