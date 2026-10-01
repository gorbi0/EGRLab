# Lista zakupowa 3 — szkic (1.10.2026)

**Status:** szkic do przeglądu, **nie zamawiać**. Lista 2 (`Plytki/Zakupy-2`) ma baner „do przeliczenia” po decyzjach z 29.09 (format S1, P02 R4, posiadane THT, nowe części SMD 1206). Ten szkic przelicza część, dla której są już BOM-y S1: P02 R4, P03 R6, P09 R2, P10 R2, P05 R3 i (od 1.10 wieczorem) P06 R2.

| Plik | Zawartość |
|---|---|
| `ZAKUPY-3-SZKIC.md` | Tabela pozycji: ilości na płytkę, wniosek (kupić / z rejestru / dokupić / do wyboru), cena TME z 28.09, oznaczenia |
| `zakupy-3-szkic.csv` | To samo w CSV |
| `src/szkic.py` | Generator: BOM-y płytek z gałęzi git, rejestr `Zamowione/zamowione.csv`, ceny z `Zakupy-2/src/tme.py` |

Odtworzenie (z katalogu repozytorium, po `git fetch origin`): `python3 Plytki/Zakupy-3-szkic/src/szkic.py`.

## Wynik (1.10.2026 wieczorem, z P06 R2)

131 pozycji:
- **8 do wyboru typu:** kątowe obudowane IDC 2×10 / 2×8 / 2×5, kątowe goldpiny 1×13 / 1×9 / 1×7, SW1 P05 (E-Switch 100 kątowy M6 — kod tulei i dostępność) i SW1 P06 (przełącznik BYPASS na panelu, DPDT ON-ON ≥ 10 A DC — MPN do wyboru);
- **77 do kupienia;**
- **4 częściowo z rejestru** (MF0207 10K, 100K, K104, SN74HC139N — rejestr zużywa najpierw P02 R4);
- **41 z rejestru** (z P06: INA240A2, MCP1525, MCP120 ×2, 74LVC125 ×2, MCP6022, MCP3201, MCP1702, SN74HC08N — przydział do sprawdzenia przy liście wiążącej);
- reszta to przewody i części posiadane.

Zmiany 1.10 wieczorem: P06 R2 dodany (BOM z gałęzi `p06-r2-pcb`: bocznik WSK25125L000FEA po przeglądzie karty, R21 PR02 39 Ω, R6 KNP01U-1R i C3 EEUFR1C221 jak w P05, C8 od spodu z uwagą grubości ≤ 1,5 mm), P05 R3 czytany z gałęzi PCB `p05-r3-pcb` (uwagi grubości kondensatorów od spodu). Wcześniej 1.10: P09 R2 bez gniazd ZL262-9SG i dystansów M2,5, P05 R3 dodany ze schematu z PR #7, 1N4148 P05 dopasowany do rejestru (Kamami 1187768). Ceny z 28.09 są tylko dla 18 pozycji do kupienia.

## Ograniczenia

- „Z rejestru” znaczy tylko, że w rejestrze jest tyle sztuk. Część z nich mogła być przewidziana dla płytek spoza szkicu (P04, P05, P06, P08); przydział ustali lista wiążąca.
- Ceny i stany TME trzeba sprawdzić w przeglądarce: Cloudflare, sposób w `docs/pamiec-claude/tme-mouser-lookup.md`.
- Poza szkicem:
  - P00 R3 i P04 R2.2 (bez zmian względem listy 2);
  - P08 i P11 (czekają na rewizje S1);
  - przewody i drobne części mechaniczne.

## Dalej

Lista wiążąca powstanie po scaleniu P05 R3 i P06 R2 (PCB na gałęziach) i rewizji S1 P11. Najpierw wybór typów złączy i listew oraz kodu E-Switch, sprawdzenie cen w TME / Mouser, potem przydział rejestru między wszystkie płytki (P02 R4 ma pierwszeństwo — zamówiona).
