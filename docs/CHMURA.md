# Praca w sesji Claude Code w chmurze

*29.09.2026. Repozytorium: `github.com/gorbi0/EGRLab` (prywatne, gałąź main). Środowisko **NIE ZBADANE** — pierwsza sesja ma je przygotować i sprawdzić (zadanie niżej).*

## Co w chmurze, co lokalnie

| W chmurze (kontener Linux, wynik jako pull request) | Tylko lokalnie (komputer użytkownika) |
|---|---|
| Generatory płytek KiCad: schemat, ERC, trasowanie Freerouting, DRC, próby ujemne, PDF, Gerbery | Pomiary: DHO804, MaxiECU, auto |
| Kompilacja i testy firmware ESP-IDF | Sklepy (TME, Mouser, Farnell, Kamami) — logowanie i Cloudflare |
| Skrypty Pythona: logi, modele (kaseta, obliczenia), kontrole zgodności złączy | Przeglądarka i aplikacje lokalne, runtime Codexa |
| Dokumentacja i recenzje plików | Zamówienia, zakupy, wysyłka plików do producenta |

## Zasady

- Obowiązuje `CLAUDE.md`. Kopia pamięci Claude: `docs/pamiec-claude/MEMORY.md` — przeczytać na starcie sesji.
- Praca na osobnej gałęzi, wynik jako pull request; użytkownik przegląda i scala.
- **Nie zmieniać `.gitattributes`** (`* -text`). Pliki mają zostać bajt w bajt, bo pakiety mają manifesty SHA-256, a `EGRLab-AKTYWNE.md` ma celowo mieszane CRLF/LF (66 linii tylko z LF).
- Zamkniętych pakietów (`…-review` po recenzji, `…-zamowienie`) nie zmieniać. Nowa rewizja to nowy katalog.
- Po istotnych ustaleniach aktualizować `EGRLab-AKTYWNE.md` i `docs/01-overview.md` z zachowaniem ich końców linii.

## Nazwy plików zarezerwowane w Windows

`AUX`, `CON`, `PRN`, `NUL`, `COM1…9`, `LPT1…9` są w Windows nazwami urządzeń, także z rozszerzeniem. Git for Windows nie otworzy takiego pliku.

W repozytorium jest 15 takich arkuszy: `AUX.kicad_sch` (pakiety P01, P05 R1) i `CON.kicad_sch` (P04, P05 R1). Na komputerze użytkownika dodano je do indeksu z zawartości czytanej przez bash (`git hash-object` + `update-index`) i oznaczono jako `skip-worktree`, więc lokalny git ich nie dotyka. W chmurze (Linux) odtwarzają się normalnie. Świeży klon na Windows ich nie odtworzy.

**Nowe arkusze i pliki nazywać inaczej**, np. `AUX5`, `CONN`, `ZLACZA`. Dotyczy to też nowych rewizji P05 i P04. Zmiana pliku o takiej nazwie w chmurze nie da się pobrać do lokalnego repozytorium na Windows zwykłym `git pull`.

## Narzędzia

Szkic instalacji w kontenerze Ubuntu: `scripts/setup-chmura.sh` (do sprawdzenia i poprawienia w pierwszej sesji).

| Narzędzie | Wersja | Do czego |
|---|---|---|
| KiCad (kicad-cli, moduł Pythona pcbnew, biblioteki symboli i footprintów) | 10.0.6, jak lokalnie | generatory, ERC/DRC, eksport |
| Java + Freerouting | Java 21, Freerouting 2.1.0 | trasowanie |
| Python 3 + reportlab, Pillow, numpy | — | PDF, podglądy, obliczenia |
| poppler-utils (pdftoppm) | — | podglądy PDF |
| Czcionki z polskimi znakami (Liberation, DejaVu) | — | zamiast Arial z Windows |
| Node + sharp | — | tylko `run_release` P01 |

Środowisko chmury musi mieć dostęp do sieci dla apt, PPA KiCada, wydań GitHub (Freerouting) i PyPI.

## Ścieżki Windows do sparametryzowania

Znane miejsca:
- KiCad: `C:/Program Files/KiCad/10.0/bin/python.exe` i `kicad-cli.exe`. `cadlib.py` w pakietach P0x ma już zmienną `KICAD_LIBRARY_ROOT`.
- Czcionki: `C:/Windows/Fonts/arial*.ttf`, np. w `Plytki/Kaseta-R1/src/rysunek.py` i w generatorach PDF.
- Runtime Codexa: `C:/Users/tgorbacz/.cache/codex-runtimes/…` (reportlab, pdftoppm, node).
- Freerouting: `C:/Users/tgorbacz/.codex/.chatgpt-projects/…/.egrlab-toolchains/freerouting/`.

Wyszukanie wszystkich miejsc: `grep -rn "C:/\|\.exe" --include=*.py Plytki/*/src Rewizje/*/src`.

Proponowany mechanizm: zmienne `KICAD_PYTHON`, `KICAD_CLI`, `KICAD_LIBRARY_ROOT`, `FREEROUTING_JAR`, `EGRLAB_FONT_DIR`, z dotychczasową wartością Windows jako domyślną. Wyniki na Windows nie mogą się zmienić.

## Pierwsza sesja — zadanie walidacyjne

1. Uruchomić `scripts/setup-chmura.sh`. Sprawdzić, że `kicad-cli version` pokazuje 10.0.6 i że `python3 -c "import pcbnew"` działa. Poprawić skrypt.
2. Sparametryzować ścieżki według sekcji wyżej.
3. Odtworzyć kontrole zamkniętego pakietu `Plytki/P02-R3-review` (`python src/run_release.py`, bez `--rebuild`) i porównać `verification/*.json`: ERC 0, DRC 0/0/0, kontrole elektryczne jak w repozytorium. Gerbery i SVG porównywać semantycznie, bo numeracja apertur zależy od UUID (zob. `docs/pamiec-claude/kicad-pipeline-quirks.md`).
4. W `Plytki/P04-PCB-R2.2-zamowienie` uruchomić `src/export_production.py`, `src/check_cam.py` i `src/cam_negative_controls.py`. Oczekiwane: DRC 0/0/0, CAM 20/20, próby ujemne 8/8 + zerowa.
5. W pull requeście opisać, co działa i jakie są różnice Windows/Linux.

Gotowe polecenie do pierwszej sesji:

> Przeczytaj CLAUDE.md, docs/CHMURA.md i docs/pamiec-claude/MEMORY.md. Wykonaj zadanie walidacyjne z docs/CHMURA.md (punkty 1–5) na gałęzi `chmura-srodowisko`. Nie zmieniaj zamkniętych pakietów ani .gitattributes. Wynik opisz w pull requeście po polsku.

## Kolejne zadania

- P02 R4 — schemat i PCB według `Plytki/P02-R4-specyfikacja/STAN-PRAC.md`.
- P03: wejście PFAIL_N, sprawy B2B. P05 R2, P06 (bocznik 2512), P11 R2 (przyciski, złącza panelu).
- Tabela wiązek pod kasetę (`Plytki/Kaseta-R1`).
