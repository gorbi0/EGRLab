# Odtwarzanie pakietu

Wymagane: KiCad 10.0.6 (`pcbnew`, `kicad-cli`, biblioteki symboli/footprintów KiCad 10), Python KiCada z Pillow i numpy; czcionki Arial, Poppler do podglądów PDF. Freerouting 2.1.0 + JRE 21 tylko dla **nowego** routingu. Gotowe wydanie odtwarza zapisany SES, bez sieci i bez sąsiednich projektów.

Zmienne: `KICAD_LIBRARY_ROOT` (katalog share/kicad), `KICAD_CLI` (exe), `KICAD_CONFIG_HOME` (zapisywalna konfiguracja), `KICAD10_3DMODEL_DIR`, `PDFTOPPM`. Dla nowej trasy `EGRLAB_FREEROUTING` wskazuje katalog z jar i `jdk-21.0.12.1+1-jre/bin/java.exe`. Domyślne ścieżki w skryptach są lokalnymi wartościami pomocniczymi; na innym komputerze ustawić własne.

1. Rozpakować wyłącznie `P03-R2-review` do pustego katalogu.
2. KiCad Python: `python src/run_release.py`. Regeneruje schemat, kontroluje ERC/netlistę, importuje SES do nowej PCB, ponownie prowadzi kontrole i eksportuje PDF.
3. `python src/run_release.py --new-route` uruchamia router i nie musi dać tej samej geometrii. Nie używać do porównania deterministyczności; nowy routing wymaga ponownych oględzin.

Samodzielny zestaw zawiera trzy zamrożone footprinty odziedziczone po P02 w `reference/footprints`. `src/parts.py` kopiuje je z tego katalogu. Nie szuka P02 obok. Weryfikacja ma osobną kopię netlisty R1; kontroluje każdą zmianę względem niej oraz tabelę pinów nowych układów niezależnie od generatora.

Porównuje się sieci, geometrię ścieżek/padów/stref, rozmieszczenie i reguły. UUID, daty raportów i raster PDF mogą się różnić. Po zmianie jakiegokolwiek wejścia pakietu wygenerować nowy manifest i sprawdzić, że raport DRC dotyczy końcowego pliku.
