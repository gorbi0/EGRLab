# M1-R1 — jedna płytka LOGGER + TESTER

Wariant M1 (decyzje D-M1-1…13, `Plytki/M1-specyfikacja/`): uproszczony S1 dla świadomego użytkownika, jedna 4-warstwowa płytka, przewody lutowane do pól na PCB, w obudowie jedna listwa śrubowa X1, kable na zewnątrz przez mufy. Obudowa powstanie pod płytkę.

## Schemat (krok 4)

- Jedno źródło: `src/parts.py` (części z `source_ref` pakietów S1). Generator: `scripts/egrlab-docker python3 src/run_schematic.py`.
- Wyniki: `output/pdf/M1-R1-schemat.pdf`, `verification/QA.md`, kontrakt listwy `docs/X1.csv`, mapa pinów `docs/GPIO.csv`, zakupy `docs/zakupy.csv`.
- Kontrole: ERC, netlista pin po pinie (`verify_schematic.py`), `verify_m1.py` (X1, GPIO i piny zakazane, skalowanie kanałów AD7606B i RC, tor prądu, bezpieczny start, wspólne MISO, budżet zasilania, sieci jednopinowe) z próbami ujemnymi i zerową.

## PCB (kroki 5–6)

- Łańcuch layoutu z P07 S1: `src/placement.py` (rozmieszczenie, recenzja użytkownika 8.10: „ok”), `build_board.py`, `route_critical.py` (miedź zablokowana), `fanout_gnd.py`, `prepare_routing.py`, Freerouting 2.1.0, `import_routing.py`, planer `complete_routes.py`, `cleanup.py`, `stitch.py`, `trim_stubs.py`; całość `src/run_layout.py` (`--reuse-ses [--replan]` odtwarza zapisany wynik routera `routing/M1.ses`).
- Płytka 150 × 80 mm, 4 warstwy JLC04161H-7628 (In1 ciągła masa, In2 sygnały), otwory M3 w narożach.
- Górna krawędź: pola przewodów do X1 w kolejności zacisków; prawa: ESP32-S3 DEV-KIT (antena w rogu, strefa bez miedzi, USB-C przy dolnej krawędzi); dolna: pola IBT-2, moduły MAX31856 (zaciski przy krawędzi), moduł microSD (gniazdo przy krawędzi).
- Tor 7,5 A (BAT_P, VBUS, P1_ECU, P1_EGR): wylewki na F.Cu i B.Cu zszyte przelotkami; para Kelvina zablokowana (K_MINUS przez In2.Cu pod masą In1); miedź wokół AD7606B przeniesiona z P05 R3 (to samo ułożenie, przesunięcie +37 / −15 mm) z jego regułami drobnego rastra (0,15 mm tylko w obrysie U3).
- Wydanie: `src/run_release.py` (schemat, layout, nadruk, `verify_pcb.py` z próbami ujemnymi, widoki, `output/pdf/M1-R1-PCB.pdf`, `verification/QA-PCB.md`).
