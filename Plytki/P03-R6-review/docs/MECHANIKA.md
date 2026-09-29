# Mechanika i montaż (R6, format S1)

Obowiązuje `Plytki/Format-S1/SPECYFIKACJA-FORMATU-S1.md` (S1-2). P03 ma klasę **L** (160,0 × 100,0 mm, sloty S1 x = 0–53, S2 x = 53,5–106,5, S3 x = 107–160), **poziom 2**, dystans 20 mm, elementy na górze ≤ 16,5 mm, 12 otworów M3 (x = 4/49 w slocie, y = 14/86). Layout nie jest częścią tego pakietu (sesja lokalna).

- **Krawędź A (y = 0):** J_BP1/J_BP2/J_BP3 — IDC 2×10 kątowe obudowane, środek x = 26,5 / 80,0 / 133,5 mm, strona wtyku równo z krawędzią, pin 1 od mniejszego x. Pas y = 0–10 mm na długości złącza zastrzeżony.
- **Krawędź B (y = 100):** J_SV1/J_SV2/J_SV3 — goldpin 1×13 kątowy w pasie x = 10–43 mm slotu (np. od x = 11,26 mm, raster 2,54), kołki ok. 6 mm za krawędzią, GND na pinach 1 i 13, nazwy sygnałów czytelne od strony B. Rezystory szeregowe R44–R76 przy węzłach.
- **M1** na dwóch listwach żeńskich 1×22, rozstaw 22,86 mm (zmierzony). **Gniazdo USB od strony krawędzi B**, żeby programować moduł przy złożonym stosie; antena od przeciwnej strony, bez miedzi obu warstw (+3 mm na boki, +8 mm za modułem). Wysokość modułu na listwach potwierdzić wobec 16,5 mm. RGB na GPIO38 odłączyć (v6.1).
- **SD1** (Adafruit 4682): karta dostępna z boku stosu albo przy krawędzi B.
- Układy SOIC-14 (U11–U14, U21–U23), SOT-23-5/6 (U3–U6), SOT-23 (Q1) lutowane wprost; U1 DIP28 i U2 DIP16 w podstawkach. SMD od spodu tylko ≤ 1,5 mm (1206, SOT-23), ≥ 1 mm od pól THT, poza strefami dystansów.
- Rezystory THT (10 kΩ, 4,7 kΩ) na stojąco, raster 5,08 mm; SMD 1206: 1 kΩ, 330 Ω, 220 Ω, 33 Ω. Kondensatory K15 THT, C12–C15 1206.
- U6, R41, C15 przy J_BP3.12; R42 przy M1 J1-13 (GPIO3), R43 przy J_BP2.18; R36–R40 przy wyjściach buforów.
- Nadruk: `P03 R6 S1-L`, znaczniki krawędzi A i B, pin 1 każdego złącza.
