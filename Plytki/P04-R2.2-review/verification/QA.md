# P04-R2.2 — wyniki weryfikacji 28.09.2026

Status: korekta R17 dla P03-R5, CAD gotowy do recenzji. **Sprzęt NIE ZBADANO; brak CAM do produkcji.** Historyczne wyniki przeniesiono do `reference/previous-verification`.

| Kontrola końcowych plików | Wynik | Raport |
|---|---|---|
| ERC; 98 części / 355 pinów | 0 naruszeń, 0 różnic | schematic-check.json, erc.json |
| Natywny DRC / niepołączone / zgodność schematu | 0 / 0 / 0 | drc.json, drc.provenance.json |
| PCB i próby usterek | 26/26; 11/11 wykrytych | pcb-checks.json |
| Logika z netlisty | 22/22; 131072 kombinacje, 14/14 mutacji | electrical-checks.json |
| Wartości i interfejsy | 11/11; 24/24 mutacji | value-checks.json |
| Budżet resetu | 7/7; 4/4 mutacje wykryte | reset-budget.json |
| Zakres R2.1 → R2.2 | 10/10; wyłącznie R17 i numer nadruku, XOR miedzi 0 | revision-checks.json |
| Odtworzenie w pustym katalogu | PASS; schemat, BOM, sieci, geometria i reguły zgodne; jedna połączona masa | independent-rebuild.json |
| Oględziny PDF | 6 stron schematu + 4 strony PCB obejrzane | visual-qa.json |
| Zachowanie oryginałów i zgodność pary | PASS | source-integrity.json |

R17=10 kΩ ±1% przed U9.5. R30 za U9 pozostaje 100 kΩ. Przy CORE OFF obliczone graniczne 0,303 V jest poniżej VIL=0,8 V; dla aktywnego U6/R41 graniczne HIGH przekracza 2,34 V. Szczegóły i źródła: `docs/KONTRAKT-RESET.md`.

Ścieżki, pady, wiercenia, strefy i rozmieszczenie zachowano. PCB wykonana według R2 wymaga tylko montażu R17=10 kΩ; nie wymaga nowej miedzi z powodu tej korekty. Model logiczny nie kwalifikuje czasu watchdoga, drgań ARM ani zbocza resetu. Próby na stole, przymiarka M01 i integracja z P03-R5 nadal wymagają wykonania. P07 HOLD.

Odtworzenie: `docs/ODTWARZANIE-R2.2.md`; pakowanie sprawdza zgodność hashy źródeł i PDF z wynikami kontroli.
