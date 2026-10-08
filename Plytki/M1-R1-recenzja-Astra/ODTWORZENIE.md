# Dowody i odtworzenie recenzji M1-R1

Raport: [RECENZJA-M1-R1.md](C:/Users/tgorbacz/Documents/GORBI/Priv/Kia/Sportage/EGRLab/Plytki/M1-R1-recenzja-Astra/RECENZJA-M1-R1.md). Dowody dotyczą źródła i SHA-256 wymienionych w raporcie. Pliki projektu pozostają w katalogu `M1-R1-do-recenzji`; nie należy uruchamiać generatorów w oryginale.

## Układ katalogu

- `evidence/`: niezależne próby, logi, końcowe wyniki i migawka SHA-256 oryginału.
- `evidence/hardware/`: świeże ERC/DRC, porównanie netlisty i kontrole PCB z kopii roboczej.
- `evidence/cam/`: świeży eksport i odczyt CAM oraz wyniki prób ujemnych.
- `evidence/firmware/`: wyniki testów C i kopie konfiguracji pięciu lokalnych kompilacji.
- `evidence/rebuild/`: logi i wyniki pełnego odtworzenia projektu z zapisanej sesji routera.

Duże katalogi robocze i narzędzia nie są kopiowane do recenzji. Pozostały w:

`C:\Users\tgorbacz\.codex\.chatgpt-projects\g-p-6a8827e57cc881919b26f761377a7bd3\M1-R1-recenzja-Astra`

`work/` jest kopią kompletnej paczki; `regen/` jest osobną kopią `Plytki/M1-R1-review`, na której odtwarzano projekt. W oryginale nie zmieniono żadnego pliku. Można odtworzyć ten układ w nowym katalogu; skrypty recenzenta odwołują się do `work/` i `regen/` względem swojego katalogu `evidence/`. Niektóre ścieżki narzędzi w skryptach są lokalne i wymagają dostosowania na innym komputerze.

## Środowisko

- KiCad CLI i Python/pcbnew **10.0.6**, lokalna instalacja `.egrlab-toolchains/kicad/runtime/bin`.
- `KICAD_LIBRARY_ROOT=C:/Program Files/KiCad/10.0/share/kicad`; lokalny `KICAD_CONFIG_HOME`.
- ESP-IDF **5.4.3**, Python 3.12, Xtensa `esp-14.2.0_20250730`, CMake 3.30.2, Ninja 1.12.1.
- TinyCC dla prób hosta C. W kopii testowej: shim `isinf` i `lroundf`; usunięte `-lm` w komendzie kompilacji `probe_drive.py`. Dostarczono zmodyfikowany shim i wrapper jako dowód środowiska. Żadnych zmian w kodzie produkcyjnym `firmware/main/`.
- Poppler do renderowania, ReportLab do PDF w pełnym łańcuchu projektu; Node + sharp do podglądów.
- Shapely 2.1.2 w osobnym `review-deps/`, wyłącznie do porównania regionów CAM. Instalacja nie zmieniała zależności projektu ani środowiska ESP-IDF.

Ostrzeżenia lokalnego Fontconfig i o powtórnych handlerach obrazów KiCad nie były naruszeniami ERC/DRC. Nie wyciszano naruszeń elektrycznych w celu uzyskania PASS. W końcowym natywnym raporcie DRC nie było także ostrzeżeń o różnicy footprintów.

## Główne polecenia

W poniższych przykładach `python-kicad` oznacza `python.exe` z `pcbnew`, `python-host` zwykły Python z zależnościami, a `kicad-cli` wersję 10.0.6. Uruchamiać w odpowiednich **kopiach roboczych**, nigdy w oryginale.

```text
# Hardware, katalog work/Plytki/M1-R1-review
kicad-cli sch erc --format json --severity-all -o verification/erc.json eda/M1.kicad_sch
kicad-cli sch export netlist --format kicadxml -o verification/M1.xml eda/M1.kicad_sch
python-kicad src/verify_schematic.py
python-kicad src/verify_m1.py
python-kicad src/verify_pcb.py

# Pełne odtworzenie w osobnym regen/, bez nowego losowania tras routera
python-kicad src/run_release.py

# Produkcja, work/Plytki/M1-PCB-R1-zamowienie
# export_production czyści gerber/ i podglad/ tej kopii
python-kicad src/export_production.py
python-host src/check_cam.py
python-host src/cam_negative_controls.py

# Firmware, work/Rewizje/EGRLab-v6.3-m1
python-host tests/run_host.py --cc <kompilator-lub-wrapper-TinyCC>
python-host -m unittest discover -s tests -v
```

