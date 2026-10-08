# Wyniki 6.3-m1 (8.10.2026)

- 5/5 kompilacji ESP-IDF 5.4.3 w Dockerze (`espressif/idf:v5.4.3`, `scripts/egrlab-idf`, sesja w chmurze): core, minimal, logger, test, wifi; rozmiary i SHA-256 w `builds.json`, ostrzeżenia z `main/` i rozmiary w `build-*.txt`, konfiguracje w `sdkconfig.*`.
- Testy hosta C (`tests/run_host.py --cc gcc`): `host-results.txt`, `test_*-results.txt`, sondy `adc-fault-results.txt`, `storage-results.txt`, `drive-results.txt` (źródła sond wygenerowane obok).
- Python: `python-tests.txt` (102 testy: 86 regresji, 16 kontroli 6.3-m1 w `test_v63_m1.py`).
- Próby mutacyjne kontroli 6.3-m1: `v63-mutations.json` (30/30 wykrytych, próba zerowa czysta).

Pomiary sprzętowe: NIE ZBADANO (lista odbiorów w `../README.md`).
