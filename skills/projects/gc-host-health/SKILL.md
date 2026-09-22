---
name: gc-host-health
description: Diagnose CPU and swap health on a Gas City host — runaway child processes, stale swap, swappiness tuning, and agent memory footprint. Use when load average is elevated, when swap is high with free RAM, when a formula-spawned child outlives its session, or when a host needs a resource audit before scaling agents.
---

# Host health: CPU, swap, and agent footprint

`gc doctor` checks the **city**; this skill checks the **host**. A healthy city on a
thrashing host still loses work to OOM kills and swap latency. Measure the host before
blaming the store.

## 1. Measure the three resource axes

```
uptime                              # load average vs $(nproc) cores
free -h                             # RAM vs swap; available vs free
cat /proc/pressure/cpu              # PSI: avg10/avg60/avg300
cat /proc/pressure/memory
cat /proc/pressure/io
```

| Axis | Healthy | Degraded |
|---|---|---|
| Load avg (1m) | < core count | > 1.5× core count for 15m+ |
| Memory PSI (some, avg60) | < 1.0 | > 5.0 |
| Swap used | < 10% of total | > 25% with free RAM available |
| I/O PSI (full, avg300) | < 1.0 | > 5.0 |

Complete when all four axes carry a measured value.

## 2. Identify CPU-dominant processes

```
top -bn1 -o %CPU | head -25
```

### Runaway child processes

Formula runs in Gas City spawn child processes (`workerd`, `node`, `python`, `dolt`,
`wrangler`) that should terminate with their parent session. When the formula exits
without killing its children, the child spins forever — measured 2026-09-13: a `workerd`
process from a completed Gateway-LLM review burned 100% of a core for 10+ hours with zero
active connections and near-zero I/O.

Identify a runaway by three signals together:

| Signal | How to check |
|---|---|
| High CPU time ≈ elapsed time | `ps -p <pid> -o etime,cputime,%cpu` — CPU time near wall-clock time means constant burn |
| Zero active connections | `ss -tn state established '( dport = :<port> )'` — listen ports have no clients |
| Near-zero I/O | `cat /proc/<pid>/io` — `syscw` near 0, `write_bytes` = 0 |

Trace the parent chain to confirm it's orphaned:

```
pstree -slap <pid> | head -10
cat /proc/<pid>/environ 2>/dev/null | tr '\0' '\n' | grep -iE 'GC_CITY|GC_ALIAS|HOME'
```

A `GC_ALIAS` value naming a dead session confirms the child is orphaned.

The quiet sibling of the runaway is the **idle orphan**: PPID 1, near-zero CPU and RSS, days
old, such as `codex-linux-sandbox` helpers whose `--command-cwd` names a worktree that no
longer exists (two found 2026-09-22 after `gc stop`). They cost nothing but hold a dead
worktree path; `kill <pid>` and move on.

**Kill policy**: `kill <pid>` first (SIGTERM). If still running after 5 seconds, `kill -9 <pid>`
(SIGKILL) — measured 2026-09-13: workerd ignored SIGTERM and required SIGKILL. Verify:

```
ps -p <pid> -o pid,comm 2>/dev/null || echo "confirmed dead"
```

Complete when every process above 20% CPU is either justified (active agent, dolt serving
queries, this session) or killed.

## 3. Diagnose swap

Swap on a GC host is typically **stale** — pages pushed during a past memory peak that were
never pulled back because nothing accessed them.

### Measure per-process swap

```
for pid in $(ls /proc/ | grep -E '^[0-9]+$'); do
  swap=$(awk '/VmSwap/{print $2}' /proc/$pid/status 2>/dev/null)
  if [ "${swap:-0}" -gt 1000 ]; then
    name=$(cat /proc/$pid/comm 2>/dev/null)
    etime=$(ps -p $pid -o etime= 2>/dev/null | tr -d ' ')
    echo "${swap} ${pid} ${etime} ${name}"
  fi
done 2>/dev/null | sort -rn | head -20 | awk '{printf "%8.1f MB | PID %-8s | %-14s | %s\n", $1/1024, $2, $3, $4}'
```

