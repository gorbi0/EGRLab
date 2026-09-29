# Weryfikacja V6 — 23.09.2026

- **79 testów Python: OK.** Regresja czytnika logów, brakujące metadane, CRC, profile, rzeczywiste piny bramek/interlock, nowe połączenia M2, pojedyncze rezystory i skale, P01 FAULT, adaptery, BOM i rozbicie wiązek. Wynik: python-tests.txt.
- **291 asercji C: OK.** Sterowanie107, runtime47, błędy AD93, storage29, lokalny ADC15. Pliki *-results.txt pochodzą z ponownego uruchomienia źródeł V6 przez TinyCC. Próby podstawiają zależności programowe; nie są symulacją analogową.
- **5/5 kompilacji ESP-IDF 5.4.3: ukończone.** CORE, minimal, LOGGER, TEST, Wi-Fi; osobne konfiguracje i obrazy V6. Domyślne zegary AD1MHz/SD4MHz; sprzęt niezaakceptowany. Logi build-*.txt, skróty builds.json.
- Generator ponownie odtworzył dane bez różnic: generator-reproducibility.txt. 585 wpisów obwodu, 2358 przypisań pinów, 81 arkuszy SVG; część wpisów to pola PTH, których nie kupuje się jako elementów.
- Kontrola renderów ADC, lokalnego ADC prądu, bramki P07, kotwy, B2B i karty stref P02. Poprawiono kolizję opisu przy wsporniku B2B. Pliki *-preview.png są podglądami wybranych arkuszy, nie layoutem PCB.
- Sprawdzono odnośniki i SHA256 oryginalnych wydań V3/V5: source-integrity.txt oraz previous-releases-sha256.json. Materiały reference/verification-v5 to wyłącznie historia poprzednich prób.

**Wszystkie 67 prób sprzętowych pozostaje NIEWYKONANE.** Nie ma pomiarów szumów/VREF/termiki, potwierdzenia czasów SPI ani odbioru ochrony automotive. Nie ma gotowych layoutów, Gerberów, ERC/DRC w EDA ani szczegółowego rozmieszczenia wszystkich części na uniwersalnych. Rysunki stref i kotew są wytycznymi wykonawczymi.

Odtworzenie w katalogu wydania:

```
python src/build_hardware.py
python src/build_montaz.py
python -m unittest discover -s tests -v
python tests/run_host.py --cc gcc
```

TinyCC można podać zamiast GCC; runner wtedy używa host-tcc-include. Generator nie zmienia profili ani wpisanych pomiarów ODBIOR. Format logu nadal5/40B; profil NVS i szablony JSON6. Nie przenosić starej kalibracji przez zmianę samego numeru wersji.
