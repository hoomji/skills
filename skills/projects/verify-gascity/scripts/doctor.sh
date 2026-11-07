#!/usr/bin/env bash
# verify-gascity doctor against the live city, read-only (the weekly verify-skill-doctors order runs it).
# Exit 0 and `doctor: clean` when the live gc, its supervisor API and its fork commit agree.
here=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
exec python3 "$here/gascity.py" doctor live
