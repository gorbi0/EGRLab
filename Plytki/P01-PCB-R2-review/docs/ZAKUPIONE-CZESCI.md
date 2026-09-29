# P01 — części zamówione a footprinty PCB R2

Części do P01 zamówiono 24.09.2026 (TME, Mouser). Rejestr: `Zamowione/ZAMOWIONE.md` w katalogu głównym projektu, a uzasadnienia zamienników są w `Plytki/P01-zakupy/ZAKUPY-P01.md`.
**BOM i schemat R3 pozostają bez zmian.** Pola MPN w PCB są polami R3. Poniżej są tylko pozycje, w których zamówiona część różni się od MPN z BOM, oraz sprawdzenie, czy pasuje do footprintu R2 (footprinty R2 = R3).

| Poz. | BOM R3 | Zamówione | Footprint R2 | Zgodność |
|---|---|---|---|---|
| D1 | 15KPA24CA-B | Littelfuse 15KPA24CA (Mouser) | TVS_P600_BIDIR_P20.32 | ten sam typ Littelfuse; różni się tylko sufiks opakowania |
| D3 | 5KP18A-B (Littelfuse) | 5KP18A (Diotec, TME) | TVS_P600_P20.32 | P600, 5 kW, 18 V; raster 20,32 |
| C1 | UPW1J100MDD | Panasonic EEU-EB1J100SH | CP_Radial_D5.0mm_P2.00mm | Ø5 × 11 mm, raster 2 mm |
| C5 | B32529C1103J000 | B32529C1103J289 | C_TDK_B32529_L7.3_W2.5_P5 | ta sama seria, inny kod wyprowadzeń; raster 5 mm |
| C8, C10, C11 | K104K15X7RF53H5 | K104K15X7RF5TH5 | C_Vishay_K15_H5_P5 | ta sama seria, wersja z taśmy |
| C12 | K101J15C0GF53H5 | Murata RDE5C1H101J0M1H03A | C_Vishay_K15_H5_P5 | C0G, raster 5 mm |
| C13 | K102J15C0GF53H5 | KEMET C320C102J1G5TA | C_Vishay_K15_H5_P5 | C0G, raster 5,08 mm (różnica 0,08 mm; nóżki się dogną) |
| R1, R23, R27 | PR02 ±1% | Vishay PR02 ±5% | R_PR02_P17.78 | ten sam korpus; tolerancja bez znaczenia funkcjonalnego |
| R2–R4, R12–R22, R24–R26, R28–R33 | MFR-50 (Yageo) | Yageo MF0207 1% (R29: MF0204) | R_MFR50_H4_P15.24 | 0207/0204 w rastrze 15,24 |
| R5–R7, R9–R11 | TE H4 0,1% 15 ppm | TE YR1B 0,1% 15 ppm | R_MFR50_H4_P15.24 | Ø2,3 × 6,3 mm w rastrze 15,24 |
| **R8** | **220 kΩ** H4 0,1% | **221 kΩ** YR1B 0,1% | R_MFR50_H4_P15.24 | **odchyłka wartości:** YR1B 220k nie był dostępny, zamówiono najbliższe 221k (E96). R8 to sprzężenie histerezy OK → OV_REF przy R7 = 10k. Próg na OV_REF przesuwa się o 0,47 mV (ok. 3 mV na wejściu dzielnika) i to wyrównuje kalibracja RV1. Histereza maleje o 0,4% (ok. 6 mV na wejściu); RV1 jej nie koryguje, ale to pomijalne. Do przyjęcia albo odrzucenia w rewizji schematu |
| Q3, Q5–Q8 | 2N5551G | onsemi 2N5551TA | TO-92_Inline_Wide | wersja z taśmy, nóżki uformowane pod raster 2,54 |
| J3 | Harwin M20-9990245 | listwa 1×2 ZL201-02G + zworka | PinHeader_1x02_P2.54mm_Vertical | raster 2,54 |

Bez odchyłek (MPN jak w BOM): Q1, Q2 (SUP53P06-20-E3), Q4 (2N5401YBU), D2 (STPS20100CT), D4/D9, D5, D6–D8, U1–U4 (U3 = TI TL431BILP), LED1, C2–C4, C6, C7, C9, RV1, J6. Mechanika zgodna z `BOM-MECHANIKA.csv`: radiatory SK129-63STS, izolacja TO-220 (tulejki IB-6, podkładki silikonowe), złącza wiązek H_BAT/H_PG (Phoenix 1786174 i 1757019, Molex 39-01-2060 i 39-00-0429).

Nie zamówiono jeszcze: samej płytki (czeka na przymiarkę 1:1 i recenzję R2) oraz rzeczy do kupienia lokalnie (przewody, drut na LK1/R34, bezpiecznik 5 A z oprawką, zaciskarka Mini-Fit Jr).
