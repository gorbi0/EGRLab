# Paczka: Kia Sportage EGR → Claude Code

## Instalacja (2 minuty)
1. Rozpakuj do stałego miejsca, np. `~/Projekty/kia-sportage-egr/`.
2. Dorzuć pliki, których nie dało się wyeksportować automatycznie:
   - `schematics/` — PDF Monolith (Kia Sportage od 2010, RU).
   - `logs/raw/` — logi XML z MaxiECU i Car Scanner, które masz lokalnie.
   - `logs/scripts/` — Twoje skrypty Python do parsowania logów (jeśli je zachowałeś).
   - `scope/setups/` — pliki `.stp` z DHO804, gdy je zapiszesz.
   - pliki z wiedzy Projektu claude.ai (pobierz z panelu Projektu) → `docs/` lub `schematics/`.
   - instrukcje Projektu claude.ai (jeśli jakieś ustawiłeś) → dopisz na końcu `CLAUDE.md`.
3. (Opcjonalnie) `git init && git add . && git commit -m "start"` — historia zmian procedury za darmo.
4. W Claude Desktop → zakładka **Code** → wybierz ten folder jako katalog roboczy.
5. Sprawdzenie: zapytaj „Jaki jest stan kampanii i co robię jako pierwsze po powrocie do Hiszpanii?”. Claude powinien odpowiedzieć z `docs/01-overview.md` bez dopytywania.

## Co jest w środku
| Plik | Rola |
|---|---|
| `CLAUDE.md` | Ładowany automatycznie: styl współpracy + import dokumentów 01–03 |
| `docs/01-overview.md` | Aktualny stan, hipotezy H1–H7, następne kroki, decyzje |
| `docs/02-learnings-and-tools.md` | Wnioski, sprzęt, pinout CUD87, strony schematów |
| `docs/03-historia.md` | Chronologia czerwiec–wrzesień 2026 |
| `docs/04-klimatyzacja-ECV.md` | Zamknięta naprawa AC/ECV (ważna dla H1/H7) |
| `docs/05-szarpanie-historia.md` | Diagnostyka szarpania, wykluczenia |
| `docs/procedura_v3_DHO804.md` | Pełna procedura pomiarowa v3 („do auta”) |
| `docs/dziennik-zdarzen.csv` | Dziennik wystąpień P0404 |
