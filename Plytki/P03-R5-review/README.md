# EGRLab P03-R5 — CORE

28.09.2026. Poprawki po recenzji P03-R4 Codexa, na zlecenie użytkownika.
**U4 = SN74LVC1G37DBVR, wejście Schmitta i wyjście open-drain.** U6 = SN74LVC1G17DBVR pozostaje. Miedź, pady, wiercenia i położenia części mają pozostać identyczne z R4; zmienia się wartość U4 i numer wydania na nadruku. Dowód: `verification/revision-checks.json`.

Współpracujący moduł: **P04-R2.2, R17 = 10 kΩ**. Poprzednie P03-R4 i P04-R2.1 pozostawiono bez zmian.

Start: [zmiany R5](docs/ZMIANY-R5.md), [zasilanie i reset](docs/ZASILANIE-RESET.md), [odbiór](docs/ODBIOR.md), [mechanika B2B](docs/B2B-STATUS.md).

- Schemat i projekt KiCad: `eda/P03.kicad_sch`, `eda/P03.kicad_pcb`, `eda/P03.kicad_pro`.
- PDF: `output/pdf/P03-R5-schemat.pdf` (5 arkuszy), `output/pdf/P03-R5-PCB.pdf` (4 strony).
- Zakupy: `docs/BOM.csv`; **U4 kupować z końcówką DBVR (SOT-23-5), nie DCKR**.
- Kontrole: `verification/QA.md`; obliczenia i mutacje interfejsu: `verification/reset-budget.json`.
- Odtworzenie: `docs/ODTWARZANIE.md`; źródła i poprzednia geometria w pakiecie.

Status: poprawki elektryczne wygenerowane i sprawdzone w CAD. Sprzęt NIE ZBADANO. B2B P03–P05 wymaga zamknięcia przekroju/przymiarki przed zamówieniem; ta paczka nie zawiera CAM do produkcji. P07 nadal HOLD. Pozostałe uwagi P05 i integracja firmware poza zakresem R5.