Pełne polecenia pięciu kompilacji znajdują się w `evidence/build-review.ps1`; wyjścia w `build-*.log`. Każdy wariant dostał osobny `build-review-*` i `sdkconfig.review-*`. Wszystkie kompilacje zakończyły się powodzeniem; nie wgrywano firmware do sprzętu i nie porównywano binariów bajtowo z kompilacjami chmurowymi, których metadane/ścieżki mogą być inne.

Przed ponownymi testami Python dostarczyć dokładne stare fixture'y opisane w M1-07. Podczas recenzji do kopii dołączono dostępne referencje v6.1-rc1, ale nie tworzono atrap brakujących v6.2-s1/P09 tylko po to, by uzyskać zielony wynik.

## Własne próby recenzenta

- `probe_review.c`: skompilować z niezmienionymi `control.c`, `profile.c`, `measure.c` i nagłówkami `firmware/main`; przykładowa komenda niżej. Wynik `probe_review.txt` pokazuje stan przy CH7=0/13,5/16,8 V. Ostatni test sekwencji 8,1/7,9 A ilustruje zasadę dwóch kolejnych próbek, **nie jest zgłoszeniem błędu OC**.
- `probe_watchdog_review.py`: wyciąga funkcje z kopii `board.c` oraz dwie gałęzie kodu `app_main.c`, kompiluje z atrapami HAL. Trzy awarie startu WDT, następnie ścieżka ponownego odblokowania. Wygenerowany C dołączony obok logu.
- `independent_checks.py`: porównuje produkcyjną kopię projektu, pobiera trzy użyte karty katalogowe i uruchamia sam generator schematu w osobnym `regen/`. Ten przebieg odtwarza utratę reguł projektu. Należy go uruchamiać przed pełnym rebuildem, który ponownie ustawia reguły.
- `geometry_review.py`: odczytuje oryginalną PCB bez zapisu, mierzy długości tras i zapisuje jawne obliczenia dla TPS2553, INA240, bocznika i GPIO39.
- `compare_final.py`: końcowa integralność źródła, kontrola ZIP, porównanie geometrii odtworzonej PCB i danych świeżego eksportu. Raport różnic tekstu Gerber jest uzupełniany przez następny skrypt.
- `compare_cam_regions.py`: używa parsera Gerber z projektu i Shapely do ilościowego porównania różnic konturów świeżego eksportu. Same różne sumy SHA nie oznaczają różnej geometrii produkcyjnej.

```text
<cc> -std=c11 -Ifirmware/main evidence/probe_review.c firmware/main/control.c firmware/main/profile.c firmware/main/measure.c -o evidence/probe_review.exe
```

Przykład wymaga dostosowania względnej ścieżki do `evidence/`; na GCC dodać `-lm`. W recenzji użyto wrappera `tcc-review.cmd`. Skrypt watchdogów wymaga kopii projektu w układzie `work/` opisanym wyżej.

## Granice dowodów

Kontrole PCB i ich mutacje pracują częściowo na migawce geometrii; nie są 13 oddzielnymi produkcyjnymi płytkami ze wstawionymi wadami. Próby CAM faktycznie modyfikują kopie plików produkcyjnych. Testy hosta nie emulują ESP32, PSRAM, SD ani układów analogowych. Dodatni pełny rebuild nie wyklucza M1-05, ponieważ cały łańcuch przywraca wygenerowane reguły po ich usunięciu.

Podglądy PDF/CAM obejrzano; nie przeprowadzono fizycznej przymiarki, pomiarów oscyloskopem, nagrzewania, testu karty SD ani jazdy samochodem. Nie wykonywano wdrożenia, zamówienia PCB ani edycji źródeł Opusa.
