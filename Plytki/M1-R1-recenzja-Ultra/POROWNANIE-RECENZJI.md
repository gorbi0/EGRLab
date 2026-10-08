# Porównanie pierwszej recenzji i przeglądu Ultra

8.10.2026. **To samo wejście: 531 plików identycznych bajtowo.** Źródło: commit `8b08953e6ecce4de4a27a26b1fe7559a885ddbe3`. Oryginał projektu i pierwszy raport zachowano.

**W drugim przeglądzie znaleziono dodatkowe 4 ważne błędy i 1 drobny.** Nie wykazano dodatkowej pewnej usterki PCB/CAM. Nowe problemy wynikają z interakcji części oprogramowania, których zgodność nie jest sprawdzana przez ERC/DRC ani same testy pinów.

| Nowe ID | Waga | Co pominięto w pierwszej recenzji | Dowód drugiego przeglądu |
|---|---|---|---|
| M1-08 | ważne | Watchdog może być odświeżany, gdy zajęty mutex blokuje sterowanie i fizyczny STOP | Rzeczywisty `safety`: blokada 400 ms utrzymuje EN/PWM po terminie MANUAL; 400 odświeżeń, 0 odczytów przycisku. Zwykły `profile` tworzy okno blokady konsolą. |
| M1-09 | ważne | Poprawny transfer po błędzie ADC nie oznacza odzyskania ważnej konfiguracji | TIMEOUT → dwa poprawne transfery: driver nadal config_ok=0, lecz oba rekordy bez INVALID, z dawnym config_id. |
| M1-10 | ważne | Zachowanie binarnego formatu v5 nie gwarantuje zgodności eksportera | Prawdziwy producent config + syntetyczna sesja −1/0/+1 A → wszystkie prądy CSV puste i brak ostrzeżeń; także HTML. |
| M1-11 | ważne | CH6 po przeniesieniu prądu do AD7606B wymaga wspólnego unieważniania kalibracji | `cal 1 5` pozostawia ical i metric; samo vcalok przywraca możliwość qualify. Stare V/A może zaniżać prąd mimo prawidłowego zera. |
| M1-12 | drobne | Nieodebrany pomiar jest traktowany jak zmierzona usterka napięcia | Wektor NaN i znana mapa → maska 9, REF+FEEDBACK; kontrola 4 V → tylko REF. |

Pełne miejsca, obliczenia, ograniczenia dowodów i proponowane naprawy: [RECENZJA-M1-R1-ULTRA.md](C:/Users/tgorbacz/Documents/GORBI/Priv/Kia/Sportage/EGRLab/Plytki/M1-R1-recenzja-Ultra/RECENZJA-M1-R1-ULTRA.md).

## Co pozostaje z pierwszego przeglądu

| ID | Wynik drugiego przeglądu |
|---|---|
| M1-01 USB / domeny zasilania | Podtrzymany. Doprecyzowano przepływ przez diodę Waveshare i warunkową wartość VDRIVE. Nie zakładać 3V3=0 ani zwarcia źródeł USB. |
| M1-02 VBAT_CAR w TEST | Powtórnie odtworzony niezależną próbą. |
| M1-03 inicjalizacja watchdogów | Podtrzymana luka w kodzie. Nie przypisywać próbie hosta dowodu pełnego zachowania ESP-IDF po błędzie i logowaniu. |
| M1-04 deklaracja straty do 1 s | Podtrzymany; fsync nie opróżnia automatycznie całej kolejki RAM. |
| M1-05 nadpisywanie `.kicad_pro` | Nadal ten sam kod; dowód generatora z pierwszej recenzji pozostaje aktualny. |
| M1-06 instrukcja przepięć ECU | Nadal niepełna szczegółowa lista pięciu przewodów. |
| M1-07 brak fixture'ów | Nadal braki w identycznej paczce; historyczny wynik 96/102 nie jest przedstawiany jako nowy przebieg. |

**Rejestr obu przeglądów: 10 ważnych i 2 drobne uwagi.** Nie jest to twierdzenie, że wszystkie błędy projektu zostały wykryte. Pierwszego raportu nie zmieniano; doprecyzowania znajdują się tutaj i w pełnej drugiej recenzji.

## Co drugie spojrzenie doprecyzowało bez dodawania usterek

- Obecne kontrole PCB nie sprawdzają pełnej pętli odsprzęgania ADC, a ich próby ujemne operują głównie na opisie wyników. Trzeba wzmocnić proces, ale nie oznacza to automatycznie wadliwej płytki.
- OS8 przy 2 kS/s nie zapewnia uśrednienia dowolnego PWM. Potrzebna kwalifikacja metryk ze wzorcem.
- Bias wejść ADC jest objęty wymaganą kalibracją; nie zgłoszono go jako wady.
- TPS2553 ma limit około 99…139 mA, a nie twarde maksimum 100 mA. To korekta opisu/budżetu.
- Margines AVCC, zależność zera prądu od 5 V, rzeczywista pętla Kelvina oraz moduły XU wymagają odbioru sprzętu.
- Świeże ERC/DRC, kontrole pinów i odtworzenie CAM ponownie przeszły. Pięciu kompilacji ESP-IDF z pierwszej recenzji nie powtarzano bez zmiany źródeł.

## Jak interpretować wynik porównania

Ten przegląd rzeczywiście znalazł więcej konkretnych błędów. Uczciwe porównanie ma jednak ograniczenie: oprócz zadeklarowanej przez użytkownika zmiany rozumowania zastosowano dodatkowy przebieg, trzy analizy pomocnicze i nowe próby integracyjne, a główny recenzent miał wcześniejszy kontekst. Nie można przypisać całej różnicy wyłącznie Ultra.

Najbardziej użyteczna zmiana procesu to stałe testowanie granic między modułami: produkcja/odczyt danych, utrata/odzyskanie ważności pomiaru, zależności kalibracji i zachowanie STOP przy opóźnionej konsoli. Te konkretne regresje powinny wejść do następnej rewizji.
