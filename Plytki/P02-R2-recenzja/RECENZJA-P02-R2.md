# P02-R2 — recenzja Claude

Data: 26.09.2026. Oceniany pakiet: `Plytki/P02-R2-review` (R2 Astry, na bazie mojego R1 i recenzji `reference/RECENZJA-P02-R1.md`). Oryginał R2 nie był modyfikowany: kontrole powtarzałem na kopii `work/`, a manifest pakietu (224 pliki) i hash ZIP się zgadzają. Pomiarów sprzętu i przymiarki nie było.

## Werdykt

**R2 przyjmuję. Zamknięcie płytki wymaga jeszcze poprawek bez zmiany miedzi: doboru F2/F3/F4, odtwarzalności pakietu i kilku poprawek w dokumentach.** Wszystkie cztery uwagi z recenzji R1 są wdrożone poprawnie. Progi HOLD_READY odtworzyłem własnym kodem co do miliwolta. Topologia filtru z oddzielnym węzłem sprzężenia usuwa problem R-02, a TP3 za R20 zamyka R-03. Zgodnie z ustaleniem, że po tej iteracji płytka jest zamknięta, poprawki wprowadziłem jako ostatnią rewizję `Plytki/P02-R3-review` (mapa: `docs/ZMIANY-R3.md` w tym pakiecie). Nie jest to nowe trasowanie: ścieżki, przelotki i rozmieszczenie są identyczne z R2.

## Co sprawdziłem niezależnie

| Sprawdzenie | Wynik |
|---|---|
| Manifest wydania R2, ZIP | 224/224 plików zgodnych, hash ZIP zgodny |
| Świeży ERC, eksport netlisty, `verify_schematic.py` | 0 naruszeń na 4 arkuszach; 208/208 pinów, 74 części, 47 sieci |
| `check_electrical.py --negative`, `check_revision.py` | 8/8 i 5/5 mutacji; zakres zmian R1→R2 4/4 |
| `verify_pcb.py` (świeży DRC), `negative_controls.py` | 29/29; 10/10 mutacji wykrytych |
| Własny model progów (`skrypty/progi_hold.py`), wartości z eksportu XML, 1024 narożniki na tor | Bank: wzrost 9,805–10,474 V, spadek 9,612–10,252 V, histereza min. 166 mV. VPROT: 11,810–12,623 V / 11,573–12,349 V, min. 205 mV. Identycznie jak w `HOLD-ANALIZA.md` |
| Przebudowa `--rebuild` na kopii (SES z pakietu) | Geometria identyczna z R2: 76/76 footprintów, 244/244 ścieżki, przelotka, strefy, 47 napisów. Różnica tylko w U5.9/U5.12 (P2-02) |
| Długości węzłów komparatora | BANK_CMP 17,3 mm, VPROT_CMP 21,4 mm; DIV: 81 / 127 mm (górne rezystory przy źródłach — decyzja z R1), filtr 10 nF przy komparatorze |
| Oględziny | 4 arkusze schematu przy 200 dpi, 5 stron PDF PCB; belka zmierzona przy 300 dpi |
| Dane producentów | Schurter SPT 5×20 (strona karty HTML), Molex 39296048 (strona produktu), TRACO TSR2 (`reference/TRACO_TSR2.txt`) |

## Uwagi

