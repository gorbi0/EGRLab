# Wyniki 6.2-s1 (1.10.2026)

- 5/5 kompilacji ESP-IDF 5.4.3 w Dockerze (`espressif/idf:v5.4.3`, `scripts/egrlab-idf`): core, minimal, logger, test, wifi; rozmiary i SHA-256 w `builds.json`, skróty logów w `build-*.txt`, konfiguracje w `sdkconfig.*`.
- Testy hosta C (`tests/run_host.py --cc gcc`): `host-results.txt`, `test_*-results.txt`, sondy `adc-fault-results.txt`, `storage-results.txt`, `current-results.txt` (źródła sond wygenerowane obok).
- Python: `python-tests.txt` (96 testów: 86 regresji 6.1 na modelu sprzętu `../EGRLab-v6.1-rc1`, 10 kontroli 6.2-s1).
- Próby mutacyjne kontroli 6.2-s1: `v62-mutations.json` (10/10 wykrytych, próba zerowa czysta).

Pomiary sprzętowe: NIE ZBADANO (lista odbiorów w `../README.md`).
