# Kontrola plików P02-R3

26.09.2026 · Claude. KiCad 10.0.6. Status: **projekt zamknięty (rewizja zamykająca po recenzji R2)**. Sprzęt, przymiarka i odbiór elektryczny: **NIE ZBADANO**. Zmiany względem R2: `docs/ZMIANY-R3.md`.

| Kontrola | Wynik i dowód |
|---|---|
| ERC, wszystkie ważności | 0, cztery arkusze A3; `erc.json` |
| Netlista vs jawny kontrakt części | 208/208 pinów, 74 części, 47 sieci; `schematic-check.json` |
| DRC, wszystkie ważności | 0 naruszeń / 0 niepołączonych / 0 błędów zgodności ze schematem; `drc.json` |
| Kontrole gotowej PCB | 29/29; `pcb-checks.json` |
| Kontrole elektryczne | 11/11 (R2: 8 + R3: bezpieczniki, prąd LED, zgaśnięcie LED po przerwaniu F1); `electrical-checks.json` |
| Zakres zmian R2 → R3 | 8/8: te same części, brak zmian pinów, wartości i MPN tylko F2/F3/F4/R16, identyczne footprinty, pozycje, połączenia z wylewką, miedź (każda ścieżka i przelotka), strefy; zmienione wyłącznie napisy T1A/T1A/T500mA i linia tytułowa; `revision-checks.json` |
| Próby ujemne na rzeczywistej PCB | 10/10 wykryte; `negative-controls.json` |
| Próby ujemne na netliście/wartościach | 8/8 wykryte (R3: szybki F2, R16 1 kΩ, bleeder 47 kΩ); `electrical-negative-controls.json` |
| Kontrola wzrokowa | Wszystkie 9 stron końcowych PDF; `visual-review.json` z SHA256 |

## Odtwarzanie

`python src/run_release.py --rebuild` przebudowuje schemat i PCB z `routing/P02.ses` (w R3 dołączony do pakietu). Zagłodzone termiki (U5.9, U5.12) są wybierane po UUID z raportu DRC, więc wynik nie zależy od języka interfejsu KiCada. W R2 przebudowa na polskim KiCadzie zostawiała te pady z termikami i świeży DRC zgłaszał 2 naruszenia. Kontrola zakresu R2 → R3 porównuje przebudowaną płytkę z zamrożoną `reference/R2.kicad_pcb`.

## Model elektryczny

Bez zmian względem R2 (`check_electrical.py`, 1024 narożniki na tor; obwiednie odtworzone niezależnie w recenzji `Plytki/P02-R2-recenzja/skrypty/progi_hold.py`).

| Wielkość | Wynik modelu |
|---|---|
| Bank: próg załączenia / wyłączenia | 9,805…10,474 V / 9,612…10,252 V |
| VPROT: próg załączenia / wyłączenia | 11,810…12,623 V / 11,573…12,349 V |
| Podtrzymanie: Cmin, start 9,5 V, przyjęte straty | 85,4 ms |
| Prąd LED1 (R16 470 Ω) | 1,69…3,22 mA |
| Przerwany F1: zgaśnięcie LED od 13,5 V, C +20 %, najniższy próg | ≤ 113 s |
| Zwarcie TP3 przy 32 V, najgorszy R20 | 33,9 mA / 1,09 W |

Nie wykonano symulacji SPICE ani pomiarów dynamiki. Ręczna kwalifikacja 15 s wymaga wcześniejszego odbioru banku; przy zgaszonym silniku — pomiar TP1/TP3 (`HOLD-ANALIZA.md`).

## Otwarte przed zamówieniem i odbiorem

Przymiarka 1:1: złącza, oprawki, adapter, bank, obejmy, osłona lutów, blacha R17. Zakup: 0001.2501 poza katalogiem TME, Mini-Fit 39-29-6048 — TME 0 szt. (26.09). I²t F1:F2 z karty PDF Schurtera. Elektryka według `ODBIOR.md`. Gerbery po przymiarce. Te pozycje nie mają wyniku PASS.
