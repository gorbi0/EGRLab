# Przegląd R3 i przejście do layoutu

| Pozycja | Status | Pozostała czynność |
|---|---|---|
| Schemat P01 i delta R2 | ZMIENIONO I SPRAWDZONO AUTOMATYCZNIE | Przegląd wąskiej delty: LK1/net DRAIN, C6 i mechanika. |
| R1-01 | SPRAWDZONE NIEZALEŻNIE W R2; REGRESJA ZACHOWANA | Pomiar rzeczywistego egzemplarza. |
| R2-01 | DECYZJA ARCHITEKTURY WPROWADZONA | Wykonanie P02-HOLD i odbiór integracyjny, przed użyciem LOGGER-a. |
| R2-02 | DOSTĘP I PROTOKÓŁ WPROWADZONE | Kwalifikacja rzeczywistej sondy/stanowiska. |
| B-01: C6 | DOBRANO DOSTĘPNĄ CZĘŚĆ | Ponowne sprawdzenie oferty przy zakupie; przymiarka. |
| M-01: radiatory | DOBRANO STS; WYMIARY I FOOTPRINT ZAPISANE | Sprawdzić faktyczny montaż i mocowanie obudowy na wydruku1:1. |
| Layout | NIEWYKONANY | Rozmieszczenie, routing, kontrola LK1/Kelvin/termików, DRC. |
| H-01: sprzęt, SOA, termika | NIE ZBADANO | ODBIOR i METROLOGIA; dopiero potem integracja. |
| P07 | HOLD | Czekamy na rzeczywisty moduł BTS7960. |

Do layoutu nie są potrzebne gotowe PCB pozostałych modułów. Interfejs P01/P02 jest
ustalony; pojemność HOLD nie trafia bezpośrednio na VPROT. Nie zamykać kontroli
sprzętu samymi symulacjami i nie odtwarzać całego EGRLab przy tej delcie.
