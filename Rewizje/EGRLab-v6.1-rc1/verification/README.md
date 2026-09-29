# Wyniki 6.1-rc1

- 86 testów Python: zaliczone. W tym 7 nowych testów stabilizacji i regresja wcześniejszych 79.
- 355 asercji C: zaliczone (sterowanie107, runtime47, ADC93, storage29, prąd15, HEALTHY/freshness64). Są to próby programu z podstawionymi zależnościami, nie testy analogowe.
- 5/5 kompilacji ESP-IDF 5.4.3: core, minimal, logger, test, wifi. Aktualność obiektów względem zmienionych źródeł sprawdzona. Sumy obrazów i źródeł: builds.json.
- 10 celowych uszkodzeń modelu: wszystkie wykryte. Oryginalne V6 nadal oblewa nowe kontrole (zgodnie z oczekiwaniem).
- 39 statycznych kontroli P01 i model DC/wrażliwości: zaliczone. Osobny test potwierdza odpowiadający mu obwód zintegrowany.
- KiCad10.0.6: 16 eksportów zgodnych, 2162 podłączonych końcówek porównanych; NC sprawdzone na brak zwarcia. 0 błędów ERC, 8 jawnych ostrzeżeń opisanych w eda/README.md. To import pinowy, nie zakończony projekt PCB.
- Poprzednie V6: 389 plików niezmienionych, potwierdzone SHA256. Pomiary sprzętowe pozostają NIEWYKONANE.

Odtworzenie z katalogu wydania:

```
python -m unittest discover -s tests -v
python tests/run_host.py --cc gcc
python stabilizacja/checks.py
python stabilizacja/checks.py --baseline
python stabilizacja/verify_eda.py --cli kicad-cli
```

Wywołanie --baseline ma zwrócić błąd: to dowód wykrywania usterek oryginału. Nie należy zmieniać bazy, by ten test „zazielenić”. TinyCC na Windows wymaga ścieżki do tcc zamiast gcc. Moduł P01: python P01-PROTECT/src/verify.py.

Weryfikacja zasilania, podciągań i semantyki nie zastępuje kontroli symboli, footprintów, tolerancji, dynamiki, termiki ani przewodów w sprzęcie. Status każdej bramki: stabilizacja/bramki-modulow.csv.
