# P08 SENSOR — R1 do recenzji

P08 zasila czujnik położenia EGR w trybie TEST z szyny 5V_SYS. TPS2553 ogranicza prąd, a przewlekany przekaźnik rozłącza dodatnie zasilanie i przewód powrotny. W LOGGER przekaźnik pozostaje wyłączony; czujnik zasila ECU przez tor P11.

Płytka: **100 × 80 mm, dwuwarstwowa, FR4 1,6 mm, Cu 35 µm**, 4 otwory M3. Montaż mieszany: przeważnie THT, TPS2553 w SOT-23-6, dwa bufory SO14 i kondensatory lokalne 0805. Jednostronnie lutowane wiązki J1–J3 z kotwami; J4 Mini-Fit Jr na PCB.

- Projekt KiCad: `eda/P08.kicad_pro`, schemat `eda/P08.kicad_sch`, PCB `eda/P08.kicad_pcb`. Lokalne biblioteki w `eda/libraries`.
- Schemat PDF: `output/pdf/P08-R1-schemat.pdf`; PCB i montaż 1:1: `output/pdf/P08-R1-PCB.pdf`.
- Zakupy: `docs/ZAKUPY.md`; dokładny BOM: `docs/BOM.csv`; wiązki: `docs/WIAZKI.md` i `docs/interfejsy.csv`.
- Obwód, obliczenia i ograniczenia: `docs/PROJEKT.md`; zmiany względem v6.1: `docs/ZMIANY.md`.
- Wyniki kontroli plików: `verification/QA.md`; pusty formularz pomiarów: `verification/ODBIOR.md`.
- Powtarzalna odbudowa: `docs/ODTWORZENIE.md`. Źródła producentów i migawki sąsiednich interfejsów w `reference`.

**Status: projekt do recenzji, sprzęt NIE ZBADANY.** Nie ma tu Gerberów dopuszczonych do produkcji. Przed ich wygenerowaniem obowiązuje recenzja i przymiarka rzeczywistych części do wydruku 1:1. Dotychczasowych płytek ani katalogów rewizji nie zmieniono. P07 pozostaje HOLD do oględzin rzeczywistego modułu BTS7960.

Warunek integracji: po pojawieniu się poprawnego SENSOR_OK odczekać **750 ms** przed pierwszym podaniem SENSOR_PERMIT (także po zaniku zasilania). READY nie potwierdza napięcia za przekaźnikiem. Ogranicznik ma około 117 mA typowo; wstępna identyfikacja nieznanego czujnika nadal wymaga źródła z limitem 20 mA.
