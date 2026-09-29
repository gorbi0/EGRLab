# P11 PANEL / R1 - schemat i PCB do recenzji

Pasywna płytka połączeń panelu EGRLab: TEST, LOGGER L1/L2, kluczyk,
STOP, ARM, MARK, detektory wtyków, TAPS i trigger oscyloskopu.
160×110 mm, FR4 1,6 mm, dwie warstwy Cu70 µm. Na PCB tylko dwa gniazda
THT i dziewięć lutowanych wiązek; elementy panelowe montowane osobno.

Otwórz `eda/P11.kicad_pro`. Czytaj kolejno `docs/DLA-RECENZENTA.md`,
`docs/WIAZKI.md`, `docs/ZAKUPY.md` i `verification/ODBIOR.md`.
PDF: `output/pdf/P11-R1-schemat.pdf` i `output/pdf/P11-R1-PCB.pdf`.
Źródła generatorów, zamrożone kontrakty sąsiednich płytek i raporty są w pakiecie.

Status: **projekt do recenzji, sprzęt NIE ZBADANO**. P07/TMOTOR pozostaje HOLD
dla zakupionego wariantu BTS7960. P11 można zbudować i sprawdzić z obciążeniami
zastępczymi bez P07. Nie publikujemy Gerberów jako zatwierdzonej produkcji przed
recenzją, przymiarką J1/J7 i zatwierdzeniem mechaniki panelu.

P11 nie jest selektorem wejść analogowych. Dozwolony jeden adapter naraz.
Porty DEUTSCH nie mają wbudowanych detektorów: wymagają własnych uchwytów
zapewniających właściwą kolejność kontaktów. Podane typy EAO są wariantem
referencyjnym low-level; nie narzucają footprintu PCB.

Nie zmieniono P00–P10, firmware ani wcześniejszych rewizji. Interfejsy zamrożono
na P03-R2, P04-R2.1, P05-R1, P06-R1, P08-R1. Zmiana kontraktu wymaga ponownego
porównania, nie ręcznej poprawki tylko tabeli pinów.
