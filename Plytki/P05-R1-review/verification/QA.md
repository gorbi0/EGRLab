# Odtwarzanie i dowody P05-R1

Narzędzia: KiCad10.0.6 (`pcbnew` i `kicad-cli` z tej samej instalacji), Python3.11 zPillow/NumPy, drugiPython zReportLab, Poppler `pdftoppm`, Freerouting2.1.0 zJRE21 tylko dla nowego trasowania. Wszystkie polecenia uruchamiać w środowisku z tymi wersjami.

Ustaw zmienne `KICAD_LIBRARY_ROOT` (katalogshare/kicad), `KICAD_CLI`, `KICAD_CONFIG_HOME` (zapisywalny profil), `EGRLAB_DOC_PYTHON` oraz `PDFTOPPM`. Dla nowego trasowania także `EGRLAB_FREEROUTING`.

```powershell
& $KicadPython src/run_release.py --no-package
& $KicadPython src/clean_rebuild.py
# Po ręcznej ocenie wszystkich PDF i zapisaniu visual-qa.json:
& $KicadPython src/package_release.py
```

`$KicadPython` oznacza Python zmodułempcbnew. Ścieżki są przykładami poleceń, nie zapisanymi danymi użytkownika. `run_release.py` odtwarza schemat i PCB zdołączonegoSES; nie wymaga ponownego uruchomienia autoroutera. SES jest wejściem geometrycznym, bo nowy przebieg routera może dać inną płytkę. Własne połączenia są zapisane w `route_critical.py` i `completion-routes.json`, a nie jako niewidoczna ręczna poprawka.

Kolejność: generacja schematu → eksportXML/ERC → niezależne testy elektryczne → rozmieszczenie i połączenia krytyczne → importSES → uzupełnienia → wypełnienieGND → opisy → przywrócenie regułDRC → natywneDRC/parity → testy geometrii/mutacji → PDF → kontrola wizualna → odtworzenie w nowym katalogu → ZIP i sprawdzenie hashów.

Raport `drc.provenance.json` obejmuje źródła, schemat, PCB, biblioteki i zapisane wejścia. Zmiana po weryfikacji unieważnia pakowanie. `clean-rebuild.json` porównuje semantyczny odcisk geometrii bez losowychUUID. `visual-qa.json` wskazuje konkretne hashe dwóchPDF obejrzanych strona po stronie. ZIP ma własny manifest i plikSHA256.

Wartości0 wDRC oznaczają brak zgłoszeń we wszystkich poziomach ważności, brak niepołączonych sieci i brak rozbieżności schemat–PCB. Nie ma listy wyłączeńDRC. Celowo uszkodzone kopie netlisty/PCB istnieją tylko w pamięci testów i nie są paczką montażową.

Weryfikacja obejmuje wyprowadzenia, logikę, proste granice tolerancji i geometrię. Nie wykonano symulacjiSPICE całegoP05 ani pomiarów sprzętu. Warunkiuruchomienia i kryteriaanalogowe są w `docs/ODBIOR.md`.

`input/routing-additions.json` przechowuje jawne połączenie GND komparatora oraz przelotki łączące lokalne pola masy. `prune_dangling.py` usuwa wyłącznie nieblokowane odgałęzienia wskazane przez natywne DRC; przed zastąpieniem PCB sprawdza kompletną łączność na pliku kandydującym. Raport usuniętych odcinków: `pruned-stubs.json`. Nowe trasowanie wymaga ponownej oceny tych uzupełnień i kontroli wizualnej — nie jest automatycznie nowym wydaniem.