### Confirm swap is stale

Stale swap has three signals together:

| Signal | Check |
|---|---|
| Swap used > 1 GB | `free -h` — SwapUsed column |
| Free RAM > swap used | `free -h` — MemAvailable >> SwapUsed |
| Memory PSI = 0 | `cat /proc/pressure/memory` — avg10/avg60/avg300 all 0.00 |

All three true means the system can absorb the swap contents into RAM right now.

### Flush stale swap

```
sudo swapoff -a && sudo swapon -a
```

This pulls all swapped pages back to RAM and clears the swap. Only run when free RAM
exceeds swap used. Verify:

```
free -h    # swap used should be near 0
```

### Tune swappiness

Default `vm.swappiness=60` causes the kernel to proactively swap idle pages even with
gigabytes of free RAM. On a GC host running AI agents with irregular access patterns,
swapped pages cause latency spikes when the agent resumes.

```
sysctl vm.swappiness                                        # read current
sudo sysctl vm.swappiness=10                                # set immediately
echo 'vm.swappiness=10' | sudo tee /etc/sysctl.d/99-swappiness.conf   # persist across reboot
```

`swappiness=10` means swap only under real memory pressure. Verified 2026-09-13: a GC host
with 31 GB RAM, 14 GB free, and 4.1 GB stale swap was running at `swappiness=60` — lowering
to 10 prevents recurrence.

Complete when swap is flushed, swappiness is set and persisted, and `free -h` confirms
near-zero swap.

## 4. Audit agent memory footprint

```
echo "Claude sessions:"
ps aux | grep '[c]laude' | grep -v 'bash\|grep' | awk '{sum+=$6; n++} END {printf "%d sessions, %.0f MB total RSS\n", n, sum/1024}'
echo "Codex sessions:"
ps aux | grep '[c]odex' | grep -v 'bash\|grep\|host' | awk '{sum+=$6; n++} END {printf "%d sessions, %.0f MB total RSS\n", n, sum/1024}'
echo "Opencode sessions:"
ps aux | grep '[o]pencode' | grep -v 'bash\|grep' | awk '{sum+=$6; n++} END {printf "%d sessions, %.0f MB total RSS\n", n, sum/1024}'
```

Budget per agent type — measured 2026-09-13:

| Agent | RSS per session | Notes |
|---|---|---|
| Claude | 250–330 MB | Grows with context window fill |
| Codex | 210–230 MB | Plus ~10 MB codex-code-mode-host child |
| Opencode | 850–900 MB | DeepSeek flash; largest single footprint |
| Dolt server | 300–400 MB | Shared across all rigs |
| bd.dog | 150–300 MB | Spikes during list/show |

At 9 concurrent agents, expect **3–4 GB RSS** for agents alone, plus dolt and bd overhead.
A 32 GB host can sustain this; a 16 GB host cannot without swap.

## 5. Check for zombie processes

```
ps aux | awk '$8 ~ /Z/ {print}'
```

A zombie is a terminated child whose parent hasn't called `wait()`. One or two zombies are
harmless; dozens indicate a parent leaking children. The parent PID is in column 3 of
`/proc/<zombie-pid>/status` (`PPid`).

Complete when every zombie is accounted for and either harmless or its parent is
identified.

## 6. Report

State the four axes from step 1 with before and after values where an action was taken.
Cross-reference with [`gc-store-reclaim`](../gc-store-reclaim/SKILL.md) when the host audit
accompanies a store reclaim — the store's `Live rows: 0` blind guard is a host-visible
symptom (dolt health probe timeout) not a store-visible one.

Complete when all four axes carry a measured value and every action taken has a before/after
pair.
