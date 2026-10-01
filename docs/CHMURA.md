# Praca w sesji Claude Code w chmurze

*29.09.2026. Repozytorium: `github.com/gorbi0/EGRLab` (prywatne, gałąź main). Środowisko **sprawdzone w pierwszej sesji** (gałąź `chmura-srodowisko`): KiCad 10.0.6 działa z obrazu Docker, kontrole zamkniętych P02-R3 i P04-PCB-R2.2 dają w chmurze te same wyniki co w repozytorium. Różnice Windows/Linux są opisane niżej.*

## Co w chmurze, co lokalnie

| W chmurze (kontener Linux, wynik jako pull request) | Tylko lokalnie (komputer użytkownika) |
|---|---|
| Generatory płytek KiCad: schemat, ERC, DRC, próby ujemne, PDF, Gerbery, paczki (bez layoutu i trasowania — patrz „Koszty”, zasada 6) | Pomiary: DHO804, MaxiECU, auto; **layout i trasowanie PCB** |
| Kompilacja i testy firmware ESP-IDF (niesprawdzone, zob. „Sieć”) | Sklepy (TME, Mouser, Farnell, Kamami) — logowanie i Cloudflare |
| Skrypty Pythona: logi, modele (kaseta, obliczenia), kontrole zgodności złączy | Przeglądarka i aplikacje lokalne, runtime Codexa |
| Dokumentacja i recenzje plików | Zamówienia, zakupy, wysyłka plików do producenta |

## Zasady

- Obowiązuje `CLAUDE.md`. Kopia pamięci Claude: `docs/pamiec-claude/MEMORY.md` — przeczytać na starcie sesji.
- Praca na osobnej gałęzi, wynik jako pull request; użytkownik przegląda i scala.
- **Nie zmieniać `.gitattributes`** (`* -text`). Pliki mają zostać bajt w bajt, bo pakiety mają manifesty SHA-256, a `EGRLab-AKTYWNE.md` ma celowo mieszane CRLF/LF (66 linii tylko z LF).
- Zamkniętych pakietów (`…-review` po recenzji, `…-zamowienie`) nie zmieniać. Nowa rewizja to nowy katalog.
- **Zamknięte pakiety uruchamiać na kopii** (np. w katalogu scratchpad sesji). `run_release.py`, `export_production.py` i próby ujemne zapisują do `verification/`, `output/`, `gerber/` i `podglad/` własnego pakietu, a na Linuksie wyniki różnią się bajtowo (niżej). Porównanie kopii z repozytorium: `scripts/chmura/porownaj_wyniki.py`.
- Po istotnych ustaleniach aktualizować `EGRLab-AKTYWNE.md` i `docs/01-overview.md` z zachowaniem ich końców linii.

## Koszty — model, wysiłek, zasady oszczędności

Sesja w chmurze płaci z kredytu za każdy krok: każde wywołanie narzędzia wysyła modelowi cały dotychczasowy kontekst, a przy wysiłku max model długo myśli także przed krokami mechanicznymi. Pierwsza sesja (walidacja środowiska, Opus 5.5 max) kosztowała ok. 5 $. Sesja lokalna idzie z planu użytkownika, nie z kredytu.

Model i wysiłek ustawia użytkownik w oknie sesji **przed pierwszą wiadomością**; zmiana w trakcie działa dopiero od następnej tury.

| Zadanie | Model | Wysiłek |
|---|---|---|
| Mechaniczne: środowisko, generatory według gotowej specyfikacji, paczki, odtwarzanie kontroli, dokumenty | Sonnet 5.5 | medium |
| Projektowe: schemat i PCB nowej rewizji, kontrole elektryczne | Opus 5.5 | high |
| Recenzja wyniku | sesja lokalna | — |

Wysiłku max w chmurze nie używać.

Zasady dla sesji w chmurze:

