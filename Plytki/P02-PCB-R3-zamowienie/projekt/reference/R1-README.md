# P02 PSU + HOLD — schemat i PCB R1 do recenzji

25.09.2026 · Claude (schemat i layout). Recenzja: Astra. Stan: **pliki do recenzji; sprzęt, przymiarka 1:1 i odbiór elektryczny NIE ZBADANE.**

P02 to zasilacz EGRLab z v6.1-rc1 (przetwornice 5V_SYS i 3V3_IO, rozdział LV03–LV10, VSENSE, VMOTOR, nadzór szyn PSU_OK) rozszerzony o obwód podtrzymania HOLD C1: bank 3 × 22 mF / 35 V, diody D_OR/D_CHARGE, R_CHARGE poza płytką, oraz lokalny wskaźnik gotowości rezerwy HOLD_READY. Decyzje użytkownika z 25.09: bank na tej płytce; HOLD_READY tylko lokalnie (LED, pole pomiarowe, zarezerwowany pin 3 w PSUOK), bez zmian w P03/P04.

## Wynik kontroli

| Kontrola | Wynik |
|---|---|
| ERC / netlista pin po pinie | 0 / 200 z 200 zgodnych |
| DRC: naruszenia / niepołączone / zgodność ze schematem | 0 / 0 / 0 |
| Kontrole gotowej PCB | 28/28 |
| Próby ujemne | 8/8 wykryte |

Szczegóły: `verification/QA.md`.

## Co przejrzeć najpierw

1. **Decyzje sporne** w `docs/ZALOZENIA-P02-R1.md` (kwalifikacja 15 s w firmware, GMSTBA zamiast PC 4, TP3 na stronie banku bez bezpiecznika, brak przelotek zszywających).
2. **Tor HOLD**: D1 z osobnymi anodami, F1 przy banku (24 mm do C1+), szyna HOLD_STORE, dzielnik banku przy źródle (`docs/LAYOUT.md`).
3. **Tor 5 A**: strefa VPROT J1 ↔ J2 i powrót w płaszczyźnie B.Cu z korytarzem bez ścieżek.
4. **Komparator HOLD_READY**: progi 9,50/9,08 V i 11,60/11,07 V, zasilanie LM2903 z 5V_SYS przy wejściach do 32 V (schemat, arkusz MON).
5. **Montaż i mechanika**: wysokość banku 45 mm, kotwy wiązek, R_CHARGE na blasze (`docs/MECHANIKA.md`).

## Pliki

| Ścieżka | Zawartość |
|---|---|
| `eda/` | projekt KiCad 10: `P02.kicad_sch` + `MON.kicad_sch`, `P02.kicad_pcb`, biblioteki lokalne |
| `output/pdf/P02-R1-schemat.pdf` | schemat, 2 arkusze A3 |
| `output/pdf/P02-R1-PCB.pdf` | podsumowanie, montaż 1:1, F.Cu 1:1, B.Cu 1:1 (druk 100 %, belka 100 mm) |
| `output/previews/` | rendery 3D i podglądy stron |
| `docs/ZALOZENIA-P02-R1.md` | karta założeń, decyzje, zmiany w trakcie projektu |
| `docs/LAYOUT.md`, `docs/MECHANIKA.md` | opis layoutu z liczbami; mechanika, montaż, serwis banku |
| `docs/BOM.csv`, `docs/parts.json` | BOM nominalny z uwagami; lista części ze źródłem w BOM v6.1 lub HOLD C1 |
| `docs/ZAKUPY-P02.md` | co jest już kupione (rejestr 24.09), co pokrywa zapas P01, czego brak |
| `reference/` | wejścia: import pinowy P02 z v6.1, obwód i kontrakt HOLD C1, źródła |
| `routing/` | DSN, zapisany wynik routera (`P02.ses`), płytka przed routingiem, DRC etapów |
| `src/` | skrypty (schemat, płytka, trasy, nadruk, kontrole, PDF); `run_release.py` odtwarza całość |
| `verification/` | ERC, netlista, DRC z proweniencją, kontrole, próby ujemne, rozmieszczenie nadruku |

## Odtworzenie

Pythonem z KiCada 10 (moduł `pcbnew`), z katalogu pakietu:

```
python src/run_release.py
```

Importuje zapisany wynik routera, więc daje tę samą geometrię płytki; `--new-route` uruchamia Freerouting od nowa (wynik za każdym razem nieco inny). Ścieżki do Freeroutinga i `pdftoppm` są w `src/run_layout.py` i `src/run_release.py` (zmienne `EGRLAB_FREEROUTING`, `PDFTOPPM`).

## Poza zakresem R1

Firmware CORE (kwalifikacja 15 s, odczyt HOLD_READY), podłączenie HOLD_READY w P03/P04, dobór wkładek DC i dokładnych MPN Mini-Fit, blacha R_CHARGE, osłona lutów banku, obudowa. Odbiór obwodu HOLD według `reference/PROJEKT.md` (Ceff, spadek, 50 ms przy 6 W, zwarcia) dopiero na zmontowanej płytce.
