#!/usr/bin/env bash
# verify-city doctor: run every feature harness's read-only `doctor` and prefix its lines.
# Exit 0 and print `verify-city: clean` only when every feature is clean; exit 1 otherwise.
# Usage: doctor.sh [--city DIR] [feature...]   (default: all features; ~1-2 min, orders reads 24h history)
set -uo pipefail
here=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
city=()
if [ "${1:-}" = "--city" ]; then city=(--city "$2"); shift 2; fi
declare -A H=([merge-wall]=merge_wall.py [quota-routing]=quota_routing.py [resource-guard]=resource_guard_check.py
              [orders]=orders_check.py [host-release]=host_release.py [gc-promotion]=gc_promotion.py
              [observability]=observability.py)
features=("$@"); [ ${#features[@]} -gt 0 ] || features=(merge-wall quota-routing resource-guard orders host-release gc-promotion observability)
rc=0
for f in "${features[@]}"; do
  s=${H[$f]:-}; [ -n "$s" ] || { echo "$f: unknown feature"; rc=1; continue; }
  out=$(timeout 300 python3 "$here/$s" "${city[@]}" doctor 2>&1); r=$?
  if [ $r -ne 0 ]; then rc=1; printf '%s\n' "$out" | sed "s/^/$f: /"; fi
done
[ $rc -eq 0 ] && echo "verify-city: clean"
exit $rc
