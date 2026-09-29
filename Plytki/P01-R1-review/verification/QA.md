# Wynik kontroli wydania — 23.09.2026

Autor: Codex. Nie jest to niezależna recenzja ani odbiór sprzętu.

- KiCad CLI 10.0.6 odczytał projekt, wyeksportował XML, PDF i trzy SVG.
- Porównanie XML z zamrożoną bazą: 87 elementów, 189 końcówek, 34 sieci; zero różnic.
- ERC: zero zgłoszonych błędów i ostrzeżeń, standardowe ustawienia KiCad.
  Domyślnie nieaktywne reguły widoczne w `erc.json`: pojedyncza etykieta globalna,
  skrzyżowanie czterech odcinków, model SPICE, filtr nazwy footprintu. Mapowanie
  padów biblioteki sprawdzono osobno; modelu SPICE nie ma.
- 195 kontroli pakietu zakończonych powodzeniem; są to m.in. kontrole padów
  każdego elementu, a nie 195 różnych prób elektrycznych.
- Cztery celowo uszkodzone kopie eksportu wykryte: D/S Q1, polaryzacja wejść OVP,
  rozłączenie SAFE_N w J5, brak footprintu J6. Oryginał nie był modyfikowany.
- Model statyczny bazy uruchomiony na kopii: 39 kontroli, 5000 kombinacji
  wrażliwości. Granice tego modelu nie są gwarantowanymi tolerancjami sprzętu.
- PDF: 3 strony A3, wyrenderowane Popplerem i obejrzane. Poprawiono kolizję
  wyjścia U2B z tabliczką rysunkową; wszystkie arkusze czytelne.
- Obejrzano rysunek stref mechanicznych. Brak projektu tras i otworów radiatorów.
- Ścieżki rejestru i cache fontów zgłaszały odmowę zapisu w środowisku uruchomienia
  CLI. Eksporty powstały i zostały niezależnie odczytane. Nie wyłączano kontroli
  połączeń, by uzyskać dodatni wynik.

Zostają otwarte E-01/M-01/B-01 z `docs/PRZEGLAD.md`; potem layout i DRC.
Próby na stole, SOA w przełączeniu, temperatura i odporność impulsowa: NIE ZBADANO.
