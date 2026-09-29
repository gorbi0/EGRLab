#!/bin/sh
# Punkt wejścia obrazu egrlab-kicad: globalne tablice bibliotek KiCada jak w instalacji na Windows.
# Bez nich DRC kopii płytek (próby ujemne) zgłasza lib_footprint_issues dla każdej biblioteki
# standardowej, nie tylko lokalnej (P02 R3: 72 zamiast 24 zgłoszeń na próbę).
set -e
CFG="${KICAD_CONFIG_HOME:-${HOME:-/tmp}/.config/kicad}/10.0"
mkdir -p "$CFG" 2>/dev/null || true
for t in fp-lib-table sym-lib-table; do
  [ -f "$CFG/$t" ] || cp /usr/share/kicad/template/$t "$CFG/$t" 2>/dev/null || true
done
exec "$@"
