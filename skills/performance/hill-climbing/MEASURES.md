# Lab measures

Reference for step 2 of [`hill-climbing`](SKILL.md) and step 3 of [`perf-baseline`](../perf-baseline/SKILL.md). Pick by runtime; every entry is deterministic for a fixed input, so the check is equality, not statistics.

## Node and other V8 hosts

| Measure | How | When it is the right one |
|---|---|---|
| Instruction count | `valgrind --tool=callgrind` (or `perf stat -e instructions:u` where counters are readable) around `node --predictable --single-threaded <bench>`; the count is the number | CPU-bound hot paths when the host has valgrind or perf counters |
| Function call counts | `node:inspector` session, `Profiler.startPreciseCoverage({callCount: true, detailed: true})` around the measured iterations, sum `ranges[0].count` per function | The portable default: works on any Node, no privileges, and names the hot functions in the same run |
| Operation counts | wrap the expensive primitives for the duration of the run (`JSON.parse`, `JSON.stringify`, `TextEncoder.encode`, `new Headers`, `RegExp.prototype.exec`) and count calls | When a call-count total is flat but the work per call moved |
| Allocation count | `--trace-gc` scavenge count, or `v8.getHeapStatistics().total_allocated_bytes` deltas under `--predictable` | GC-driven jank, string churn (the UTF-16 case: one non-Latin-1 character makes the whole string two-byte) |

`--predictable` removes the concurrent recompiler and the sampler; `--single-threaded` removes worker threads. Warm the code first (run the input a fixed number of times, discarded), then count a fixed number of iterations, so JIT tier-up lands before the counted window.

## Browsers

Chromium has no instruction counter, so count what the renderer does:

| Measure | How |
|---|---|
| V8 call counts | CDP `Profiler.startPreciseCoverage` as above, through Puppeteer or Playwright |
| React commits per interaction | a `Profiler` `onRender` counter, or the DevTools hook's `onCommitFiberRoot` |
| Layout and style recalculation counts | CDP `Performance.getMetrics` (`LayoutCount`, `RecalcStyleCount`) before and after |
| DOM mutations | a `MutationObserver` on `document` counting records |
| Layout shifts by region | the Layout Instability API, attributing each shift to a named region and a phase (before first paint, after typeable); the guarantee is zero shifts in a named region |
| Frame budget | `requestAnimationFrame` timestamps against a fixed budget (16.67ms at 60Hz, 8.33ms at 120Hz); count frames over budget, and pin the refresh rate with DevTools begin-frame control |

## Proving a measure

A measure is shipped when one change moved it and the field signal moved the same way. Record the pair with the measure:

```
message-tree assembly: instructions -48%  ->  wall clock -78%
status-line scanner:   instructions -31%  ->  wall clock -44%
```

A count that falls while the field holds still is measuring something users do not wait on. Unship it, name it in the unshipped list, and pick another row.

## Shape of a checked-in baseline

One file per lab, one row per journey stage, the measure's name and the count, and the commit it was measured at:

```json
{
  "measured_at": "6d1dcd6ab",
  "node": "24.18.1",
  "journeys": {
    "chat completion, non-stream": { "calls": 18234, "wall_ms_median": 0.41 },
    "chat completion, stream":     { "calls": 41207, "wall_ms_median": 2.9 }
  }
}
```

Wall clock rides along as a correlate for the reader and is never the gate.
