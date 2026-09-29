# Źródła P00 R1

- v6.1-rc1: `eda/P00/P00.xml` (import pinowy), `hardware/P00-BOM.csv`, `docs/03-uruchomienie.md` §0 i §4, `verification/ODBIOR.csv` (wiersze P00) — kopie w tym katalogu.
- [TI LM2937, SNVS100F](https://www.ti.com/lit/ds/symlink/lm2937.pdf): wejście 26 V ciągle / 60 V przez ≤ 100 ms, VIN ≥ VOUT + 1 V, Cout ≥ 10 µF przy ESR < 3 Ω, ochrona przed odwrotną polaryzacją, TO-220: 1 = IN, 2 = GND (tab), 3 = OUT, RθJA 77,9 °C/W. Sprawdzone na stronach 1 i 4 karty (streszczenie narzędzia podało błędne liczby).
- [Würth WS-SLTV 450301014042](https://www.we-online.com/components/products/datasheet/450301014042.pdf): SPDT ON-ON, COM = środkowy pin 1, styki 2/3, „opposite side connection”, raster 2,54 mm (5,08 mm między skrajnymi), otwory Ø0,8 mm, 300 mA / 24 V DC, trwałość 2000 cykli.
- [TI TLC555](https://www.ti.com/lit/ds/symlink/tlc555.pdf): zasilanie od 2 V; częstotliwość astabilna 1,44/((RA + 2 RB)·C).
- [Vishay 1N5819](https://www.vishay.com/docs/88525/1n5817.pdf), [Phoenix MKDS 1,5/2-5,08](https://www.phoenixcontact.com/en-pl/products/pcb-terminal-block-mkds-15-2-508-1715721), [Kingbright L-934](https://www.kingbrightusa.com/images/catalog/SPEC/L-934GD.pdf), [Vishay K](https://www.vishay.com/docs/45171/kseries.pdf), [Yageo MF0207](https://www.yageo.com/upload/media/product/productsearch/datasheet/lr/Yageo_LR_MFR_1.pdf).