| ID | Waga | Gdzie | Ustalenie | Dowód | Propozycja |
|---|---|---|---|---|---|
| **P2-01** | Istotna, przed zakupem | F2, F3, F4 | Wkładki bez MPN; opis „F1A / F100mA DC-rated (select)”. Poza tym **TRACO zaleca przed TSR2 bezpiecznik zwłoczny** (24 Vin: 3,15 A slow blow), a nie szybki | `TRACO_TSR2.txt` w. 54–55. Schurter SPT 5×20: 0,5–3,15 A mają 250 VAC / **300 VDC**, UL 1500 A przy 300 VDC; najmniejszy prąd w serii 0,5 A. SP 5×20 (szybki) i FST 5×20 nie mają parametru DC | F2/F3: **Schurter 0001.2504 (T1A)**. 1 A wystarcza przy budżecie ≤ 6 W: najwyżej ok. 0,86 A przy 7 V. F4: **Schurter 0001.2501 (T0,5A)**. VSENSE niesie ok. 25 µA (P05: R31 499 kΩ), więc bezpiecznik chroni tylko przewód; 100 mA z v6.1 nie ma odpowiednika z parametrem DC w tej serii. F1 zostaje 0001.2507 (T2A). Selektywność F1:F2 = 2:1 w tej samej serii: I²t z karty PDF potwierdzić przy zakupie. TME 26.09: 0001.2504 ok. 6600 szt., 0001.2501 poza katalogiem TME |
| **P2-02** | Średnia, odtwarzalność | `routing/`, `src/run_layout.py` | `--rebuild` z README nie odtwarza płytki. (1) Pakiet nie ma `routing/P02.ses`, jest tylko `P02-normalized.ses`. (2) Zagłodzone termiki są rozpoznawane wyrażeniem `PTH pad (\d+) .* of (\w+)`. Polski KiCad pisze „Pole PTH 9 [GND] na U5”, więc U5.9/U5.12 nie dostają pełnego połączenia i świeży DRC ma 2 naruszenia | Przebudowa w `work/` z podstawionym SES: miedź identyczna, `drc.json`: 2 × `starved_thermal` (U5.9, U5.12); `verify_pcb` 28/29 | Dołączyć SES; zagłodzone pady wybierać po UUID z raportu DRC (niezależnie od języka) |
| P2-03 | Drobna, eksploatacja | U7B, próg VPROT_OK | Próg rosnący 12,25 V nominalnie (obwiednia 11,81–12,62 V) leży w zakresie akumulatora w spoczynku (ok. 12,2–12,7 V; P01 dokłada ok. 0,05–0,1 V na SUP53P06). Przy zgaszonym silniku, czyli w trybie TEST/HOT-SOAK, kontrakt „VPROT ≥ 11,5 V” jest spełniony, a kontrolka zależnie od egzemplarza nie świeci | `skrypty/progi_hold.json`, sekcja `reachability_by_VPROT`: przy 12,4 V świeci egzemplarz nominalny, najgorszy nie | Progów nie zmieniać: gwarantują „LED ⇒ kontrakt”. Dopisać procedurę przy zgaszonym silniku: kwalifikacja ręczna TP1 ≥ 11,6 V i TP3 ≥ 9,7 V przez 15 s (TP3 przez R20 i DMM 10 MΩ: błąd 0,01 %) |
| P2-04 | Drobna, dokumentacja | HOLD-ANALIZA, ODBIOR 12, arkusz HOLD | „Kontrolka nie sprawdza ciągłości F1” / „LED może świecić mimo braku rezerwy”. W rzeczywistości przy przerwanym F1 bank jest odcięty od ładowania i rozładowują go R1 ∥ R6+R7 (τ ≈ 280–330 s), więc **LED gaśnie po ok. 1–2 min**: 55–85 s przy nominalnym C, najdłużej ok. 115 s przy C +20 % i najniższym progu, start z 13,5 V | `progi_hold.json`: `F1_open_LED_off_after_s_*` | Opisać wykrycie z opóźnieniem 1–2 min i wpisać to jako oczekiwany wynik ODBIOR 12; Ceff nadal nie jest sprawdzane |
| P2-05 | Drobna, czytelność | Arkusz 1 schematu | Wartość i oznaczenie D1 leżą na etykiecie VLOG_RES. Etykiety HOLD_STORE i VLOG_RES przecina przewód szyny, bo `cadlib.node()` stawia etykietę globalną na pierwszym węźle poziomej szyny z tekstem wzdłuż przewodu | Rasteryzacja 200 dpi, `work/zoom-d1.png`, `zoom-store.png` | Etykiety globalne na poziomych szynach kierować od szyny; pola D1 na lewo od symbolu |
| P2-06 | Drobna, dokumentacja | `MECHANIKA.md`, `ZAKUPY-P02.md` | Pogubione spacje: „raster10”, „co najmniej3 mm”, „MBB0207VD3012BC100,30,1kΩ0,1%”. Przecinek dziesiętny zlewa się z separatorem | Tekst plików | Przywrócić spacje |
| P2-07 | Drobna, PDF | Belka 100 mm, strony 2–5 | Długość poprawna (99,99 mm przy 300 dpi), ale kolor RGB 205/215/220 i cienka linia — na wydruku może być prawie niewidoczna | `work/scalebar.png` | Czarna, grubsza belka z kreskami końcowymi |
| P2-08 | Sugestia | LED1, R16 | Prąd LED ok. 1,0–1,25 mA (R16 1 kΩ, L-934GD) — kontrolka kwalifikacji słabo widoczna w kabinie | `progi_hold.json` | R16 470 Ω: ok. 2,3–2,7 mA; wyjście U6C obciążone łącznie ok. 2,8 mA |

