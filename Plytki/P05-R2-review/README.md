# P05 DAQ — R2, etap schematu

*29.09.2026. Pakiet na kopii łańcucha `P05-R1-review/src` według `Plytki/P05-R2-specyfikacja/ZADANIE-P05-R2.md` i recenzji `Plytki/P05-R1-recenzja/RECENZJA-P05-R1.md`. Zamknięty pakiet R1 bez zmian.*

**Status: schemat R2 gotowy do recenzji. PCB w tym pakiecie nie ma** — decyzja użytkownika z 29.09: płytki przechodzą na format S1 (`Plytki/Format-S1/`), więc layoutu w obrysie R1 (160 × 120 mm) nie kończono. Niedokończony layout przy U1 jest w `wip-layout-obrys-R1/` wyłącznie jako wzór rozmieszczenia odsprzęgania AD7606B dla layoutu S1. Sprzętu nie zmontowano ani nie zmierzono.

## Zmiany R1 → R2

| Punkt | R1 | R2 | Źródło |
|---|---|---|---|
| R5 (próg dolny DAQ_OK) | 5,90 kΩ | **6,04 kΩ** 0,1 %, 25 ppm/K | P5-02 |
| R7 (próg górny DAQ_OK) | 5,23 kΩ | **5,11 kΩ** 0,1 %, 25 ppm/K | P5-02 |
| Okno nominalne | 4,826–5,165 V | **4,800–5,186 V** | P5-02 |
| Narożniki okna | 4,779–4,874 / 5,118–5,213 V | **4,752–4,849 / 5,137–5,234 V** | `verify_electrical.py` |
| R13 (podciąganie CS po stronie B2B) | 10 kΩ | **47 kΩ** (zasilanie wsteczne 3V3_DAQ 0,30 → 0,07 V) | P5-05 |
| U2 (referencja okna) | ADR4525BRZ | **REF5025IDR** (klasa wysoka 0,05 %, 3 ppm/K); 2 VIN, 4 GND, 6 VOUT, reszta wolna; C24 1 µF bez zmian (REF50xx: 1–50 µF) | lista zakupowa 2 |
| CH7 | VPROT_SENSE | **VBAT_SENSE** (akumulator auta przez P02 R4 J11.1); dzielnik 499k/100k i J5 bez zmian | P02 R4 |
| Arkusze | `AUX.kicad_sch`, `CON.kicad_sch` | **`AUX_IN.kicad_sch`, `ZLACZA.kicad_sch`** (nazwy zarezerwowane w Windows) | `docs/CHMURA.md` |
| Arkusz ADC | kondensatory bez przypisania | opisy „Cx przy U1.nn” | P5-08 |
| `docs/ODBIOR.md` | 5VA 4,90–5,10 V | 5V_SYS 4,93–5,07 V przy 23 °C, nowe progi, 3V3_DAQ ≈ 0,07 V w kroku 7, przekaźniki ≤ 3,9 V i VDS U4.18 ≤ 0,3 V | P5-02/03/05 |
| `docs/INTEGRACJA.md` | — | ≥ 10 ms AVCC/VDRIVE → reset, kalibracja w firmware, budżet pojemności 5V_SYS | P5-07/08 |

Bez zmian (decyzje z zadania): SW1 C&K 7201, bez diody 1N5817 (P5-06, sporne: ryzyko małe, a BOM jest odchudzany), okno bez histerezy (P5-09).

## REF5025: klasa ma znaczenie

Lista zakupowa 2 wpisuje **REF5025AIDR** z parametrami „0,05 %, 3 ppm/K”. Te parametry ma klasa wysoka **REF5025IDR**; AIDR to klasa standardowa (0,1 %, 8 ppm/K). Z budżetem referencji jak dla pozostałych elementów (dokładność + TC × 100 K + 0,02 % po lutowaniu + 0,015 % histereza/starzenie):

| U2 | budżet | dolny narożnik | górny narożnik | reguła 4,75–5,25 V |
|---|---:|---:|---:|---|
| REF5025IDR | 0,115 % | 4,7524 V | 5,2344 V | spełniona |
| REF5025AIDR | 0,215 % | **4,7477 V** | 5,2397 V | **niespełniona** |

`verify_electrical.py` liczy oba warianty; AIDR jest próbą ujemną (wykryta). Karty TI nie udało się pobrać w chmurze (ti.com blokowany przez proxy) — parametry klas pochodzą z opisu produktu u dystrybutorów; do potwierdzenia z kartą przed zakupem.

## Kontrole

`python src/run_schematic.py` (Python KiCada; w chmurze `scripts/egrlab-docker`): schemat, tabele, ERC, netlista, kontrole, PDF.

- ERC **0**, 8 arkuszy; netlista **421/421** pinów zgodnych z `parts.py`, 110 części, 109 sieci.
- Kontrole elektryczne **23/23**, próby ujemne **12/12** (nowe: TEMP REF podłączony, CH7 z powrotem na VPROT, U2 w klasie AIDR).
- Zapas 5VA do narożników przy TSR 2-2450 (`electrical-checks.json`, `window.tsr_margin`): −2 %/25 °C +31,5 mV; −2 %/60 °C −3,5 mV; +2 %/25 °C +49,5 mV; +2 %/60 °C +14,5 mV. Przypadek −2 % w upale zostaje nieosłonięty — stąd kryterium odbioru 5V_SYS 4,93–5,07 V.

## Pliki

- `eda/` — schemat KiCad 10 (8 arkuszy A3) i biblioteki; bez PCB.
- `output/pdf/P05-R2-schemat.pdf`, `output/previews/sch-1-*.png`.
- `docs/` — BOM, zakupy, pinout, PROJEKT, ODBIOR, INTEGRACJA, MECHANIKA (mechanika jak w R1, do przeliczenia w S1).
- `verification/` — ERC, netlista, `schematic-check.json`, `electrical-checks.json`.
- `wip-layout-obrys-R1/` — niedokończony layout, patrz jego README.
