# Lista zakupowa 4 — kandydaci MPN dla pozycji otwartych (zadanie dla sesji w chmurze, 4.10.2026)

**Ustawienia sesji:** Sonnet 5.5, wysiłek medium (Opus high, jeśli dostępny budżet). Baza: `origin/zamowienie-s1`. Gałąź zadania: `zakupy-4-kandydaci`, wynik jako PR do `zamowienie-s1`.

**Cel:** użytkownik zdecydował 4.10, że konkretne kody proponuje Claude, a on zatwierdza jedną listę. Sklepy (TME, Mouser — Cloudflare) i ceny sprawdza sesja lokalna; ta sesja wybiera kandydatów **z kart producentów** i sprawdza ich zgodność z footprintami i wymaganiami.

**Źródła:** `Plytki/Zakupy-3-szkic/ZAKUPY-3-SZKIC.md` (pozycje „do wyboru”), `docs/ZAKUPY.md` wydań P05 R3 i P06 R2, `Plytki/P11-S1-przygotowanie/README.md` (decyzje 4.10), footprinty w `eda/` wydań. Pamięć: `MEMORY.md`, `egrlab-purchasing-state.md`, `tme-mouser-lookup.md` (asortyment TME: m.in. brak Würth, IDC Amphenol FCI T821).

## Zasady

`docs/CHMURA.md` 1–9. Nie zmieniać pakietów płytek. Jeśli sieć w chmurze nie wpuszcza na strony producentów, zapisać to w PR i oprzeć się na kartach w repozytorium oraz na wiedzy — z jawnym oznaczeniem „do sprawdzenia”.

## Pozycje

Dla każdej: 1 kandydat główny + 1–2 zamienniki (różni producenci), parametry kluczowe, link do karty, zgodność z footprintem (wymiary z karty wobec `.kicad_mod`), uwagi montażowe.

1. **SW1 P05:** E-Switch 100DP1T1B3M6REH (tuleja B3 z gwintem + nakrętka; B4 jest standardem dla M6) — czy B3 z M6 jest dostępna i jaki ma czas; zamiennik o tym samym rastrze, gdyby nie było.
2. **BYPASS P06 (panel):** DPDT ON-ON ≥ 10 A DC przy 12–30 V, oczka lutownicze 2,5 mm², tuleja z nakrętką (NKK S6A nie).
3. **Porty L1 / L2 / TEST:** Amphenol AT04-12PA / PB / PC w wersji panelowej (kołnierz) + wtyki AT06-12SA / SB / SC dla adapterów, styki do 2,5 mm² dla prądu silnika i 0,5–1 mm² dla sygnałów, zaślepki, klin.
4. **Przyciski panelu ze stykami złoconymi (P11-7):** STOP zatrzaskowy (NC), ARM, MARK, stacyjka / kluczyk 2-pozycyjny; średnica otworu 16 / 19 / 22 mm; dopuszczenie do ok. 27 µA / 3 V.
5. **Złącza IDC kątowe obudowane 2×10 / 2×8 / 2×5 (złocone)** i kątowe goldpiny 1×13 / 1×9 / 1×7 — dostępne w TME (Amphenol FCI, Harwin, Ninigi itp.); zgodność z footprintami J_BP i J_SV.
6. **C1 P05 / C3 P06 EEUFR1C221** (220 µF 16 V) — potwierdzić średnicę, raster i wysokość wobec footprintu i limitu 16,5 mm; zamiennik low-ESR.
7. **P05 C35 10 µF, P06 C17 100 nF** (nowe 4.10) — kody 1206 zgodne z resztą listy.

## Wynik

`Plytki/Zakupy-4-kandydaci/KANDYDACI.md` + `kandydaci.csv` (pozycja, płytka, ilość, MPN główny, zamienniki, producent, karta, zgodność footprintu, uwagi). Po PR zakończyć pracę.
