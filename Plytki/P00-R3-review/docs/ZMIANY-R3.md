# P00-R3 — zmiany względem R2 (rewizja zamykająca)

27.09.2026 · Claude. Podstawa: R2 Astry (`Plytki/P00-R2-review`, bez zmian) i moja recenzja `Plytki/P00-R2-recenzja/RECENZJA-P00-R2.md` (kopia w `reference/RECENZJA-P00-R2.md`).

**Miedź, rozmieszczenie, strefy, wartości, MPN i footprinty są identyczne z R2.** Sprawdza to `src/check_revision.py` na zamrożonych `reference/R2.kicad_pcb` i `reference/R2-parts.json`. Kontrola obejmuje każdą ścieżkę i przelotkę, pola wylewek i obrys. Zmieniły się wyłącznie trzy napisy na nadruku.

| Uwaga recenzji | Zmiana w R3 | Gdzie |
|---|---|---|
| P0-01 mapa wiązki z P04 v6.1 | `P00-P04-WIAZKA.md` napisany od nowa dla P04-R2.1: piny J1–J8 P04, TP1 P04 jako źródło gałęzi, pięć gałęzi 1 kΩ, wybierak HB, styki STOP/ARM/SAFE_N, lista „tylko pomiar” i przypisanie do prób E03–E21. Nowa kontrola `check_harness.py` na zamrożonej netliście P04-R2.1 (sieć, pulldown, rodzaj wejścia, poziom H, zgodność tabel dokumentu) | `docs/`, `src/check_harness.py`, `requirements/harness-P04-R2.1.json`, `reference/P04-R2.1-*` |
| P0-02 wyposażenie wiązki | Pięć rezystorów 1 kΩ, cztery zworki, wybierak HB, trzy styki i złącza współpracujące z P04 | `ZAKUPY-P00.md` |
| P0-03 bilans cieplny | Kontrola wiąże budżet 65 mA z maksimum policzonym z netlisty (57,1 mA). Planem B jest 12 V, bo radiator na tabie U2 koliduje z C5/C7 | `verify_electrical.py`, `ZALOZENIA`, `ODBIOR`, `LAYOUT.md` |
| P0-04 poziom H heartbeat | Kontrola dla typowego wyjścia TLC555 (≥ 2,4 V na wejściu P04); narożnik minimalnego VOH jest raportowany. W ODBIOR pomiar na J9 z 10 kΩ przed P04 i środek zaradczy | `verify_electrical.py`, `requirements/electrical.json`, `ODBIOR`, uwaga RL9 |
| P0-05 próby ujemne | Kopie dostają tabelę bibliotek, więc ich DRC jest czysty, dopóki nie zepsuje go sama wada. Próba zerowa musi przejść 25/25 przy czystym DRC. Nowa mutacja: napis +VIN przy TP3 | `negative_controls.py` |
| P0-06 język KiCada | Zagłodzone termiki rozpoznawane po UUID z raportu DRC | `run_layout.py` |
| P0-07 napis +VIN przy TP3 | „+VIN 6-15V” pod J10, pole TP3 opisane „ZA D1”. Kontrola: najbliższym polem napisu +VIN jest J10.1, a napisu ZA D1 — TP3 | `silkscreen.py`, `verify_pcb.py` |
| P0-08 opisy | Uwagi R6 (tolerancja nieistotna), RL9 i TP3; docstring `cleanup.py`; R05 w `ZAMKNIECIE-RECENZJI.md`; w ODBIOR numery prób P04-R2.1 | `parts.py`, `docs/` |

Poza tym zmieniły się tytuły (P00-R3), linia tytułowa PCB („PCB R3”) oraz nazwy PDF i archiwum. Nazwy plików `ZALOZENIA-P00-R2.md` i `ODBIOR-P00-R2.md` oraz skryptów zostały bez zmian; ich treść jest już z R3.

## Czego nie zmieniano

Miedź, rozmieszczenie, wartości, MPN i footprinty. RL9 1 kΩ, LED przy ok. 1–1,5 mA, zakres 6–15 V (zalecane 9–12 V), C6 + R6. Gerbery różnią się od R2 wyłącznie warstwą F.Silkscreen.

## Sporne

- **RL9 zostaje 1 kΩ.** Typowo H heartbeat na wejściu P04 wynosi ≥ 2,45 V. Przy minimalnym VOH z karty TLC555 wychodzi 1,87–2,25 V wobec VIH 2,0 V. Nie przyciemniam LED9 zapobiegawczo. Rozstrzyga pomiar na J9, a środek zaradczy jest w ODBIOR.
- **Plan B dla temperatury: 12 V zamiast radiatora.** Tab U2 jest 1,5 mm od obrysu C5/C7, a obliczenie nie wymaga radiatora.

## Wyniki

`verification/QA.md`.
