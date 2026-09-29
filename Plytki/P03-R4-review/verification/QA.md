# Odbiór plików P03-R4

27.09.2026 · Claude. KiCad 10.0.6. **R4: bufor Schmitta U6 (SN74LVC1G17) z R41 i C15 w resecie do P04; poza obszarem przy J4 miedź = R3.** Sprzęt, przekrój B2B i przymiarka: **NIE ZBADANO**. Zmiany: `docs/ZMIANY-R4.md`.

| Kontrola | Wynik | Dowód |
|---|---|---|
| ERC, pięć arkuszy A3 | 0 naruszeń | `erc.json` |
| Schemat / lista części / piny | 91 części, 430/430 pinów, 132 sieci | `schematic-check.json`, `P03.xml` |
| Kontrakt v6.1 | 310 pozycji, 9 jawnych zmian (R3: 8 + J4.15 = SUP_N_OUT), 0 nieoczekiwanych | `v61-compare.json` |
| Kontrole elektryczne netlisty | 53/53 (R3: 51; wspólny reset rozdzielony na MCU/MCP i tor do P04 przez U6 + R41; nowa kontrola C15; złącze P04 z aliasem SUP_N = SUP_N_OUT) | `function-checks.json` |
| Celowe błędy netlisty | 43/43 wykryte właściwą kontrolą (R3: 37 + J4.15 z powrotem na SUP_N ×2, LVC1G14 zamiast LVC1G17, R41 = 0R, U6 z SUP_RAW_N, C15 poza 3V3_CORE) | `function-mutations.json` |
| Świeży DRC / niepołączone / różnice ze schematem | 0 / 0 / 0 | `drc.json`, `drc.provenance.json` |
| Kontrole PCB | 30/30 (R3: 29 + tor U6 → R41 → J4.15: 8,4 / 2,8 / 5,8 mm; C15 2,2 mm od U6.5) | `pcb-checks.json` |
| Próby ujemne PCB | Próba zerowa: 30/30 i czysty DRC kopii. 18/18 wad wykrytych właściwą kontrolą (R3: 15 + U6 daleko od J4, C15 daleko od U6, oznaczenie R41 poza szczeliną) | `negative-controls.json` |
| Zakres R3 → R4 | 13/13: części = R3 + U6/R41/C15; jedyna zmiana pinu J4.15; notatka zmieniona tylko w J4; footprinty R3 identyczne poza siecią J4.15; usunięte dokładnie 3 odcinki R3; 25 nowych elementów zablokowanych, w obszarze 6–31 × 58–84 mm, na sieciach zmiany; 8 odcinków R3 o tej samej geometrii zablokowanych; strefy, obrys i nadruk (poza tytułem) jak w R3; pakiet R3 zgodny z manifestem | `revision-checks.json` |
| Zasiewanie miedzi R3 | 823 elementy z `routing/P03-R3.ses`, 2 przewody zastąpione, 0 sieci kolidujących (1 runda); wynik routera spoza zbioru przetrasowania pominięty (19 elementów artefaktów) | `routing/seed.json`, `ses-import.json` |
| Tabele użytkowe | Netlista 430 pinów, interfejsy 88, BOM 91, zakupy 83 części — zgodne z CAD | `table-checks.json` |
| Odtworzenie od zera | PASS: osobny katalog poza projektem tylko ze źródłami (src, reference, docs, oba SES, dwa skrypty weryfikacji), pełne `run_release.py`; `rebuild-compare.py`: wszystkie kategorie zgodne, XOR wypełnień F.Cu 0, B.Cu 4,5×10⁻¹⁰ mm² (limit 10⁻⁸); 85 plików wejściowych identycznych z wydaniem; w kopii 30/30, 53/53, 19/19, 43/43, 13/13 | `standalone-rebuild.json`, `standalone-run.log` |
| Oględziny PDF | Obie końcowe PDF (5 + 4 strony), obszar zmiany w 300/600 dpi; SHA256 w raporcie | `visual-review.json` |

## Granice wyniku

Zbocze SUP_N_OUT na P04 policzono dla szacowanego obciążenia ok. 20 pF (taśma 150 mm). Limit 10 ns/V obowiązuje do ok. 36 pF, a rozstrzyga pomiar z `docs/ODBIOR.md`. Zmiana layoutu przy J4 czeka na recenzję. Nie wykonano pomiarów spadków napięcia, prądu wstecznego, zboczy SPI i SUP_N_OUT, resetu, temperatur ani RF. Nie potwierdzono fizycznego spasowania P03–P05. Brak Gerberów i zatwierdzenia do produkcji. P07 nadal HOLD.

## Ponowne sprawdzenie

1. KiCad Python: `python src/run_release.py`.
2. Obejrzeć wszystkie strony obu PDF i zaktualizować `verification/visual-review.json`.
3. `python src/package_release.py` — manifest i ZIP. Odmawia przy nieaktualnych raportach.
