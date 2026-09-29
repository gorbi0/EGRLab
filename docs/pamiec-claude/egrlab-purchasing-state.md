---
name: egrlab-purchasing-state
description: What the user owns / has ordered for EGRLab (Zamowione/ register, 24.09) and the unordered list 2 of 28.09 (Plytki/Zakupy-2) with its open items
metadata:
  node_type: memory
  type: project
  originSessionId: 1bdb3685-394a-4886-bbc7-14b9957d5ea4
  modified: 2026-09-28T13:37:42.752Z
---

Stan na 2026-09-24 (TME, Mouser, Kamami):
- **Rejestr zamówionych części:** `EGRLab/Zamowione/ZAMOWIONE.md` i `zamowione.csv` (dostawca, symbol, szt., moduł, pozycje, BOM, zapas). W środku pola CSV nie używać średnika, tylko `|` albo przecinka. Użytkownik chce, żeby każde zamówienie było tam dopisane po jego złożeniu. Tabela „Stan kompletacji” pokazuje, co jeszcze brakuje per moduł.
- **Użytkownik już ma** moduł ESP32-S3 (P03 M1), AD7606B (P05) i 2× MAX31856 „XU” z Allegro (P09, wg `P09-R1-review/docs/MODUL-KWALIFIKACJA.md`; w ZAMOWIONE.md wciąż jako brak). Nie dodawać ich do list zakupowych.
- **TME / Mouser / Kamami 24.09:** P01 kompletne; Mouser: TSR ×2, MCP120-300 ×4, MCP120-450 ×3, 74HC08 ×8, 74LVC125AD ×25, MCP23017, HC139 ×1, TPS3808 ×2 + PA0085, INA240/MCP3201 ×2, MCP6022, MCP1525, MCP1702; Kamami: adaptery SO14 ×18 (po R1 potrzeba już tylko 11 — P05/P06/P08–P10 lutują SOIC wprost), SOIC8 ×2, SOT23 ×2, goldpin 1×40 ×9, DIP14 ×10, DIP16 ×2, DIP-8P ×2, 1N4148 ×10.
- **Lista 2 (28.09, NIEZAMÓWIONA):** `Plytki/Zakupy-2/` — ZAKUPY-2.md, TME-wklej.txt (106 poz., ok. 855 zł netto), TME-przewody-wklej.txt (szpule, 347 zł — do decyzji), Kamami (7 poz., 42 zł brutto), FARNELL-wklej.txt (9 poz., 247 zł), MOUSER-wklej.txt (20 poz., 344 zł, wszystko na stanie), generator `src/gen.py` (kontrola pokrycia każdej pozycji BOM). Oparta na P03-R5 i P04-R2.2 (U4 SN74LVC1G37, R17 10k) i wartościach P05 z recenzji.
- **Zamiany 1:1 bez zmiany PCB (28.09, wpisać w kolejne rewizje płytek):** P05 U2 ADR4525BRZ (nigdzie na stanie, DigiKey 33 tyg.) → REF5025AIDR (Mouser 595-REF5025AIDR; ten sam pinout SOIC-8, zasila tylko okno DAQ_OK); P03-R5 U4 SN74LVC1G37DBVR → DBVRQ1; P06 R3/R4 5k1 0,1 % → YR1B5K11CC (dzielnik 1:2); P11 J7 39-29-9129 → 39-29-6128 (Au bez kołków). Do decyzji: PBV-R005-F1-0.5 (tylko DigiKey 163,30 zł), EAO (panel, poza PCB). Użytkownik 28.09: boi się części z dostępnością Q1 2027 — reguła: co nie jest do kupienia w 2–3 tygodnie, zastąpić; PCB z fabrykapcb.pl przychodzą po 2 dniach; wylot do Alicante 23.10.2026.

**Why:** użytkownik minimalizuje liczbę dostawców i koszty wysyłki (Mouser od 300 zł bez opłaty, Farnell od 200 zł). Sam decyduje o kosztach.
**How to apply:** przed kolejną listą sprawdź `Zamowione/` i `Plytki/Zakupy-2/`; po zamówieniu listy 2 dopisz ją do rejestru. Przy zmianie rewizji płytki regeneruj listę przez `src/gen.py` (dane w items*.py/tme.py/other.py). P07 wstrzymany. Zob. [[tme-mouser-lookup]], [[p00-r1-state]] (korekta wiązki P00), [[egrlab-review-rules]].
