# Lista zakupowa 3 — szkic (1.10.2026)

**Status:** szkic do przeglądu, **nie zamawiać**. Lista 2 (`Plytki/Zakupy-2`) ma baner „do przeliczenia” po decyzjach z 29.09 (format S1, P02 R4, posiadane THT, nowe części SMD 1206). Ten szkic przelicza część, dla której są już BOM-y S1: P02 R4, P03 R6, P09 R2 i P10 R2.

| Plik | Zawartość |
|---|---|
| `ZAKUPY-3-SZKIC.md` | Tabela pozycji: ilości na płytkę, wniosek (kupić / z rejestru / dokupić / do wyboru), cena TME z 28.09, oznaczenia |
| `zakupy-3-szkic.csv` | To samo w CSV |
| `src/szkic.py` | Generator: BOM-y płytek z gałęzi git, rejestr `Zamowione/zamowione.csv`, ceny z `Zakupy-2/src/tme.py` |

Odtworzenie (z katalogu repozytorium, po `git fetch origin`): `python3 Plytki/Zakupy-3-szkic/src/szkic.py`.

## Wynik

89 pozycji:
- **5 do wyboru typu:** kątowe obudowane IDC 2×10 / 2×8 / 2×5 i kątowe goldpiny 1×13 / 1×9;
- **43 do kupienia;**
- **4 częściowo z rejestru:**
  - MF0207 10K: 16 potrzebnych przy 7 w rejestrze;
  - MF0207 100K: 13 potrzebnych przy 7;
  - K104: 12 potrzebnych przy 5;
  - SN74HC139N: 2 potrzebne przy 1;
- **34 z rejestru;**
- **reszta** to przewody i części posiadane.

Ceny z 28.09 są tylko dla 16 pozycji do kupienia (ok. 74 zł netto bez minimów i wysyłki). Nowe części S1 (rezystory i kondensatory 1206, złącza J_BP, listwy) nie mają jeszcze ceny.

Grupowanie:
- rezystory i kondensatory 1206 oraz posiadane MF0207 — po wartości; P09/P10 podają w BOM tylko „SMD 1206 …”, a P02/P03 mają Yageo RC1206 i Murata GRM31;
- pozostałe części — po numerze;
- gniazda, dystanse i zworki ukryte w opisach BOM są dopisane jak w liście 2.

## Ograniczenia

- „Z rejestru” znaczy tylko, że w rejestrze jest tyle sztuk. Część z nich mogła być przewidziana dla płytek spoza szkicu (P04, P05, P06, P08); przydział ustali lista wiążąca.
- Ceny i stany TME trzeba sprawdzić w przeglądarce: Cloudflare, sposób w `docs/pamiec-claude/tme-mouser-lookup.md`.
- Poza szkicem:
  - P00 R3 i P04 R2.2 (bez zmian względem listy 2);
  - P05 R3 (schemat w toku w chmurze), P06, P08 i P11 (czekają na rewizje S1);
  - przewody i drobne części mechaniczne.

## Dalej

Lista wiążąca powstanie po recenzji PR-ów P03, P09 i P10 oraz po schemacie P05 R3. Najpierw wybór typów złączy i listew, sprawdzenie cen w TME, potem przydział rejestru między wszystkie płytki.
