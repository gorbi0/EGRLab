# Ponowny przegląd R2

Autor ponownie sprawdził Q1/Q2 GDS i D9, domyślny OFF, Q4 PNP, poziom ON,
prąd/energię bramki, start/stop, wpływ na SAFE, MPN, footprinty i wiązki.
To NIE JEST niezależna recenzja R2. Opus oceniał R1, nie tę poprawkę.

| ID | Stan | Do zamknięcia |
|---|---|---|
| R1-01 | POPRAWIONE_W_PROJEKCIE | Recenzja nowego toru, następnie hotplug/OVP na stole. |
| R1-02 | POPRAWIONE_W_PROJEKCIE | Odbiór protokołu, pomiar rzeczywistych zboczy. |
| R1-03 | POPRAWIONE_W_PROJEKCIE, fit otwarty | Przewód w PTH3,2 bez obcinania drutów; lut poprawnie zwilżony. |
| R1-04 | DOBÓR_ZAMKNIĘTY | Para1757019↔1786174 u producenta; przy montażu pin1/oznaczenia. |
| E-02 | OTWARTE przed layoutem | Niezależna recenzja delty Q2/C5/C6/D9 oraz granic modelu. |
| M-01 | OTWARTE przed layoutem | Rysunek mocowań dwóch radiatorów, miejsca na większy Q2 i C6. |
| B-01 | OTWARTE przed layoutem | MPN/dostępność/gabaryty, zwłaszcza H4,C1,C6 i próbka przewodu. |
| L-01 | NIE WYKONANO | Layout2L, DRC, Gerbery, wiercenia. |
| H-01 | NIE WYKONANO | Pełne100µs, dV/dt, SOA przy starcie/OVP, termika i reszta ODBIOR. |
| P07 | HOLD | Czekamy na moduł BTS7960. |

Recenzent: sprawdzić granice parametrów modelu, wyłączenie Q2 przez Q4 i budżet
detektor→ENABLE. Oddzielnie ocenić duży prąd przy OVP z Q1 już włączonym.
Nie zmieniać progów testu, aby dostać PASS. Zachować każdy niezaliczony przypadek.

`verification/legacy-static-model.json` używa STARYCH wartości bramki, nie jest
dowodem nowych czasów ani napięcia ON. Detektor/AUX/SAFE pozostały takie same
(XML). Nowe DC bramki jest w bounds.json, dynamika w dynamics.json.