1. Czytać tylko to, co wskazuje zadanie: z `docs/pamiec-claude/` indeks `MEMORY.md` i pliki wymienione w poleceniu. Nie przeglądać repozytorium na zapas.
2. Długie wyjścia (Docker, KiCad, Freerouting, pip) kierować do pliku i pokazywać koniec, np. `polecenie > /tmp/log.txt 2>&1; tail -n 20 /tmp/log.txt`. Z JSON-ów wyciągać potrzebne pola zamiast wypisywać całe pliki.
3. Każdą kontrolę uruchamiać raz, ponownie tylko po zmianie, której dotyczy.
4. Duże zadania dzielić na etapy z osobnym PR (schemat → recenzja lokalna → PCB), żeby nie płacić za PCB do schematu, który zmieni recenzja.
5. Po otwarciu PR zakończyć pracę. Nie włączać śledzenia PR: każdy komentarz i scalenie budzi sesję i kosztuje turę. Pytania do użytkownika wpisywać do opisu PR.
6. **Layout i trasowanie PCB robi sesja lokalna, nie chmura.** Pilot P02 R4 (29.09) pokazał, dlaczego. Sesja przez kilka godzin pisała własne planery tras i czekała na przebiegi routera, zużywając ok. 30 $ w godzinę. Restart kontenera skasował niewypchnięty wynik. W chmurze zostają zadania o jasnym końcu: schemat, kontrole, dokumenty, paczki.
7. Po każdym zakończonym etapie commit i push na gałąź zadania, żeby restart kontenera niczego nie kasował.
8. Nie pisać własnych routerów ani planerów i nie uruchamiać procesów dłuższych niż ok. 15 min. Nie monitorować ich częstym sprawdzaniem: każde wybudzenie sesji to tura liczona od całego kontekstu.
9. Twardy limit: jeśli coś nie wychodzi po dwóch próbach, zapisać stan, wypchnąć i opisać problem w PR.

## Nazwy plików zarezerwowane w Windows

`AUX`, `CON`, `PRN`, `NUL`, `COM1…9`, `LPT1…9` są w Windows nazwami urządzeń, także z rozszerzeniem. Git for Windows nie otworzy takiego pliku.

W repozytorium jest 15 takich arkuszy: `AUX.kicad_sch` (pakiety P01, P05 R1) i `CON.kicad_sch` (P04, P05 R1). Na komputerze użytkownika dodano je do indeksu z zawartości czytanej przez bash (`git hash-object` + `update-index`) i oznaczono jako `skip-worktree`, więc lokalny git ich nie dotyka. W chmurze (Linux) odtwarzają się normalnie (sprawdzone 29.09). Świeży klon na Windows ich nie odtworzy.

