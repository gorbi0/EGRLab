---
name: p04-r2-state
description: "P04 SAFE R2 (Claude, 26.09.2026) — poprawka R1 Astry wg mojej recenzji R4-01…R4-07; wydane do recenzji, zip 19b388e4; sporne i otwarte punkty"
metadata:
  node_type: memory
  type: project
  originSessionId: 1bdb3685-394a-4886-bbc7-14b9957d5ea4
  modified: 2026-09-28T19:34:18.332Z
---

`Plytki/P04-R2-review` + `P04-R2-review.zip` (sha256 19b388e43d57…, 123 pliki); R1 nietknięte (118/118). ERC 0, 355 pinów, DRC 0/0/0, PCB 26/26, elektryka 22/22, mutacje 14/14 + 11/11, czyste odtworzenie identyczne (odcisk f0fce2a8…). Mapa zmian `docs/ZMIANY-R2.md`.

Schemat: U11 MCP100-300; SAFE_WD = SAFE_OK & WD_Q (U7D) na U3.1/U5.5/U5.13; R38/R39 1k, R40 100R (J7.1 PG_3V3, J8.1 PANEL_3V3); R41/R42 1k (pulldowny R23/R24 po stronie bramek); C18 1n C0G; TP14 SAFE_WD, TP15 Q1_B; ODBIOR E21 (TP15 do GND) i E22 (prądy zwarcia).
PCB: grzebień R41/R42/R4 nad J8.3/4/5, R39 między J8 i J7, C18 przy U2.11, R5 pod U2; 55 + 14 przelotek GND; pas „GND ROW J2”.

Sporne (oznaczone w ZMIANY-R2): pas GND ROW J2 (nowa reguła), R40 = 100 Ω, pominięte opcje (R na wyjściach taśm, 10 nF przy R41/R42).
Otwarte: przymiarka Mini-Fit przy grzebieniu; próg MCP100-300 potwierdzić w DS11187F (lokalnie tylko DS11184D MCP120/130); dla C18 K102J15C0GF53H5 w P01 kupiono zamiennik KEMET C320C102J1G5TA — pewnie to samo tu. P03 R2 (powstał równolegle, nie mój) ma nadal R14 = 0 Ω na CORE_LINK.

Stan 26.09 (wieczór): Astra zrecenzowała R2 i wydała `Plytki/P04-R2.1-review` — CAD, wiercenia, nadruk i PDF identyczne z moim R2, poprawione tylko opisy (histereza/reset, zwarcia wyjść HC, E01–E22) + testy wartości/BOM/połączeń; „projekt zamknięty do wykonania prototypu” (start: `docs/ZAMKNIECIE-P04.md`). Następny krok: przymiarka M01, potem Gerber.

Stan 28.09: jest `Plytki/P04-R2.2-review` (R17 100k → 10k pod reset z P03-R5; miedź = R2.1, XOR 0). Paczka zamówieniowa `Plytki/P04-PCB-R2.2-zamowienie`, ZIP 1f7e9b84… (DRC 0/0/0, CAM 20/20, próby 8/8), dołączona do `Plytki/Zamowienie-Satland/`; 101 przelotek z pierścieniem 0,20 mm (minimum Satlandu). Zob. [[pcb-fab-satland]].

**Why:** schemat pracy Claude ↔ Astra; P04 jest zamknięte — bez nowej iteracji, chyba że pojawi się konkretna niezgodność.
**How to apply:** przy odpowiedzi na recenzję bronić liczbami z `verification/*.json`; nowe trasowanie = nowa recenzja layoutu. Zob. [[p04-r1-review]], [[kicad-pipeline-quirks]].
