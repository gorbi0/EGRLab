---
name: pcb-fab-satland
description: "Wytwórnia PCB (28.09.2026): Satland Prototype Gdańsk; fabrykapcb.pl nie; miedź 35 µm na P00–P02 (decyzja: koszt), próba nagrzewania przed P07; paczki P00/P02 na wzór P01, folder Plytki/Zamowienie-Satland"
metadata:
  node_type: memory
  type: project
  originSessionId: 1bdb3685-394a-4886-bbc7-14b9957d5ea4
  modified: 2026-09-28T19:34:22.873Z
---

Użytkownik zamawia PCB w Polsce. **Satland Prototype** (prototypy.com, Gdańsk, biuro@prototypy.com, +48 58 554-07-64): miedź 35/50/70/105 µm; przy 70 µm ścieżka i odstęp od 0,25 mm (przy 35 µm od 0,2); wiertła 0,3–6,4 mm; pierścień od 0,2 mm; HAL lub cyna chemiczna; maska i opis obustronnie; laminat w kalkulatorze 1,5 mm (nie 1,6); terminy STANDARD PLUS 7 d / EXPRESS 5 d / SUPER EXPRESS 3 d / 24 h / 8 h (te dwa po telefonie); paczkomat InPost; test elektryczny nie w kalkulatorze — pytać.

**fabrykapcb.pl (Margol) odrzucona 28.09:** 2 h dotyczy płytek jednostronnych bez opcji; dwustronna z maską i metalizacją to 4–6 dni; przy miedzi > 35 µm zalecają ścieżki ≥ 1 mm i odstępy ≥ 0,5 mm; metalizacja galwaniczna gwarantowana przy pierścieniu ≥ 0,4 mm (P00: 31, P01: 47, P02: 39 pól węższych); wymagają napisu na miedzi. Użytkownik uznał, że wprowadzono go w błąd co do terminu.

Stan 28.09: `Plytki/Zamowienie-Satland/` — ZIP-y P00-R3 (d45254c5…), P01-R3.1 (abca5949…), P02-R3 (5d9e1479…), specyfikacje PL, INSTRUKCJA-SATLAND.md, MAIL-DO-SATLAND.txt. Paczki `Plytki/P00-PCB-R3-zamowienie`, `P02-PCB-R3-zamowienie` zrobione skryptami w ich `src/` (export_production.py — KiCad Python; check_cam.py — własny parser Gerber/Excellon + Pillow, bo gerbonary nie ma; cam_negative_controls.py; write_docs.py; seal_package.py). P00 i P02 bez warstwy B.SilkS (w projekcie pusta — eksport KiCada zawiera wtedy same regiony LPC z odejmowania maski). P01 ma prawdziwy dolny opis.

**Decyzja 28.09 (użytkownik): miedź 35 µm na P00, P01 i P02** — 70 µm kosztuje ok. 4× więcej; Gerbery bez zmian. IPC-2221 przy 5 A: P01 odcinki 2 mm +17 °C (70 µm: +5), BAT_FUSED 3 mm +9 °C; P02 VMOTOR przez wylewkę VPROT. Warunek: próba nagrzewania 0,1/1/3,5/5 A przed pierwszym P07. Zmieniono opisy w paczkach P01 (manifest odświeżony, ZIP abca5949 bez zmian) i P02 (ponownie zamknięta, ZIP 5d9e1479 bez zmian) oraz folder Zamowienie-Satland (dodana sekcja ustawień JLCPCB, wszystko 1 oz).

28.09 (później): dołączona **P04-R2.2** — paczka `Plytki/P04-PCB-R2.2-zamowienie` (ZIP 1f7e9b84…), w folderze Satland: ZIP, SPECYFIKACJA-P04.txt, instrukcja (kolumna P04, uwaga o pierścieniu 0,20 mm przelotek), mail z 4 płytkami i trzecim pytaniem. Użytkownik skłania się do JLCPCB (najtaniej, wysyłka 20–30 $ → więcej płytek naraz); kolejne do JLC: P03/P05 po recenzji P03-R5, P05 R2 i przekroju B2B; P06, P08–P11 po recenzji; P07 HOLD. Skrypty w paczce P04 są nowsze niż w P00/P02 (tolerancja otworów, `.kicad_prl`, pierścień z geometrii) — kolejne płytki pakować kopią z `P04-PCB-R2.2-zamowienie/src/`.

29.09: **P01 i P02 wstrzymane** (zasilanie z ogniw 18650 — [[zasilanie-ogniwa-18650]]); do zamówienia tylko P00 i P04.

30.09: **P02 R4 (format S1) — paczka `Plytki/P02-PCB-R4-zamowienie/`** (ZIP aa7b526b…), skrypty z paczki P04 dostosowane do S1:
obrys z narożnikami R (config `corner_radius_mm`), akceptacja lib_footprint_mismatch tylko dla części z przyciętym nadrukiem
(`lib_mismatch_accept`), teksty z `release_date` i `fab` (JLCPCB: 1,6 mm). W folderze Satland dopisana uwaga: P01-R3.1 i
P02-R3 nie zamawiać. Kolejne płytki S1 pakować kopią z `P02-PCB-R4-zamowienie/src/`.

**Why:** termin 23.10.2026 (wylot do Alicante); koszt 70 µm.
**How to apply:** kolejne płytki (P03, P05…) pakować tymi samymi skryptami (config.json: name, source, revision, board_mm, copper_um, layers, pdf, odbior); sprawdzać pusty dolny opis; laminat 1,5 mm w Satlandzie. Zob. [[egrlab-purchasing-state]], [[p00-r1-state]], [[p02-r1-state]], [[kicad-pipeline-quirks]].
