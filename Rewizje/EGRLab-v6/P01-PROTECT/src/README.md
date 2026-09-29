# Odtwarzanie dokumentacji

Wymagania: Python 3 oraz pakiet `reportlab`. Generator PDF używa czcionek Segoe UI z Windows.

Uruchom kolejno z głównego katalogu tego dodatku:

```powershell
python src/build_netlist.py
python src/verify.py
python src/render.py
```

`build_netlist.py` definiuje elementy i połączenia. Generuje JSON, BOM i netlistę CSV. `verify.py` sprawdza połączenia oraz uproszczony model statyczny progów. `render.py` tworzy PDF, arkusze SVG i zgrupowaną listę zakupów na podstawie tych samych danych oraz dokumentów Markdown.

Po zmianie dokumentacji trzeba ponownie sprawdzić wygląd stron PDF. Same skrypty nie wykonują symulacji SPICE, analizy dynamicznej tranzystorów ani pomiarów sprzętowych. Kontrole zakończone powodzeniem nie oznaczają odbioru modułu do pracy w samochodzie.
