# Kontrola plików P02-R2

25.09.2026. KiCad 10.0.6, Freerouting 2.1.0 / Java 21. Status: **do recenzji Opusa**. Sprzęt, przymiarka i odbiór elektryczny: **NIE ZBADANO**.

| Kontrola | Wynik i dowód |
|---|---|
| ERC, wszystkie ważności | 0, cztery arkusze A3; `erc.json` |
| Netlista vs jawny kontrakt części | 208/208 pinów, 74 części, 47 sieci; `schematic-check.json` |
| DRC, wszystkie ważności | 0 naruszeń / 0 niepołączonych / 0 błędów zgodności ze schematem; `drc.json` |
| Kontrole gotowej PCB | 29/29; `pcb-checks.json` |
| Kontrole elektryczne | 8/8; `electrical-checks.json` |
| Ograniczenie zmian względem R1 | 4/4; `revision-checks.json` |
| Próby ujemne na rzeczywistej PCB | 10/10 wykryte; `negative-controls.json` |
| Próby ujemne na netliście/wartościach | 5/5 wykryte; `electrical-negative-controls.json` |
| Kontrola wzrokowa | Wszystkie 9 stron końcowych PDF; `visual-review.json` z SHA256 |

## Kontrole dodatkowe

- Każdy pad PCB, footprint i wartość zgodne z eksportowaną netlistą. 72 części na P02, R17 poza PCB, C16 na adapterze U5, cztery otwory M3.
- Tor VPROT i powrót GND dla 5 A: przekroje miedzi, szerokości ścieżek, płaszczyzna masy, zablokowana szyna HOLD_STORE i odległość F1 od banku.
- Anody D1/D2, pinouty LV, górne rezystory dzielników przy źródłach, odsprzęganie, odstępy banku, kotwy wiązek i nadruki.
- TP3 wyłącznie za R20. Filtry C14/C15 przed R18/R19; R8/R11 przy wejściach komparatorów.
- Tylko cztery dodane części: R18, R19, R20, C16. Względem R1 przestawiono wyłącznie R8, R11, TP3; sprawdzono jawną listę zmian pinów i wartości. Nie oznacza to identyczności każdej ścieżki: część sygnałową ponownie trasowano.

Pełne 29 sprawdzeń i mierzone wielkości: `pcb-checks.json`. Nie użyto wykluczeń DRC. U5.9/U5.12 mają pełne połączenie do masy, ponieważ termiki w tej geometrii były niekompletne.

## Model elektryczny

`check_electrical.py` odczytuje wartości i połączenia z eksportu KiCada. Dla obu komparatorów enumeruje po 1024 kombinacje zadeklarowanych tolerancji, offsetu, prądów wejściowych, upływu wyjścia, VOL i zasilania. Źródła i założenia: `docs/HOLD-ANALIZA.md`.

| Wielkość | Wynik modelu |
|---|---|
| Bank: próg załączenia / wyłączenia | 9,805…10,474 V / 9,612…10,252 V |
| VPROT: próg załączenia / wyłączenia | 11,810…12,623 V / 11,573…12,349 V |
| Minimalny natychmiastowy skok sprzężenia | 23,355 mV |
| Podtrzymanie: Cmin, start 9,5 V, przyjęte straty | 85,38 ms; straty wymagają potwierdzenia pomiarem |
| Energia banku, C +20%, 32 V | 40,55 J |
| Rozładowanie do 1 V przez R1, najwolniejszy narożnik | 1303 s, około 21,7 min |
| Zwarcie TP3 przy 32 V, najgorszy R20 | 33,91 mA / 1,085 W |

Przedziały progów dotyczą różnych egzemplarzy i tolerancji. Nie odejmować końców dwóch niezależnych przedziałów jako histerezy jednego układu: histereza jest obliczana parami dla tego samego narożnika. Zakres obliczeń: 0…50°C wewnątrz obudowy; inne temperatury wymagają ponownego modelu.

Nie wykonano symulacji SPICE ani pomiarów dynamiki. DC i RC nie dowodzą braku oscylacji od pasożytów PCB. HOLD_READY nie mierzy Ceff i nie wykrywa przerwanego F1. Ręczna kwalifikacja 15 s wymaga wcześniejszego odbioru banku; firmware jej nie realizuje.

## Próby z celowymi błędami

Na kopiach PCB zmieniano: przewężenie VPROT, ścieżkę w korytarzu powrotu, niezablokowaną miedź banku, odsunięte odsprzęganie, oznaczenie w obrysie obcej części, położenie otworu, opisy LV, szerokość gałęzi VPROT, TP3 połączony z surowym bankiem oraz ominięty rezystor separujący filtr. Wszystkie dziesięć zmian wykryły właściwe kontrole. Kopie robocze nie wchodzą do ZIP; wyniki są zachowane.

Pięć mutacji elektrycznych sprawdza wykrywanie starych wartości progów, kondensatora na wejściu sprzężenia, niechronionego TP3 i przywróconego kondensatora 100 nF. Dokładne nazwy i wyniki: `electrical-negative-controls.json`.

## Świeżość i odtwarzanie

`src/run_release.py`: ERC → netlista → kontrole schematu i elektryczne → różnice R1/R2 → świeży DRC i kontrole PCB → próby ujemne → eksporty natywne → PDF → obrazy stron. Logi: `run-*.log`.

`pcb-checks.json` wiąże wynik z SHA płytki; `drc.provenance.json` także z CAD, bibliotekami, regułami, skryptami, kontraktem części i netlistą. Zmiana wejścia wymaga świeżej kontroli. Raport elektryczny zapisuje hashe swojej netlisty, części i skryptu.

Wizualnie sprawdzono opisy i przewody wszystkich arkuszy, polaryzację banku, TP3/R20, nadruki, odbicie spodu, warstwy miedzi i układ stron. Rysunki 1:1 mają belkę 100 mm; skala wydruku zależy od drukarki. Modele 3D pokazują gabaryty, bez kompletnej obudowy i obejm.

Po inspekcji PDF `src/package_review.py` sprawdza raporty i hashe, tworzy manifest i ZIP. Manifest nie obejmuje siebie, kopii mutacji ani cache narzędzi.

## Otwarte przed zamówieniem i odbiorem

F2/F3/F4: zatwierdzenie wkładek DC. Mechanika: przymiarka złączy, oprawek, adaptera i banku; mocowanie banku do obudowy, osłona lutów, blacha R17. Elektryka: `ODBIOR.md` — progi, rampy i zapady, Ceff, ESR, 50 ms przy 6 W, temperatura, odsprzęganie i kontrolowane zwarcia. Te pozycje nie mają wyniku PASS.