Informacyjnie: Molex potwierdza 39-29-6048 jako „Vertical Header … 4 Circuits, without Snap-in Plastic Peg PCB Lock, Gold” (5566-04AGS). Zgadza się z footprintem 5566-04A bez otworów na kołki. Dostępność 26.09: TME 0 szt., Mouser 489 szt.

## Zmiany R2 — ocena

| Uwaga R1 | Wykonanie w R2 | Ocena |
|---|---|---|
| R-01 progi HOLD_READY | Rt/Rb 0,1 %, obwiednia 1024 narożników | Poprawne; najniższy próg wyłączenia banku 9,612 V ≥ 9,5 V, VPROT 11,573 V ≥ 11,5 V. Podtrzymanie od 9,612 V: 93 ms (od 9,5 V: 85 ms) |
| R-02 kondensator w węźle sprzężenia | C14/C15 10 nF na DIV, R18/R19 10 kΩ, sprzężenie na CMP | Poprawne; skok regeneracji ≥ 23 mV bez RC, filtr τ ≈ 75–79 µs |
| R-03 TP3 na surowym banku | R20 1 kΩ / 2 W przy banku, TP3 za nim | Poprawne; zwarcie TP3 przy 32 V ok. 34 mA |
| R-04 czytelność schematu | Cztery arkusze A3 | Duża poprawa; zostały dwie kolizje na arkuszu 1 (P2-05) |
| Budżet, energia, bleeder | 33,79 / 40,55 J; do 1 V ok. 21,7 min | Zgodne z moim rachunkiem (z dzielnikiem 19,3 min — wartość w dokumencie jest ostrożniejsza) |

## Czego nie da się rozstrzygnąć bez sprzętu

Stabilność komparatorów przy wolnych rampach i zakłóceniach silnika, rzeczywisty spadek bank → VLOG_RES (limit 1,2 V), Ceff/ESR, czas 50 ms przy 6 W, temperatury R17/D1/D2, przymiarka złączy i obejm banku. Formularz `verification/ODBIOR.md` to obejmuje.

## Mocne strony R2

- Pełna obwiednia tolerancji z jawnie podanymi założeniami, liczona z eksportu netlisty, nie z generatora.
- Filtr i sprzężenie rozdzielone jednym rezystorem, bez zmiany koncepcji nadzoru.
- Próby ujemne rzeczywiście trafiają w nowe elementy (surowy TP3, ominięty rezystor separujący, kondensator na węźle sprzężenia).
- Uczciwie opisane granice: brak Gerberów, F2/F3/F4 jawnie otwarte zamiast wymyślonych MPN.

## Dowody

`skrypty/progi_hold.py` + `.json` (niezależny model), `skrypty/porownaj_plytki.py` (porównanie geometrii), `skrypty/rebuild-r2.log`, `work/` (kopia robocza z przebudową i raportami), `work-orig/P02.kicad_pcb` (płytka R2 z pakietu do porównania).
