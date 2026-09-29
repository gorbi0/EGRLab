# Kolejność recenzji P03-R2

1. `ZMIANY-R2.md`: siedem ustaleń recenzji R1 i dowody poprawek.
2. `ZASILANIE-RESET.md`: wspólne EN/MCP/P04, obciążenie EN oraz kierunek Q1/U5. Sprawdzić piny w podlinkowanych notach producentów.
3. Pięć arkuszy `output/pdf/P03-R2-schemat.pdf`, szczególnie POWER i bufory `_SRC`.
4. `verification/QA.md`, następnie świeże uruchomienie testów według `ODTWARZANIE.md`. Nie opierać oceny wyłącznie na liczniku PASS.
5. `eda/P03.kicad_pcb` i cztery strony PDF PCB: lokalne masy U5/C13, C3 przy VDD6, położenie rezystorów 33 Ω, tor 5 V oraz dostęp montażowy.
6. `MECHANIKA.md` i `ODBIOR.md`: przymiarka B2B i pomiary pozostają otwarte, mimo pozytywnego wyniku sprawdzeń CAD.

Zmiana nie obejmuje innych płytek ani bazowego firmware. Oryginalny pakiet R1 jest zachowany. Nowe U4/U5/Q1 są w obudowach SOT23 z dostępnymi wyprowadzeniami; dobór ten nie wymaga układu LM74800 ani obudowy QFN.
