# Weryfikacja EGRLab v5 — 22.09.2026

## Wykonane

- **5/5 kompilacji ESP-IDF 5.4.3 zakończonych kodem 0:** CORE, minimal, LOGGER, TEST, Wi-Fi. Oddzielne sdkconfig i katalogi kompilacji; końcowe kompilacje przyrostowe po pełnym zbudowaniu każdego wariantu. Logi `build-*.txt`, konfiguracje `sdkconfig.*`, rozmiary i SHA256 aplikacji w `builds.json`.
- **63 testy Python — OK.** Czytnik formatów 1–5, CRC, niepełne metadane, kalibracje, profile, netlista i wiązki. Testy v4 zachowano jako regresję historycznej bazy; `test_v5.py` sprawdza nowy obwód, rzeczywiste piny bramek, wszystkie 128 kombinacji sygnałów gotowości, lokalny permit, kodowanie IDC oraz kompletność połączeń między modułami.
- **291 asercji C — OK:** 107 logika sterowania, 47 konfiguracja/JSON/metryki, 93 ustawianie i błędy ADC, 29 kolejka i serializacja, 15 odczyt lokalnego prądu. Wyniki są w plikach `*-results.txt`. Próby ADC/storage/current wyciągają rzeczywiste funkcje ze źródeł i podstawiają sterowane odpowiedzi zależności.
- Syntetyczny log v5: 4000 próbek, 40 B/rekord, CRC, eksport CSV i 7 wykresów HTML. Symulowana utrata prądu nie zeruje wyniku i nie usuwa poprawnych napięć. Raport otwarto w przeglądarce; bez błędów JavaScript. **To nie jest pomiar samochodu.**
- Wzrokowa kontrola renderowanych arkuszy P04, P05 i P06; poprawiono zawijanie długich nazw. Atlas i BOM generowane z tego samego modelu połączeń. 603 wpisy elementów, 2382 przypisania pinów, 83 arkusze SVG. Tabela wiązek zawiera również wolne pozycje NC — nie należy ich łączyć ze sobą.
- Potwierdzono brak zmian SHA256 191 plików źródłowych wcześniejszych wydań użytych do opracowania v5. `sources-sha256.json` i `source-integrity.txt`. Katalog V3 nie był modyfikowany.

## Odtworzenie

W katalogu wydania:

```
python -m unittest discover -s tests -v
python tests/run_host.py --cc gcc
python src/build_hardware.py
```

Host C sprawdzono także TinyCC 0.9.27. Do tego kompilatora runner automatycznie używa lokalnej nakładki math.h; GCC korzysta ze swojej biblioteki. Nakładka nie wchodzi do firmware. Starszy TinyCC zastępuje _Static_assert równoważnym sprawdzeniem rozmiaru tablicy na etapie kompilacji. Próbki i metryki w testach są sztuczne; nie emulują właściwości analogowych.

## Do wykonania na sprzęcie

Wszystkie **57 pozycji `ODBIOR.csv` ma status NIEWYKONANE**. Nie wykonano pomiarów szumów, czasu SPI, progów i opóźnień odcięcia, charakterystyki prądowej ani temperatur. Nie zweryfikowano odporności na przepięcia w samochodzie. Brak layoutu PCB, Gerberów, ERC/DRC w EDA i modelu mechaniki złączy. Sprawdzenie spójności netlisty nie zastępuje tych prac.

Wydanie zawiera projekt obwodu do etapowej budowy prototypu, program i dokumentację montażową. Nie należy opisywać go jako fizycznie odebranego urządzenia ani gotowych do produkcji PCB. Przed TEST trzeba wykonać odbiór, kalibracje i wymagane ustawienia opisane w docs/03-uruchomienie.md.
