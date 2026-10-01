# Lista zakupowa 3 — szkic (1.10.2026)

**Status:** szkic do przeglądu, **nie zamawiać**. Lista 2 (`Plytki/Zakupy-2`) ma baner „do przeliczenia” po decyzjach z 29.09 (format S1, P02 R4, posiadane THT, nowe części SMD 1206). Ten szkic przelicza część, dla której są już BOM-y S1: P02 R4, P03 R6, P09 R2, P10 R2 i (od 1.10) P05 R3.

| Plik | Zawartość |
|---|---|
| `ZAKUPY-3-SZKIC.md` | Tabela pozycji: ilości na płytkę, wniosek (kupić / z rejestru / dokupić / do wyboru), cena TME z 28.09, oznaczenia |
| `zakupy-3-szkic.csv` | To samo w CSV |
| `src/szkic.py` | Generator: BOM-y płytek z gałęzi git, rejestr `Zamowione/zamowione.csv`, ceny z `Zakupy-2/src/tme.py` |

Odtworzenie (z katalogu repozytorium, po `git fetch origin`): `python3 Plytki/Zakupy-3-szkic/src/szkic.py`.

## Wynik (1.10.2026, po decyzjach użytkownika)

115 pozycji:
- **6 do wyboru typu:** kątowe obudowane IDC 2×10 / 2×8 / 2×5, kątowe goldpiny 1×13 / 1×9 oraz SW1 P05 (E-Switch 100 kątowy M6 — kod tulei i dostępność);
- **67 do kupienia;**
- **4 częściowo z rejestru** (MF0207 10K: 16 potrzebnych przy 7; 100K: 13 przy 7; K104: 12 przy 5; SN74HC139N: 2 przy 1) — rejestr zużywa najpierw P02 R4;
- **36 z rejestru;**
- reszta to przewody i części posiadane.

Zmiany 1.10: P09 R2 bez gniazd ZL262-9SG i dystansów M2,5 (moduły MAX31856 lutowane wprost), P05 R3 dodany (schemat z PR #7 po poprawkach: kondensatory foliowe jako nowe 1206, C1 220 µF, SW1 E-Switch M6), 1N4148 P05 dopasowany do rejestru (Kamami 1187768). Ceny z 28.09 są tylko dla 18 pozycji do kupienia (ok. 73 zł netto bez minimów i wysyłki).

## Ograniczenia

- „Z rejestru” znaczy tylko, że w rejestrze jest tyle sztuk. Część z nich mogła być przewidziana dla płytek spoza szkicu (P04, P05, P06, P08); przydział ustali lista wiążąca.
- Ceny i stany TME trzeba sprawdzić w przeglądarce: Cloudflare, sposób w `docs/pamiec-claude/tme-mouser-lookup.md`.
- Poza szkicem:
  - P00 R3 i P04 R2.2 (bez zmian względem listy 2);
  - P06, P08 i P11 (czekają na rewizje S1; P06 z decyzjami 1.10: klasa 2/3, bocznik 2512 Kelvin, BYPASS na panelu, C3 220 µF);
  - przewody i drobne części mechaniczne.

## Dalej

Lista wiążąca powstanie po scaleniu P03 R6 (trasowanie w toku) i rewizjach S1 P06 i P11. Najpierw wybór typów złączy i listew oraz kodu E-Switch, sprawdzenie cen w TME / Mouser, potem przydział rejestru między wszystkie płytki (P02 R4 ma pierwszeństwo — zamówiona).
