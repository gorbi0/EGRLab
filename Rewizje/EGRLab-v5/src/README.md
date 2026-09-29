# Regeneracja atlasu i danych połączeń

`python src/build_hardware.py` odtwarza hardware/ oraz atlas SVG z modelu obwodu i niezmienionych danych reference/. Nie wykonuje trasowania PCB ani ERC w programie CAD. Przed zmianą zrób kopię katalogu; po zmianie uruchom testy, zaktualizuj karty PCB oraz BOM-y poszczególnych płytek.

Generator dokumentacji roboczej nie jest potrzebny do użycia wydania. Pliki profiles/ i verification/ODBIOR.csv są przeznaczone do uzupełniania pomiarami; nie regeneruj ich po odbiorze sprzętu.
