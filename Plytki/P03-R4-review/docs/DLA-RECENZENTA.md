# Kolejność recenzji P03 (R4)

*R4 (27.09.2026): bufor Schmitta U6 w resecie do P04, decyzja użytkownika po końcowej recenzji R2 (`reference/RECENZJA-P03-R2.md`, P3-01). Poza obszarem przy J4 miedź = R3 (`verification/revision-checks.json`). Historia: `ZMIANY-R2.md`, `ZMIANY-R3.md`.*

1. `ZMIANY-R4.md`: zakres zmiany i punkty sporne.
2. `ZASILANIE-RESET.md`, sekcja R4: progi U6, R41, obciążenie taśmą H_SAFE, zbocze i opóźnienia na P04. Liczby sprawdzić w `reference/datasheets/SN74LVC1G17.pdf` i w karcie 74LVC125A (Nexperia).
3. `output/pdf/P03-R4-schemat.pdf`: arkusz POWER (2/5, U6/R41/C15) i LINKS (5/5, J4.15 = SUP_N_OUT).
4. Layout przy J4: blok R4 w `src/route_critical.py`, strony 2–4 `output/pdf/P03-R4-PCB.pdf`, dokładny bilans miedzi w `verification/revision-checks.json`. Sprawdzić: przelotki HW_ARMED_CORE (7,5; 73,76) i (13,6; 78,69), dostęp lutownicy do U6/C15/R41 przy obudowie J4 i adapterze U12, pętlę odsprzęgania C15 (GND przez przelotki i wylewki), oznaczenie R41 w szczelinie.
5. `verification/QA.md`, następnie świeże uruchomienie testów według `ODTWARZANIE.md`. Nie opierać oceny wyłącznie na liczniku PASS.
6. `ODBIOR.md`: nowe próby U6/R41 i zbocza SUP_N_OUT na P04. `MECHANIKA.md`: przymiarka B2B i kolejność montażu pozostają otwarte.

Zmiana nie obejmuje innych płytek ani bazowego firmware. P04 odbiera SUP_N_OUT na tym samym pinie J2.15 co wcześniej SUP_N; mapa złączy P04-R2.1 bez zmian. U4/U5/U6/Q1 w obudowach SOT23, C12–C15 i R41 w 1206, bez QFN/BGA.