**Po każdym `merge`, `pull`, `reset` lub `checkout` na Windows uruchomić `bash scripts/aux-con-indeks.sh`.** Git for Windows pomija te pliki przy rozpakowywaniu drzewa i usuwa je z indeksu razem ze znacznikiem skip-worktree (tak było przy scaleniu PR #1). Następny commit usunąłby je z repozytorium. Skrypt przywraca wpisy z HEAD i sprawdza, że indeks = HEAD. `git diff --cached` pokazuje wtedy mylące nazwy (np. „usunięte” pliki `.zip.sha256` obok katalogów z AUX), więc wiarygodna kontrola to `git write-tree` równe `git rev-parse HEAD^{tree}` przed dodaniem własnych zmian.

Scalanie na Windows: `git -c core.protectNTFS=false merge …` zachowuje te wpisy w indeksie (sprawdzone przy PR #2), a zwykłe `git merge` je gubi. Skrypt i tak uruchomić, a przed wypchnięciem sprawdzić, że commit ma 15 arkuszy AUX/CON.

**Nowe arkusze i pliki nazywać inaczej**, np. `AUX5`, `CONN`, `ZLACZA`. Dotyczy to też nowych rewizji P05 i P04. Zmiana pliku o takiej nazwie w chmurze nie da się pobrać do lokalnego repozytorium na Windows zwykłym `git pull`.

## Sieć — polityka środowiska (sprawdzona 29.09.2026)

Proxy wyjściowe środowiska odrzuca część adresów kodem 403. **Nie obchodzić blokad** (np. PPA po zwykłym HTTP przez `ppa.launchpad.net` odpowiada, ale z tego nie korzystamy). Zmiana dostępu: ustawienia środowiska w aplikacji (Network access — szerszy poziom albo dopisany host).

| Zablokowane (403) | Dostępne |
|---|---|
| `ppa.launchpadcontent.net` — PPA KiCada; `apt-get update` pada też na wpisanych w obraz PPA deadsnakes i ondrej/php | Docker Hub (`registry-1.docker.io`), przy czym bywa **429 Too Many Requests** (limit anonimowych pobrań) |
| `deb.debian.org`, `security.debian.org`, `ftp.debian.org`, `ftp.pl.debian.org`, `cdn-fastly.deb.debian.org`, `mirror.kernel.org`, `snapshot.debian.org` | `mirror.gcr.io` (lustro Docker Hub; ten sam digest obrazu KiCada) |
| `downloads.kicad.org`, `kicad-downloads.s3.cern.ch`, `flathub.org`, `dl.flathub.org` | `github.com/…/releases/download/…` i `release-assets.githubusercontent.com` |
| `download.java.net`, `api.adoptium.net` | PyPI, `registry.npmjs.org`, `nodejs.org`, `conda.anaconda.org` (conda-forge) |
| `dl.espressif.com` (ESP-IDF — sprawdzić obraz `espressif/idf` z Docker Hub, jest dostępny) | `archive.ubuntu.com`, `security.ubuntu.com` (Ubuntu 24.04 ma tylko KiCad 7.0.11) |
| `api.github.com` i strony `github.com` spoza repozytoriów sesji (samo pobieranie wydań działa) | `gitlab.com` |

## Narzędzia — obraz Docker `egrlab-kicad:10.0.6`

Wersje w tabeli są przypięte w `scripts/setup-chmura.sh` (micromamba, koła Pythona) i `scripts/chmura/Dockerfile` (poppler, OpenJDK, Node, sharp); zmiana wersji = zmiana w obu plikach i w tabeli. Instalacja: `bash scripts/setup-chmura.sh` — ok. 2–3 min od zera (pobranie obrazu KiCada 30–40 s, budowa ok. 85 s), na końcu test dymny. Skrypt sam uruchamia demona Dockera (w kontenerze sesji nie działa od startu), pobiera na hoście pliki do `scripts/chmura/.cache/` (w `.gitignore`) i buduje obraz z `scripts/chmura/Dockerfile` na bazie oficjalnego `kicad/kicad:10.0.6` (Debian 13), przypiętego digestem; przy 429 z Docker Hub bierze ten sam obraz z `mirror.gcr.io`. Brakujące w obrazie narzędzia pochodzą z conda-forge (poppler, Java, Node), PyPI (koła Pythona), npm (sharp) i archive.ubuntu.com (czcionki, źródła locale), bo mirrory Debiana są zablokowane.

| Narzędzie | W chmurze | Lokalnie (Windows) |
|---|---|---|
| KiCad (kicad-cli, pcbnew, biblioteki) | 10.0.6, obraz `kicad/kicad:10.0.6`, digest `sha256:18693567…` | 10.0.6 |
| Python z pcbnew | 3.13.5 (`/usr/bin/python3` obrazu) | Python KiCada `bin/python.exe` |
| numpy / Pillow / reportlab / pdfplumber | 2.5.3 / 12.3.0 / 4.4.9 / 0.11.10 | Python KiCada; reportlab 4.4.9 z runtime Codexa |
| poppler (`pdftoppm`, `pdftotext`) | 26.09.0 (conda-forge) | runtime Codexa |
| Java | OpenJDK 21.0.10 (conda-forge) | Temurin JRE 21.0.12.1 |
| Freerouting | 2.1.0 (sha256 `2c07d58f…`), działa bez GUI | 2.1.0 |
| ngspice (biblioteka współdzielona) | 44.2 (`libngspice0` z obrazu KiCada), `NGSPICE_LIBRARY` ustawione w obrazie | `ngspice.dll` z runtime KiCada |
| micromamba | 2.9.0-0 (sha256 `366cd9cd…`) | — |
| Node / sharp | 22.23.2 / 0.34.5 | runtime Codexa |
| Czcionki | Liberation Sans i Sans Narrow (metrycznie zgodne z Arial i Arial Narrow), DejaVu | Arial z `C:/Windows/Fonts` |
| Język | `pl_PL.UTF-8` (jak polski Windows; raporty DRC po polsku) | polski |

Uruchamianie: `scripts/egrlab-docker <polecenie>`, np. w katalogu kopii pakietu `…/scripts/egrlab-docker python3 src/run_release.py`. Repozytorium i katalog bieżący są montowane pod tymi samymi ścieżkami co na hoście, kontener działa bez sieci, z uid użytkownika i tymczasowym `HOME`. Dodatkowe katalogi (np. scratchpad spoza repozytorium): `EGRLAB_EXTRA_MOUNTS="/ścieżka"`. Raporty po angielsku: `EGRLAB_LANG=C.UTF-8`.

## Ścieżki Windows — jak są rozwiązane

Zamkniętych pakietów nie zmieniano. Zgodność daje obraz:

| W skryptach pakietów | W obrazie |
|---|---|
| `Path(sys.executable).with_name('kicad-cli.exe')` | dowiązanie `/usr/bin/kicad-cli.exe` → `kicad-cli` |
| `KICAD_CLI`, `KICAD_LIBRARY_ROOT` | `/usr/bin/kicad-cli`, `/usr/share/kicad` |
| `EGRLAB_PDF_PYTHON`, `EGRLAB_DOC_PYTHON`, `EGRLAB_NODE`, `EGRLAB_SHARP`, `PDFTOPPM`, `EGRLAB_PDFTOPPM` (domyślnie runtime Codexa) | narzędzia obrazu |
| `EGRLAB_FREEROUTING` + `jdk-21.0.12.1+1-jre/bin/java.exe` i `freerouting-2.1.0.jar` | `/opt/egrlab/freerouting` o tym samym układzie; `java.exe` → OpenJDK 21 |
| `C:/Windows/Fonts/arial*.ttf` w reportlab i PIL | `egrlab_winpaths.py` (ładowany przez `.pth`) podmienia tylko nazwy plików czcionek na Liberation; wyłączenie `EGRLAB_WINPATHS=0` |
| globalne tablice bibliotek użytkownika KiCada | punkt wejścia obrazu kopiuje szablonowe `fp-lib-table` i `sym-lib-table` do `$HOME/.config/kicad/10.0` |

Otwarte skrypty: `Plytki/Kaseta-R1/src/rysunek.py` czyta `EGRLAB_FONT_DIR` (bez zmiennej — czcionki Windows jak dotąd, więc wynik na Windows się nie zmienia). W nowym kodzie używać nazw, które pakiety już mają, z dotychczasową ścieżką Windows jako domyślną: `KICAD_CLI`, `KICAD_LIBRARY_ROOT`, `EGRLAB_FREEROUTING` (katalog), `EGRLAB_FONT_DIR`, `EGRLAB_PDF_PYTHON`/`EGRLAB_DOC_PYTHON`, `EGRLAB_NODE`, `EGRLAB_SHARP`, `PDFTOPPM`. Obraz ustawia też proponowane wcześniej `KICAD_PYTHON` i `FREEROUTING_JAR`. `NGSPICE_LIBRARY` wskazuje `libngspice.so.0` z obrazu (sprawdzone na `Plytki/P01-R3-review/src/ngshared.py`). Poza obrazem: `EGRLAB_TCC` (tcc nie ma).

## Różnice Windows / Linux (P02-R3, P04-PCB-R2.2, Kaseta-R1)

Wyniki kontroli są te same; różnice dotyczą tylko zapisu plików. Klasy nadaje `porownaj_wyniki.py`.

| Różnica | Skutek | Rozstrzygnięcie |
|---|---|---|
| Python na Windows zapisuje CRLF, na Linuksie LF | JSON i logi różnią się bajtowo (P02: 19 plików, P04: 3) | CRLF → LF przed porównaniem |
| Daty i ścieżki bezwzględne (netlista XML, SVG, ERC/DRC JSON, `.gbrjob`, raport wierceń, komentarz w Excellon) | skróty SHA-256 w raportach (`drc.provenance.json`, `electrical-checks.json`, `cam-checks.json`) inne | porównanie po usunięciu znaczników |
| Windows porównuje ścieżki bez rozróżniania wielkości liter | inna kolejność list plików wejściowych | porównanie list po posortowaniu |
| Brak globalnej tablicy bibliotek w świeżym KiCadzie | w próbach ujemnych 72 zamiast 24 zgłoszeń `lib_footprint_issues` | naprawione w obrazie |
| Język KiCada | bez `pl_PL` opisy DRC po angielsku | obraz ma `pl_PL.UTF-8` |
| Liberation zamiast Arial | PDF z reportlab: te same słowa, podglądy PNG różnią się na 0,6–1,0 % pikseli (kształt glifów); PDF/SVG z KiCada bez różnic | oględziny (strona 2 PCB P02 R3 — równoważna) |
| Zaokrąglenia MSVC/GCC przy wielokątach | F.Cu i B.Cu P04: po 3 kontury regionów z wierzchołkami przesuniętymi o 1 nm; flash, ścieżki, maski, opis, obrys i wiercenia identyczne | `porownaj_gerbery.py`, tolerancja 10 nm |
| Losowe UUID nowych ścieżek w próbach ujemnych P02 (`bcu_return`, `hold_free`) | inne miejsce odcinka w pliku, inna para w `unconnected_items` | liczby i typy naruszeń identyczne, wykrycie 10/10 |
| Paragon eksportu P04 | ścieżka `kicad-cli` (`C:\Program Files\…\kicad-cli.exe` ↔ `/usr/bin/kicad-cli.exe`) | reszta poleceń identyczna |

Freerouting w kontenerze bez sieci wypisuje `ERROR Could not determine local host name` i nie sprawdza nowej wersji — bez znaczenia dla trasowania.

## Czasy (29.09.2026)

| Krok | Czas |
|---|---|
| `setup-chmura.sh` od zera | ok. 2 min 10 s |
| P02-R3 `run_release.py` (bez `--rebuild`) | 78–136 s |
| P04 `export_production.py` / `check_cam.py` / `cam_negative_controls.py` | 11 s / 3 s / 26 s |
| Kaseta-R1 `rysunek.py` | 1 s |
| Freerouting, 5 przebiegów na `routing/P02.dsn` z P02 R3 | 9 s |

## Pierwsza sesja — zadanie walidacyjne (wykonane 29.09.2026)

1. `scripts/setup-chmura.sh` — przepisany na obraz Docker (PPA zablokowane). `kicad-cli version` = 10.0.6, `import pcbnew` działa.
2. Ścieżki Windows — rozwiązane w obrazie bez zmian w zamkniętych pakietach; `Kaseta-R1/src/rysunek.py` z `EGRLAB_FONT_DIR`.
3. `Plytki/P02-R3-review`, `python src/run_release.py` na kopii: 13/13 kroków PASS; ERC 0, DRC 0/0/0, kontrole elektryczne 11/11 (próby ujemne 8/8), PCB 29/29, rewizja R2 → R3 8/8, próby ujemne PCB 10/10 — jak w repozytorium.
4. `Plytki/P04-PCB-R2.2-zamowienie` na kopii: DRC 0/0/0, CAM 20/20 (450 PTH, 12 NPTH), próby ujemne 8/8 + zerowa. Suma PCB zgodna z wydaniem.
5. Opis w pull requeście gałęzi `chmura-srodowisko`.

Manifesty SHA-256 obu pakietów w repozytorium sprawdzone po pracy: 234/234 i 223/223 zgodnych.

## Kolejne zadania

Wykonane: krok 0 i P02 R4 etap 1 (PR #2, scalone 29.09.2026; recenzja `Plytki/P02-R4-recenzja/RECENZJA-P02-R4-ETAP1.md`).

**Od 29.09.2026 każda nowa płytka powstaje w formacie S1:** `Plytki/Format-S1/SPECYFIKACJA-FORMATU-S1.md` i `format-s1.json`. Format S1 to:
- stos płytek L, 2/3 i 1/3 na 160 × 100 mm;
- złącze płytki połączeń P12 na krawędzi A;
- listwa serwisowa z kołkami na krawędzi B;
- posiadane rezystory THT na stojąco, nowe części SMD 1206;
- produkcja w JLCPCB.

1. **P02 R4, etap 2 — PCB w S1 (pilot):** sesja w chmurze wypycha schemat, rozmieszczenie i skrypty (gałąź `p02-r4-pcb`). Trasowanie i recenzję robi sesja lokalna (zasada 6). Polecenie niżej jest już tylko zapisem historycznym.
2. **P05 R2** (gałąź `p05-r2`): z zadania obowiązują zmiany schematu i dokumentów; layout wykona nowe zadanie P05 w S1.
3. **LOGGER w S1 — schematy w chmurze, layouty lokalnie:**
   - P09 i P10: `Plytki/Format-S1/zadania/ZADANIE-P09-P10-S1.md` (Sonnet 5.5, high), polecenie niżej;
   - P03: `Plytki/Format-S1/zadania/ZADANIE-P03-S1.md` (Opus 5.5, high), polecenie niżej;
   - P05: `Plytki/Format-S1/zadania/ZADANIE-P05-S1.md` (Opus 5.5, high; dwa złącza J_BP — decyzja użytkownika 1.10.2026), polecenie niżej;
   - potem P06 (po doborze bocznika 2512 i przełącznika BYPASS);
   - na końcu P12 (płytka połączeń z plików `docs/J_BP.csv` wszystkich płytek), P11 pod nowy panel i obudowa.
4. **Wariant pełny w S1:** P04, P08, P07.

### Praca równoległa

Kilka sesji może działać naraz. Każda pracuje tylko we własnym pakiecie. Żadna nie zmienia plików wspólnych: `EGRLab-AKTYWNE.md`, `docs/01-overview.md`, `docs/CHMURA.md`, `docs/pamiec-claude/`, `scripts/`, `Plytki/Format-S1/`, `.gitignore`. Uzupełnia je sesja lokalna po scaleniu. Rozsądny limit to dwie sesje, bo każdy PR przechodzi lokalną recenzję.

### Gotowe polecenie — P09 i P10 w S1 (schematy)

Ustawienia sesji: Sonnet 5.5, wysiłek high.

> Przeczytaj CLAUDE.md, docs/CHMURA.md (zwłaszcza „Koszty”, zasady 6–9), docs/pamiec-claude/MEMORY.md, a z pamięci tylko format-s1.md, chmura-limity.md i kicad-pipeline-quirks.md. Wykonaj zadanie z Plytki/Format-S1/zadania/ZADANIE-P09-P10-S1.md na gałęzi p09-p10-s1. Tylko schematy i kontrole, bez PCB. Po każdej płytce commit i push. Nie zmieniaj plików wspólnych wymienionych w zadaniu. Zakończ PR-em po polsku; pytania wpisz do opisu PR i nie włączaj śledzenia PR.

### Gotowe polecenie — P03 w S1 (schemat)

Ustawienia sesji: Opus 5.5, wysiłek high.

> Przeczytaj CLAUDE.md, docs/CHMURA.md (zwłaszcza „Koszty”, zasady 6–9), docs/pamiec-claude/MEMORY.md, a z pamięci tylko format-s1.md, chmura-limity.md, kicad-pipeline-quirks.md i p03-r1-state.md. Wykonaj zadanie z Plytki/Format-S1/zadania/ZADANIE-P03-S1.md na gałęzi p03-s1. Tylko schemat i kontrole, bez PCB. Po każdym etapie commit i push. Nie zmieniaj plików wspólnych wymienionych w zadaniu. Zakończ PR-em po polsku; pytania wpisz do opisu PR i nie włączaj śledzenia PR.

### Gotowe polecenie — P05 w S1 (schemat)

Ustawienia sesji: Opus 5.5, wysiłek high.

> Przeczytaj CLAUDE.md, docs/CHMURA.md (zwłaszcza „Koszty”, zasady 6–9), docs/pamiec-claude/MEMORY.md, a z pamięci tylko format-s1.md, chmura-limity.md, kicad-pipeline-quirks.md i p05-r1-review.md. Wykonaj zadanie z Plytki/Format-S1/zadania/ZADANIE-P05-S1.md na gałęzi p05-s1. Tylko schemat i kontrole, bez PCB. Po każdym etapie commit i push. Nie zmieniaj plików wspólnych wymienionych w zadaniu. Zakończ PR-em po polsku; pytania wpisz do opisu PR i nie włączaj śledzenia PR.

### Gotowe polecenie — P02 R4, etap 2 (S1)

Ustawienia sesji: Opus 5.5, wysiłek high.

> Przeczytaj CLAUDE.md, docs/CHMURA.md (zwłaszcza „Koszty”), docs/pamiec-claude/MEMORY.md, a z pamięci tylko kicad-pipeline-quirks.md, p02-r1-state.md, p01-pcb-r1-review.md i format-s1.md. Wykonaj zadanie z Plytki/P02-R4-specyfikacja/ZADANIE-P02-R4-ETAP2.md (wersja 2, format S1) na gałęzi p02-r4-pcb. Obowiązuje Plytki/Format-S1/SPECYFIKACJA-FORMATU-S1.md. Nie zmieniaj plików wspólnych wymienionych w zadaniu. Zakończ PR-em po polsku; pytania wpisz do opisu PR i nie włączaj śledzenia PR.
