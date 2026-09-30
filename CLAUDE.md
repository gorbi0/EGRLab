# Kia Sportage — kampania diagnostyczna EGR / P0404

Samodzielna diagnostyka i naprawa: **Kia Sportage SL 2013, 1.7 CRDi D4FD, Bosch EDC17C08, ~280 tys. km.**
Główny problem: przerywany P0404 (EGR) → tryb awaryjny. Zawór EGR wymieniany 3× w ~20 tys. km, bez nagaru.
Wiodący kierunek: wiązka / masa / złącze, a nie sam zawór.

## Kontekst (ładowany automatycznie)

@docs/01-overview.md
@docs/02-learnings-and-tools.md
@docs/03-historia.md

## Dokumenty czytane na żądanie (nie importowane, żeby nie zapychać kontekstu)

- `docs/procedura_v3_DHO804.md` — **aktualna procedura pomiarowa** (Test A, Kroki 0–7, ścieżka B, nastawy Rigol DHO804). Jedyny dokument „do auta”. Czytaj przed każdą rozmową o pomiarach skopem.
- `docs/04-klimatyzacja-ECV.md` — zamknięta naprawa AC (przerwana żyła ECV), piny FATC, dane kompresora. Czytaj, gdy temat dotyka H1/H7.
- `docs/05-szarpanie-historia.md` — diagnostyka szarpania 1600–1800 obr. (lipiec 2026), wykluczone hipotezy.
- `docs/dziennik-zdarzen.csv` — dziennik wystąpień P0404. Dopisuj nowe wiersze, gdy użytkownik zgłosi zdarzenie.
- `schematics/` — PDF ze schematami (Monolith, RU). Numery stron w `docs/02-learnings-and-tools.md`.
- `logs/raw/` — logi XML z MaxiECU / Car Scanner. `logs/scripts/` — parsery Python.
- `scope/setups/` — pliki `.stp` DHO804. `scope/captures/` — zrzuty PNG/CSV ze skopu.
- `EGRLab-AKTYWNE.md` — bieżący etap przyrządu EGRLab: płytki P00–P11, decyzje, stany pakietów, zakupy.
- `docs/pamiec-claude/MEMORY.md` — kopia pamięci Claude z komputera użytkownika (29.09.2026): stany płytek, decyzje, pułapki narzędzi. W sesji w chmurze przeczytaj na starcie.
- `docs/CHMURA.md` — praca w sesji w chmurze: podział zadań chmura/lokalnie, narzędzia Linux, ścieżki Windows do sparametryzowania, zadanie pierwszej sesji.
- `docs/UBUNTU-24-7.md` — komputer 24/7 z Ubuntu (od 30.09.2026): tam idą długie zadania (layout, trasowanie, generatory); środowisko Docker, przywracanie pamięci, zasady.
- `Plytki/P03-R6-review/STAN-PRAC.md` — bieżąca praca: P03 R6 (CORE w formacie S1), layout w toku, gałąź `p03-r6-pcb`.

## Jak ze mną pracować

- Po polsku, **na Ty**. Zwięźle, konkretnie, krótkie sekcje; proza zamiast list, tabele gdy porównujesz.
- Szczerze zamiast pocieszająco. Jeśli się mylisz — przyznaj i popraw od razu. Poprawiam błędy natychmiast, więc nie broń złej tezy.
- Metoda: dane → systematyczna eliminacja hipotez → dopiero potem wymiana części. **Nie proponuj wymiany zaworu EGR ani usunięcia EGR** (zaślepka nie rusza P0404, programowe wycięcie = maskowanie; obie opcje odrzucone).
- Zanim zaproponujesz test, sprawdź, czy istniejące logi/obserwacje już go nie rozstrzygają (był taki błąd z testem AC on/off przy logu z AC zawsze włączoną).
- Przy analizie logów: uwzględniaj **regenerację DPF** (tłumi EGR, zafałszowuje obraz), limit próbkowania 1,8–4,6 Hz (maks. 3–4 kanały na sesję), jeden PID EGR bez pary desired/actual.
- Dokumenty terenowe muszą być samowystarczalne (czytane przy masce bez kontekstu). Sporne decyzje oznaczaj w dokumencie z jednozdaniowym uzasadnieniem.
- Aktualizując procedurę, twórz nową wersję (v4…) i zaznacz na górze, co się zmieniło.
- Po istotnym ustaleniu zaktualizuj `docs/01-overview.md` (stan) lub `docs/02-learnings-and-tools.md` (wnioski), żeby następna sesja zaczynała z aktualnym obrazem.
- Logistyka: części kupowane w Polsce, wysyłka do Hiszpanii InPost; Ryanair — bagaż kabinowy (ostre końcówki sond itp.).
