#!/usr/bin/env bash
# Tylko na Windows, po każdym merge/pull/reset/checkout: przywraca do indeksu pliki o nazwach
# zarezerwowanych (AUX, CON, ...), które git for Windows pomija przy rozpakowywaniu drzewa
# (core.protectNTFS), i oznacza je skip-worktree. Bez tego następny commit usunąłby je z repozytorium.
# Zob. docs/CHMURA.md, sekcja „Nazwy plików zarezerwowane w Windows”.
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"
git ls-tree -r HEAD | grep -iE $'\t(.*/)?(AUX|CON|PRN|NUL|COM[1-9]|LPT[1-9])(\\.[^/]*)?$' |
while IFS=$'\t' read -r meta path; do
  set -- $meta   # tryb, typ, skrót
  git -c core.protectNTFS=false update-index --add --cacheinfo "$1,$3,$path"
  git -c core.protectNTFS=false update-index --skip-worktree -- "$path"
done
echo "plików skip-worktree: $(git ls-files -v | grep -c '^S' || true)"
if git diff --cached --quiet HEAD --; then
  echo "indeks = HEAD"
else
  echo "UWAGA: indeks różni się od HEAD — sprawdź przed commitem: git diff --cached --name-status HEAD"
fi
