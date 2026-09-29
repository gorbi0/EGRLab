---
name: egrlab-codex-toolchains
description: "Gdzie Astra (Codex) trzyma toolchainy i buildy EGRLab na laptopie (~11 GB poza repo); dysk C: był pełny 25.09.2026"
metadata:
  node_type: memory
  type: reference
  originSessionId: 3865af86-b552-4ae8-8505-576f94f56226
  modified: 2026-09-25T06:36:41.093Z
---

Toolchainy EGRLab przygotowane przez Astrę (Codex) leżą poza repo, w `C:\Users\tgorbacz\.codex\.chatgpt-projects\g-p-6a8827e57cc881919b26f761377a7bd3\.egrlab-toolchains`: ESP-IDF, zainstalowane toolchainy xtensa/riscv w `tools\tools`, pobrane archiwa w `tools\dist`, przenośny KiCad 10.0.6 w `kicad\runtime` (obok jego instalatora) i Freerouting. Buildy firmware dla kolejnych wersji to `.b4`, `.b41`, `.b5`, `.b6` i `.b61` w tym samym katalogu projektu. Każdy ma 0,5–0,7 GB i konfiguracje core/logger/minimal/test/wifi. Całość zajmuje ~11 GB i powstała 22–23.09.2026.

25.09.2026 na dysku C: zostało 0,6 GB wolnego z 474 GB, a 23–24.09 w dzienniku są błędy „opóźniony zapis nie powiódł się”. Przed ciężkimi buildami lub eksportami KiCad trzeba sprawdzić wolne miejsce (później 25.09: ~78 GB wolne).

Odbiór PCB P01 R3/R3.1 (`src/run_release.py`, Python KiCad) potrzebuje runtime'u Codexa: `--docs-python C:/Users/tgorbacz/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe` (reportlab 4.4.9), `--node .../dependencies/node/bin/node.exe`, `--sharp-module .../dependencies/node/node_modules/sharp`; pdftoppm bierze z `.../dependencies/native/poppler`. Pełny przebieg z `--rebuild` ~10 min. Powiązane: [[kicad-pipeline-quirks]], [[user-pcb-background]], [[claude-msix-appdata-view]].
