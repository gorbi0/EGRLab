# P03-R3 — zmiany względem R2 (rewizja zamykająca)

27.09.2026 · Claude. Podstawa: R2 Astry (`Plytki/P03-R2-review`, pakiet zgodny z manifestem) i końcowa recenzja `Plytki/P03-R2-recenzja/RECENZJA-P03-R2.md` (kopia w `reference/RECENZJA-P03-R2.md`).

**Miedź, rozmieszczenie, strefy, pady i połączenia są identyczne z R2** — sprawdza to `src/check_revision.py` (11/11) na zamrożonych `reference/R2.kicad_pcb` i `reference/R2-parts.json`. Jedyna zmiana wartości: R14.

| Uwaga | Zmiana w R3 | Gdzie |
|---|---|---|
| P3-01 wolne zbocze SUP_N na złączu do P04 | Bez zmiany miedzi. Opis skutków w P04-R2.1 i nowa próba „Zbocze SUP_N na P04” w odbiorze. Czyste rozwiązanie (bufor Schmitta przed J4.15) do decyzji — patrz „Sporne” | `ZASILANIE-RESET.md`, `ODBIOR.md` |
| P3-02 CORE_LINK przez 0 Ω | **R14 = 1 kΩ / 1 %** (MF0207FTE-1K, ten sam footprint). Nowe kontrole: „szyna zasilania na złączu bezpośrednio lub przez < 100 Ω” i „CORE_LINK przez 1K”; mutacje: R14 = 0R, J4.13 na 3V3_CORE | `parts.py`, `verify_function.py`, `zakupy.csv` |
| P3-03 próby ujemne bez czystego DRC (błąd skryptu z mojego R1) | Kopie dostają tabelę bibliotek; próba zerowa musi przejść 29/29 przy czystym DRC. Ujawniło to, że `dangling_lock` z R2 (przesunięcie 1,27 mm) nie odcinał ścieżki od padu, więc DRC go nie wykrywał; teraz 2,54 mm i DRC zgłasza `track_dangling` | `negative_controls.py` |
| P3-04 CAN_RX / P10 | Wymaganie interfejsowe dla P10 (RXD znosi 0,35 mA przy wyłączonym P10); P10-R1 spełnia je buforem RX z Ioff | `ZALOZENIA-P03-R2.md` |
| P3-05 SPI3_MISO / P09 | Wymaganie dla P09 (MISO w wysokiej impedancji bez zasilania); poziom spoczynkowy ≈ 0,6 V z podciąganiem na 4682; P09-R1 spełnia je (74LVC125A z Ioff) | `ZALOZENIA-P03-R2.md` |
| P3-06 liczby resetu, karta LTC4412 | LOW ≈ 0,25 V zamiast „< 0,7 V”; lokalna kopia karty LTC4412 (4412f) i potwierdzenie zasilania z VIN lub SENSE | `ZASILANIE-RESET.md`, `ZRODLA.md`, `reference/datasheets/` |

Dodatkowo:

- Nowa kontrola porównuje złącza pin w pin z zamrożonymi danymi sąsiadów: P02-R3 J3 (LV03), P04-R2.1 J2 (H_SAFE) i P05-R1 J1 (B2B). Źródło to `reference/interfaces-R3.json` z hashami ich manifestów. Mutacje obejmują zamianę pinu SUP_N/CORE_LINK i B2B.
- Pakowanie wydzielono do `src/package_release.py`. Odmawia pracy przy nieaktualnej kontroli wzrokowej lub nieaktualnym DRC.
- `verification/rebuild-compare.py` zapisuje raport w katalogu kopii (drugi argument). W R2 zapisywał w pierwszym, co w czasie recenzji nadpisało jeden plik pakietu R2. Plik przywrócono z archiwum R2, a manifest R2 jest znów zgodny.
- Tytuły P03-R3, linia tytułowa PCB „PCB R3”, nazwy PDF i archiwum. Nazwy `ZALOZENIA-P03-R2.md` i skryptów bez zmian.

## Czego nie zmieniano

Miedź, rozmieszczenie, pozostałe wartości i MPN. Wspólny reset EN/MCP/P04, U4/R34/R35. LTC4412 + AO3401A. Rezystory stanów domyślnych i R36–R40. Złącza i pozycja J1. Brak Gerberów — powstaną po zatwierdzeniu przekroju B2B i przymiarce.

## Sporne

- **Wolne zbocze SUP_N do P04 zostaje (P3-01).** To odstępstwo od karty 74LVC125A (Δt/ΔV ≤ 10 ns/V). Analiza P04-R2.1 pokazuje, że skutki występują tylko w stanie rozbrojonym: zatrzask ARM nie może się ustawić, a przy zapadzie możliwe są krótkie zakłócenia WD_Q/SENSOR_PERMIT. Usunięcie wymaga bufora Schmitta SN74LVC1G17 przed J4.15, czyli nowego trasowania i ponownej recenzji layoutu. Decyzja należy do użytkownika. Pomiar w odbiorze rozstrzyga, czy zakłócenia w ogóle występują.
- **R14 1 kΩ zamiast zwory z v6.1.** P04 i tak odbiera CORE_LINK przez LVC z 10 kΩ, tak jak z kanałów P00. Ograniczenie prądu zwarcia w taśmie jest spójne z P04 R2.

## Wyniki

`verification/QA.md`.
