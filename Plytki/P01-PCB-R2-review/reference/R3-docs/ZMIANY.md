# R2 → R3 — mała delta i sposób zamknięcia uwag

| Uwaga | Wprowadzona zmiana | Dowód / dalszy odbiór |
|---|---|---|
| R2-01, przerwa 10–27ms po krótkim błędzie | Ustalono rozdział: P01 chroni i wyłącza silnik, P02 podtrzymuje pomiary. Kontrakt 50ms/6W na wejściu przetwornic, obwód 3×22000µF przez ładowanie rezystorowe i diody. | recovery.json i hold-budget.json. Rzeczywiste P02 i pomiary jeszcze przed nami. |
| R2-02, mierzalność | LK1 przed całym VPROT, pola siłowe i Kelvin; rozdzielenie prób małego ładunku i dużego prądu. Budżet niepewności i reguły PASS/FAIL w METROLOGIA. | XML, footprint, test obejścia LK1; odbiór stanowiska przed oceną PCB. |
| R2-02, powerbank | Nie stosować masy DHO804 na SOURCE. Pozostać przy właściwym pomiarze różnicowym i uziemieniu zgodnym z instrukcją Rigola. | Instrukcja DHO800 §1.1. |
| R2-03, BAT | Zamieniono strony 1757019/1786174 we wszystkich bieżących dokumentach wiązki i BOM. | Brak zmiany pinów J7: 1=BAT_FUSED, 2=GND. |
| R2-04, C6 | WIMA MKS2D041001K00JO00, 1µF/100V/±5%, P5, korpus 7,2×7,2/H13mm. | Karta WIMA, oferta detaliczna TME, footprint i ponowne scenariusze RC. |
| R2-05, J7/TP | Termiki 1,2mm/gap0,3; radiator SK129-63STS z footprintem P25,4/D2,8; wymogi lokalizacji TP1/TP2 i LK1. | Właściwe rozmieszczenie oraz wypełnienie miedzi do sprawdzenia w layout/DRC. |

Q1.2 i tab Q1 to teraz **P01_Q1_DRAIN**. LK1.1=DRAIN, LK1.2=VPROT.
Wszystkie wcześniejsze odgałęzienia VPROT, w tym C5, pozostają za LK1.
LK1 nie jest zworą logiczną ani elementem do przełączania pod obciążeniem.
Zachowano Q2 P-MOS, D9, C5/C6 nominalnie, R21/R22/R27 i cały tor AUX/OVP/UVLO/SAFE.
`design/changes.json` to pełna jawna delta względem zamrożonej bazy 6.1;
`verification/r3-checks.json` sprawdza osobno wąską różnicę względem XML R2.

Znany błąd R1 dalej jest wykrywany. Nie wracamy do jego szybszego restartu.
Uzupełnienie testu powrotu ujawniło, że przypadek Vth=1V nie zawsze traci zasilanie:
to zależy także od zacisku Q2 i długości impulsu. Pierwsza zbyt szeroka asercja
„każdy przypadek spada poniżej 7V” była błędem oczekiwania testu. Wynik zachowano
w recovery-initial-expectation.json. Nie zmieniono progów ochrony P01; wymaganie
jest konkretne: wykryć przypadki utraty zasilania bez rezerwy i sprawdzić bufor
w określonej dziedzinie. Wyniku modelu nie uogólniać na wszystkie egzemplarze.
