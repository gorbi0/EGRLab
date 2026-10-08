# Odtworzenie drugiej recenzji M1-R1

8.10.2026. Pliki w `evidence/` są zapisanymi dowodami z recenzji, a nie poprawionym projektem. Żaden test nie sterował rzeczywistym zaworem. Nowe próby wykonują rzeczywiste funkcje C oraz czytnik Python; platforma ESP-IDF i harmonogram są zastąpione kontrolowanymi atrapami.

## Jedno polecenie dla pięciu nowych zgłoszeń

Wymagania: Python 3 oraz TinyCC dla Windows z dostępnego lokalnego toolchainu EGRLab. Podany toolchain był już używany w projekcie; pakiet recenzji nie pobiera ani nie instaluje narzędzi. Własny nagłówek `math.h` zapewnia zgodność kompilatora hostowego; nie jest zmianą dostarczonego firmware ani bibliotek ESP-IDF.

```powershell
$review = 'C:/Users/tgorbacz/Documents/GORBI/Priv/Kia/Sportage/EGRLab/Plytki/M1-R1-recenzja-Ultra'
$source = 'C:/Users/tgorbacz/Documents/GORBI/Priv/Kia/Sportage/EGRLab/Plytki/M1-R1-do-recenzji'
$workspace = 'C:/Users/tgorbacz/.codex/.chatgpt-projects/g-p-6a8827e57cc881919b26f761377a7bd3'
$python = 'C:/Users/tgorbacz/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe'
$scratch = Join-Path $env:TEMP ('M1-Ultra-repro-' + [guid]::NewGuid().ToString('N'))
& $python "$review/run_review_probes.py" --source $source --tcc "$workspace/EGRLab-v3-review/toolchain/tcc/tcc.exe" --work $scratch
```

Skrypt wymaga nowego katalogu roboczego, sprawdza SHA-256 wszystkich plików źródłowych przed próbą i porównuje je po niej. Nie pozwala bez ostrzeżenia testować innej rewizji. Nie pisze w źródle ani w katalogu zapieczętowanej recenzji. Import Python ma wyłączone tworzenie `__pycache__` w źródle. Ścieżki w kopiach harnessów zostały sparametryzowane; funkcje wycinane z firmware pozostają niezmienione.

W tej recenzji powyższy mechanizm uruchomiono ponownie po przygotowaniu publikacji. Przebieg znajduje się w `evidence/reproduction/run.log` i `run.json`. Oczekiwany ostatni komunikat:

```text
All five NEW review findings reproduced on the unchanged R1 source.
```

To komunikat **odtworzenia usterek**, nie ich naprawy. Po poprawieniu firmware należy dodać przeciwne asercje jako regresje projektu; ten skrypt jest świadomie związany z hashami R1.

| Próba | Rzeczywisty kod | Granica dowodu |
|---|---|---|
| `probe_independent.py` | `safety`, `button_tick`, `print_profile`, operacje bramki/LEDC, `control.c` | Wstrzyknięty mutex 400 ms; nie pomiar ESP32. Czas UART wynika z liczby bajtów i konfiguracji. |
| `probe_adc_metadata.py` | `acquisition`, `board_adc`, `control.c`, `measure.c`, `jsonlog.c` | TIMEOUT/udane transfery podstawiono w `adc_read_owned`; nie założono resetu zakresów. |
| `probe_producer.c` | `control_build_config`, `json_config`, `profile_command`, `trigger_sample` | Fixture inicjuje profil; zakres zmian kwalifikacji i NaN testowany na rzeczywistych funkcjach. |
| `probe_reader.py` | Niepoprawiony `tools/egrlog.py` | Pełny syntetyczny log v5, CRC, CSV i HTML; nie log z auta. |

Pozostałe wyniki hostowe: `evidence/firmware/test_control-results.txt`, `test_runtime-results.txt`, `test_health-results.txt`, `test_obd-results.txt`. Oryginalne zestawy C przeszły odpowiednio 131, 66, 58 i 23 asercje. Ich źródła są w `Rewizje/EGRLab-v6.3-m1/tests/` paczki. Nie przeprowadzono ponownie całej suity Python ani pięciu kompilacji ESP-IDF — wyniki tych szerszych przebiegów są wyraźnie opisane jako pochodzące z pierwszej recenzji identycznego pakietu.

## Kontrole CAD wykonane w drugim przebiegu

KiCad 10.0.6, Python z jego runtime. Kontrole uruchamiano na kopii całej paczki w lokalnym katalogu `M1-R1-recenzja-Ultra/work`, a nie na źródle. Ścieżki wykonywalne:

```text
<workspace>/.egrlab-toolchains/kicad/runtime/bin/kicad-cli.exe
<workspace>/.egrlab-toolchains/kicad/runtime/bin/python.exe
```

Ustawienia:

```powershell
$env:KICAD_CONFIG_HOME = "$workspace/.egrlab-toolchains/kicad/config"
$env:KICAD_LIBRARY_ROOT = 'C:/Program Files/KiCad/10.0/share/kicad'
```

Dla katalogu `Plytki/M1-R1-review` we **własnej kopii** wykonano:

```text
kicad-cli sch erc --format json --severity-all -o verification/erc.json eda/M1.kicad_sch
kicad-cli sch export netlist --format kicadxml -o verification/M1.xml eda/M1.kicad_sch
python src/verify_schematic.py
python src/verify_m1.py
python src/verify_pcb.py
```

Ostatni skrypt sam uruchamia DRC z `--severity-all --schematic-parity --all-track-errors --refill-zones`, po czym bada geometrię i wykonuje próby ujemne. Wyniki tego przebiegu są skopiowane do `evidence/fresh-cad/`. Nie mieszano ich z historycznymi plikami `run-*.log` autora. Ewentualne ostrzeżenie Fontconfig dotyczyło cache fontów, nie reguł elektrycznych.

## CAM, analog i interfejsy

- `evidence/analog/compare_cam.py`, `cam_geometric_diff.py` i `fresh-cam/`: świeży eksport i porównanie do plików produkcyjnych. Uwzględniono różnice metadanych i oddzielnie geometrię F/B.
- `evidence/analog/inspect_board.py`, `gndpath.py`, `geometry.json`, `paths.json`: niezależny odczyt PCB i przybliżone drogi miedzi, z ograniczeniami opisanymi w notatce.
- `evidence/power/audit_power.py`, `audit-results.json`: 126 porównań pin–sieć z XML i padami rzeczywistego PCB. Skrypt nie regeneruje źródła.
- Notatki pomocnicze podają źródła producentów. Są dodatkowym materiałem; nadrzędna klasyfikacja usterek znajduje się w głównym raporcie.

Skrypty analogu i mapy pinów zawierają zastane bezwzględne ścieżki tego stanowiska. Po przeniesieniu na inny komputer należy dostosować katalog wejściowy i uruchamiać ich kopie, aby nie zmieniać dowodów. Pakiet nie wymaga ponownego wykonania generatora PCB, aby odtworzyć pięć nowych usterek firmware.

## Integralność

`evidence/source-snapshot.json` zawiera SHA-256 531 plików wejściowych. `evidence/source-after.json` potwierdza ich niezmienność na końcu. `evidence/prior-review-verification.json` potwierdza zachowanie pierwszej recenzji względem jej manifestu. `MANIFEST-RECENZJI-ULTRA.json` obejmuje wszystkie pliki tej publikacji z wyjątkiem siebie.

Wyniki są dowodami określonych kontroli, nie deklaracją odbioru fizycznego sprzętu.
