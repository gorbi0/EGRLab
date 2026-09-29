Odtworzenie listy (Python 3, bez dodatkowych pakietów):
  python gen.py ..    -> TME-wklej.txt, TME-przewody-wklej.txt, FARNELL-wklej.txt, MOUSER-wklej.txt, zakupy-2.csv
                         oraz kontrola pokrycia: każda pozycja z BOM-ów ma zakup, zapas albo status otwarty
  python doc.py ..    -> ZAKUPY-2.md
Dane: items.py/items2.py (zapotrzebowanie netto z pakietów płytek i zapas z 24.09),
      tme.py (symbole, ceny i stany TME z 28.09), other.py (Kamami, przewody, Farnell, Mouser, pozycje otwarte).
