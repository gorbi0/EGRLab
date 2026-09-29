# Regeneracja atlasu i danych połączeń

`python src/build_hardware.py` odtwarza model, CSV połączeń, obie kopie interfejsy.csv, BOM-y, zakupy, karty PCB i atlas SVG. Poprawki V6 są w v6_changes.py, stosowane przed zapisem danych. `python src/build_montaz.py` odtwarza rysunki zasad montażu. Nie wykonuje to trasowania PCB ani ERC w programie CAD. Po zmianie uruchom `python -m unittest discover -s tests -v` oraz testy C opisane w verification/README.md.

Generator dokumentacji roboczej nie jest potrzebny do użycia wydania. Pliki profiles/ i verification/ODBIOR.csv są przeznaczone do uzupełniania pomiarami; nie regeneruj ich po odbiorze sprzętu.
