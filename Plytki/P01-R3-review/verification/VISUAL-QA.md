# Kontrola wizualna wydania R3

23.09.2026. Obejrzano rastry wygenerowane z końcowych PDF przez Poppler:

- P01-R3-schemat.pdf: wszystkie 3 strony A3, render do 2300 px. Sprawdzono
  oznaczenia, połączenia, tabelki i marginesy. LK1 przesunięto względem Q1,
  aby jego opis nie nachodził na MPN tranzystora; obejrzano ponowny eksport.
- P02-HOLD-C1-polaczenia.pdf: 1 strona A4 poziomo, render do 2000 px. Usunięto
  kolizje opisów D_OR i HOLD_FUSED, dodano jawne GND przy C_BUS, poszerzono
  symbol bezpiecznika. Sprawdzono ponowny render.
- Obejrzano również aktualne PNG planu stref i wykresów. Plan stref nie jest
  layoutem ani rysunkiem wierceń. Wykresy są wynikami modelu.

W końcowych renderach nie stwierdzono uciętych opisów ani kolizji utrudniających
odczyt. Numery padów i połączenia sprawdzają osobno testy XML/footprintów.
Ta kontrola nie zastępuje DRC, przymiarki rzeczywistych elementów ani wydruku 1:1.
