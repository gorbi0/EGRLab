# Odbiór plików P03-R3

27.09.2026 · Claude. KiCad 10.0.6. **Rewizja zamykająca po końcowej recenzji R2; miedź = R2.** Sprzęt, przekrój B2B i przymiarka: **NIE ZBADANO**. Zmiany: `docs/ZMIANY-R3.md`.

| Kontrola | Wynik | Dowód |
|---|---|---|
| ERC, pięć arkuszy A3 | 0 naruszeń | `erc.json` |
| Schemat / lista części / piny | 88 części, 421/421 pinów, 129 sieci | `schematic-check.json`, `P03.xml` |
| Kontrakt v6.1 | 310 pozycji, 8 jawnych zmian, 0 nieoczekiwanych | `v61-compare.json` |
| Kontrole elektryczne netlisty | 51/51 (R2: 48 + szyny zasilania na złączach, CORE_LINK przez 1K, złącza = zamrożone P02-R3/P04-R2.1/P05-R1) | `function-checks.json` |
| Celowe błędy netlisty | 37/37 wykryte właściwą kontrolą (R2: 33 + R14 = 0R, J4.13 na 3V3_CORE, SUP_N na pinie CORE_LINK, zła żyła B2B) | `function-mutations.json` |
| Świeży DRC / niepołączone / różnice ze schematem | 0 / 0 / 0 | `drc.json`, `drc.provenance.json` |
| Kontrole PCB | 29/29 | `pcb-checks.json` |
| Próby ujemne PCB | Próba zerowa: 29/29 i czysty DRC kopii. 15/15 wad wykrytych właściwą kontrolą; `dangling_lock` teraz naprawdę odcina ścieżkę (DRC: `track_dangling`) | `negative-controls.json` |
| Zakres R2 → R3 | 11/11: te same części i piny; wartość i MPN zmienione tylko w R14; identyczne footprinty, pozycje, pady, wiercenia, miedź, strefy, wypełnienia i obrys; na nadruku tylko linia tytułowa; pakiet R2 zgodny z manifestem | `revision-checks.json` |
| Tabele użytkowe | Netlista 421 pinów, interfejsy 88, BOM 88, zakupy 80 części — zgodne z CAD | `table-checks.json` |
| Odtworzenie od zera | PASS: osobny katalog tylko ze źródłami (src, reference, docs, SES, dwa skrypty weryfikacji), pełne `run_release.py`; `rebuild-compare.py`: wszystkie kategorie zgodne, XOR wypełnień F.Cu 0, B.Cu 4,5×10⁻¹⁰ mm² (limit 10⁻⁸); w kopii 29/29, 51/51, 16/16, 37/37, 11/11 | `standalone-rebuild.json` |
| Oględziny PDF | Obie końcowe PDF (5 + 4 strony); SHA256 w raporcie | `visual-review.json` |

## Granice wyniku

Wolne zbocze SUP_N na złączu do P04 jest opisane i do pomiaru (`docs/ZASILANIE-RESET.md`, `docs/ODBIOR.md`). Nie usunięto go, bo wymaga nowego trasowania. Nie wykonano pomiarów spadków napięcia, prądu wstecznego, zboczy SPI i SUP_N, resetu, temperatur ani RF. Nie potwierdzono fizycznego spasowania P03–P05. Brak Gerberów i zatwierdzenia do produkcji. P07 nadal HOLD.

## Ponowne sprawdzenie

1. KiCad Python: `python src/run_release.py`.
2. Obejrzeć wszystkie strony obu PDF i zaktualizować `verification/visual-review.json`.
3. `python src/package_release.py` — manifest i ZIP. Odmawia przy nieaktualnych raportach.
