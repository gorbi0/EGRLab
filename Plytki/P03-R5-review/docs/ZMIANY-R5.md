# P03-R5 — odpowiedź na recenzję R4

| Uwaga | Wdrożenie | Dowód |
|---|---|---|
| Wolne wejście U4 LVC1G07 | SN74LVC1G37DBVR, Schmitt + open-drain, te same piny 1 NC / 2 A / 3 GND / 4 Y / 5 VCC. R13 pozostaje 10 kΩ | BOM, POWER, netlista, mutacja cofająca U4 do LVC1G07 |
| LOW bez CORE | Wspólne wydanie P04-R2.2: R17 10 kΩ zamiast 100 kΩ. Zamrożona mapa części sąsiada | `verify_reset.py`, budżet 30 µA × 10,1 kΩ = 0,303 V < 0,8 V |
| Nieuprawnione VOL 0,1 V | Obliczenie z 0,4 V, tolerancjami R34/R35 i założeniem tolerancji rezystora EN modułu | `ZASILANIE-RESET.md`, `reset-budget.json` |
| Limit 36 pF i czas 17 ns | Usunięta deklaracja gwarancji. R41 220 Ω pozostaje; pomiar obu zboczy na P04 U9.5 z uwzględnieniem sondy | `ODBIOR.md` |
| Montaż rezystorów | R41 jawnie wyjątkiem SMD 1206; reszta THT DIN0207 | `MECHANIKA.md` |
| Ryzyko przypadkowych zmian PCB | Zamrożone PCB i części R4; ścisła kontrola różnic, również geometryczne XOR wylewek | `check_revision.py` |
| Proces | Krótki kontrakt resetu obejmujący zanik zasilania, upływności, progi i zbocza | `KONTRAKT-RESET.md`; w obu pakietach ten sam tekst |
| Odtwarzanie projektu | Powtórny eksport schematu zachowuje ustawienia PCB; BOM zakupowy jest regenerowany z aktualnych części | `audit_rebuild.py` sprawdza ponowny eksport i odtworzenie w pustym katalogu; `check_tables.py` porównuje zakupy z BOM |

R4 i wcześniejsze wydania nie są modyfikowane. Nie dodano elementów ani nie zmieniono tras. Historyczne `ZMIANY-R2/R3/R4.md` opisują dawne wydania; aktualne wymagania zawiera R5.

SN74LVC1G37DBVR jest aktywnym kodem TI. Oferta DigiKey 296-SN74LVC1G37DBVRCT-ND potwierdza sprzedaż na sztuki (stan magazynu sprawdzić przy zakupie): [TI](https://www.ti.com/product/SN74LVC1G37/part-details/SN74LVC1G37DBVR), [DigiKey](https://www.digikey.com/en/products/detail/texas-instruments/SN74LVC1G37DBVR/27634802). Nie oznacza to zakupu ani rezerwacji części.

Mechanika B2B nadal ma osobny warunek odbioru — `B2B-STATUS.md`. Prace nad nią nie zmieniły footprintów ani P05.
