# M1-R1 — jedna płytka LOGGER + TESTER (etap: schemat)

Wariant M1 (decyzje D-M1-1…13, `Plytki/M1-specyfikacja/`): uproszczony S1 dla świadomego użytkownika, jedna 4-warstwowa płytka, przewody lutowane do pól na PCB, w obudowie jedna listwa śrubowa X1, kable na zewnątrz przez mufy.

- Jedno źródło: `src/parts.py` (części z `source_ref` pakietów S1). Generator: `scripts/egrlab-docker python3 src/run_schematic.py`.
- Wyniki: `output/pdf/M1-R1-schemat.pdf`, `verification/QA.md`, kontrakt listwy `docs/X1.csv`, mapa pinów `docs/GPIO.csv`, zakupy `docs/zakupy.csv`.
- Kontrole: ERC, netlista pin po pinie (`verify_schematic.py`), `verify_m1.py` (X1, GPIO i piny zakazane, skalowanie kanałów AD7606B i RC, tor prądu, bezpieczny start, wspólne MISO, budżet zasilania, sieci jednopinowe) z próbami ujemnymi i zerową.
- Następny krok planu: rozmieszczenie (krok 5) z recenzją przed trasowaniem.
