# Odbiór plików P01-PCB-R1

Data: 2026-09-23. Narzędzie końcowego odbioru: **KiCad 10.0.6**.
Stan: **przegląd layoutu; sprzęt i przymiarka NIE ZBADANE**.

| Kontrola | Wynik |
|---|---|
| Native DRC: naruszenia / niepołączone / zgodność schematu | **0 / 0 / 0** |
| Kontrole gotowej PCB i geometrii (`pcb-checks.json`) | **17/17 PASS** |
| Próbne usterki w kopiach (`negative-controls.json`) | **3/3 wykryte** |
| Schematu R3 nie zmieniono | 3 pliki zgodne SHA256 z manifestem R3 |
| Komponenty | 89 elektrycznych + HS1/HS2 + 4 mocowania = 95 footprintów |
| Fizyczne pady elektryczne | 195; zawierają dwa dodatkowe odczepy Kelvin LK1 |
| Format / warstwy / miedź | 160×120 mm / 2 / 70µm na stronę |
| Referencyjne ścieżki i przelotki mocy/pomiaru | wszystkie 56 zachowane |
| TP1 SOURCE / TP2 GATE | 4,805 / 4,719 mm do Q1 |
| Kotwy wiązek J5/J7 | 12,5 mm od rzędu lutów |
| Wypełniona miedź termików J7 | 4 ramiona na pad, każda z 2 stron; sprawdzone także szczeliny obok ramion |
| Izolacja LK1 i radiatorów w netliście | zachowana; kontrola fizyczna przed montażem |
| PDF | 5 stron obejrzanych po renderowaniu; montaż i miedź 1:1 |

`pcb-checks.json` wiąże wynik z SHA256 gotowej PCB. `release-manifest.json`
wiąże pliki pakietu. **Po każdej zmianie miedzi, pada, footprintu albo reguły
wynik trzeba uzyskać ponownie**; nie wystarczy zachować starego raportu.

## Co wykryło coś rzeczywistego

Router połączył pomocniczą gałąź C5 z polem sense VPROT przy LK1. DRC dopuszczał
takie połączenie, bo elektrycznie należało do tej samej sieci. Kontrola stopnia
rozgałęzienia pól sense wykryła problem. Gałąź przeniesiono do pola siłowego;
obie ścieżki sense są teraz wyłącznie zakończeniami pomiarowymi 0,4 mm.

To przykład kolejności kontroli: **schemat/netlista → DRC → wymaganie funkcjonalne
w geometrii PCB**. W kolejnym module należy zdefiniować takie wymagania przed
routingiem, np. położenie ADC/filtru, tor Kelvina bocznika i ścieżkę SAFE.

## Próby ujemne

1. Usunięcie odcinka do TP2: wykryte przez kontrolę zachowania toru i długości dojścia.
2. Przesunięcie H3 o 1 mm: wykryte przez niezależnie zapisane współrzędne otworów.
3. Ścieżka zwierająca LK1: wykryta przez natywny DRC jako `shorting_items`.

Pliki w `negative-controls/` są wynikami prób błędów. Nie są alternatywnymi
wersjami do produkcji. Skrypt tworzy robocze kopie i nie zmienia `eda/P01.kicad_pcb`.

## Reguły i powtórzenie odbioru

Wymagana clearance sieci 0,30 mm (minimum globalne 0,25), minimum ścieżki0,30,
viaØ0,8, annulus0,20, Cu-krawędź0,50, otwór-otwór0,30 i silk0,15 mm.
Tablica wyłączeń konkretnych naruszeń jest pusta. Nie wyłączano naruszeń, aby
otrzymać PASS. Pozostałe standardowe kategorie/poziomy KiCada są w projekcie.

Uruchomić z katalogu pakietu (z narzędziami KiCad dostępnymi w PATH):

```powershell
kicad-cli pcb drc --format json --severity-all --schematic-parity --all-track-errors --refill-zones --save-board -o verification/drc.json eda/P01.kicad_pcb
# Python dołączony do KiCada, z modułem pcbnew:
python src/verify_pcb.py
python src/negative_controls.py
```

Nie używać przypadkowego Pythona bez `pcbnew`. `verify_pcb.py` nie nadpisuje PCB.
Po ponownym wypełnieniu stref może zmienić się serializacja pliku i jego hash:
wtedy powtórzyć odbiór oraz manifest. Biblioteki padów R3 są w pakiecie referencyjnym
i nie wymagają instalowania kompletu bibliotek globalnych.

## Narzędzia i odtwarzalność

Prowadzenie krytycznych sieci zapisano jawnie; pozostałe sygnały Freerouting2.1.0
prowadził lokalnie. Nie wysyłano projektu do usługi routingu. Jego wynik nie był
kryterium końcowym: po imporcie wykonano DRC i kontrole PCB w KiCadzie.

Pythonowe API importu SES zwracało False bez diagnostyki. Skrypt `import_routing.py`
odczytuje ściśle kontrolowany podzbiór SES: pozycje wszystkich95 footprintów,
jednostkę0,1µm, dwie warstwy, znane sieci, ścieżki i przelotki. W wyniku importu
dodano415 segmentów i8 przelotek do torów przygotowanych ręcznie. Późniejsza
korekta gałęzi C5 jest w `repair_kelvin.py`. Nie ignoruje się nieznanych rekordów.

Skrypty budowy stanowią zapis prac, nie automat bezwarunkowej regeneracji.
Źródłem końcowym jest zapisany projekt KiCad. `routing/prerouted.kicad_pcb` jest
tylko wzorcem ścieżek krytycznych przed routingiem; nie otwierać go jako gotowej PCB.

KiCad CLI zgłaszał niedostępny zapis osobistych ustawień/font cache w środowisku
ograniczonym. Raport DRC, plik PCB i renderowanie zostały utworzone; komunikaty
zachowano w logach. To nie są wyniki pomiarów urządzenia.

Plot SVG dostał margines0,05mm przez zmianę samego viewportu, bez skalowania
geometrii. Dzięki temu cały obrys jest widoczny. PDF osadza obrazy CAD około
762dpi w ich fizycznych wymiarach; osobne SVG zachowują geometrię wektorową.
Na stronach2-4 jest niezależna belka100mm. Rzeczywistą drukarkę trzeba sprawdzić.

Źródła narzędzi: [KiCad PCB Editor](https://docs.kicad.org/10.0/en/pcbnew/pcbnew.html),
[KiCad CLI](https://docs.kicad.org/10.0/en/cli/cli.html),
[Freerouting 2.1.0](https://github.com/freerouting/freerouting/releases/tag/v2.1.0).
Źródła części i protokoły badań pozostają w dokumentacji R3.

## Pozostałe otwarte warunki

Przymiarka radiatorów, izolacji, złączy, przewodów i obudowy; kwalifikacja lutów
PTH mocy; pomiary termiczne i SOA Q1; dynamika pełnego układu; metrologia VGS/
prądu; odporność na impulsy; integracja z P02-HOLD. Żadnego nie oznaczono PASS.
Gerber/Excellon są następnym eksportem po przymiarce. P07 pozostaje HOLD.
