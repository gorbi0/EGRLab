# P03-R1 — recenzja Codex

Główny dokument: **RECENZJA-P03-R1.md**. Oryginalny projekt pozostaje bez zmian.

Werdykt: ograniczona R2 przed zamówieniem PCB. Dwa problemy P1: brak ustalonych stanów przed buforami i niespójny reset MCP/MCU. Cztery problemy P2: zasilanie szyny z USB, odsprzęganie TPS3808, zależność generatora od P02, nieustalone wejścia odłączonych modułów. Jedna uwaga P3: czytelność schematu.

Pakiet zawiera raport, dowody kontroli i skrypt audytu. Nie zawiera zmienionych PCB ani Gerberów. Trwające HOLD P07 i otwarte kwalifikacje P05 pozostają aktualne.

## Jak odtworzyć odczyt dowodów

Skrypt wymaga Pythona KiCad 10 z pcbnew. Nie zmienia CAD, lecz aktualizuje `evidence/independent-audit.json`:

```powershell
python audit.py 'C:\Users\tgorbacz\Documents\GORBI\Priv\Kia\Sportage\EGRLab\Plytki\P03-R1-review'
```

`fresh-netlist.xml` jest zamrożoną netlistą z czasu recenzji. Skrypt porównuje manifest wskazanego pakietu, a jego geometria pochodzi ze wskazanego PCB. Jeśli CAD ulegnie zmianie, do nowej recenzji należy odświeżyć ERC, DRC i eksport netlisty — nie łączyć starych dowodów z nową płytką:

```text
kicad-cli sch erc --severity-all --format json -o evidence/fresh-erc.json <P03.kicad_sch>
kicad-cli sch export netlist --format kicadxml -o evidence/fresh-netlist.xml <P03.kicad_sch>
kicad-cli pcb drc --format json --severity-all --all-track-errors --schematic-parity --refill-zones -o evidence/fresh-drc.json <P03.kicad_pcb>
```

`source-release-manifest.json` zamraża identyfikację ocenianego wydania. `REVIEW-MANIFEST.json` wiąże pliki recenzji ich hashami i potwierdza, czy wydanie źródłowe pozostało niezmienione. `evidence/integration-reference/` zawiera odczytane dane sąsiednich modułów i bazowego firmware.

Pomiary oscyloskopem, przymiarka części i testy zasilania nie zostały wykonane. Wynik 26/26 oznacza ponowne uruchomienie kontroli autora; nie oznacza zamknięcia siedmiu uwag recenzji. Kontrole ujemne 14/14 pochodzą z dostarczonego raportu, nie z ponownego przebiegu recenzenta.
