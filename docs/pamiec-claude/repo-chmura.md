---
name: repo-chmura
description: "Repozytorium github.com/gorbi0/EGRLab (prywatne, 29.09.2026) pod sesje Claude w chmurze: * -text, zipy recenzji poza repo, 15 plików AUX/CON jako skip-worktree, e-mail lokalny gorbi@adres.pl; docs/CHMURA.md"
metadata:
  node_type: memory
  type: project
  originSessionId: 1bdb3685-394a-4886-bbc7-14b9957d5ea4
  modified: 2026-09-29T09:06:58.627Z
---

29.09.2026 użytkownik dostał ofertę 250 $ na sesje w chmurze (odebrać do 8.10, wygasa 5.11) i poprosił o przygotowanie repozytorium.

**Stan:**
- **Na GitHubie: github.com/gorbi0/EGRLab** (prywatne), gałąź main, pierwszy commit 45dce9c (258 MB). Aplikacja Claude GitHub ma dostęp do wszystkich repozytoriów konta gorbi0.
- W tym repozytorium lokalnie `user.email = gorbi@adres.pl` (prywatny, zgodny z kontem GitHub). Globalny adres git użytkownika zostaje firmowy (t.gorbaczuk@ican.pl), nie zmieniać.
- Credential Manager ma zapisane konto gorbi0, więc `git push` z mojej powłoki działa bez okna. Pierwsze logowanie z procesu w tle nie pokazało okna; zadziałało dopiero w terminalu użytkownika.
- `.gitattributes`: `* -text`, bo manifesty SHA-256 i mieszane CRLF/LF muszą przetrwać bajt w bajt.
- `.gitignore`: wszystkie `*.zip` poza paczkami DO-ZAMOWIENIA, oraz pliki podręczne. **negative-controls/ i *.kicad_prl zostają**, bo są w manifestach P00/P02 zamówieniowych i P01.
- Rozmiar: 10 135 plików, ok. 371 MB po kompresji.
- **Nazwy zarezerwowane w Windows** (AUX, CON…): git for Windows nie otwiera `AUX.kicad_sch` ani `CON.kicad_sch` (15 plików: P01, P04, P05). Dodane przez `cat f | git hash-object -w --stdin` + `git -c core.protectNTFS=false update-index --add --cacheinfo`, potem `--skip-worktree`. Nowych arkuszy tak nie nazywać.
- `docs/CHMURA.md`: podział chmura/lokalnie, narzędzia Linux, ścieżki Windows do sparametryzowania, zadanie walidacyjne pierwszej sesji i gotowe polecenie. Szkic instalacji: `scripts/setup-chmura.sh` (nie zbadany).
- Kopia pamięci w `docs/pamiec-claude/` (stan 29.09); CLAUDE.md wskazuje ją i CHMURA.md.

**Pierwsza sesja w chmurze (29.09, gałąź `chmura-srodowisko`, commit 44160de, PR #1 — scalony fast-forward na polecenie użytkownika):**
- PPA KiCada, mirrory Debiana, api.github.com zablokowane (403); KiCad 10.0.6 z obrazu Docker `kicad/kicad:10.0.6` (digest przypięty) + dodatki → `egrlab-kicad:10.0.6`; `bash scripts/setup-chmura.sh` (~2 min), polecenia przez `scripts/egrlab-docker`. Zamknięte pakiety bez zmian — zgodność przez dowiązania w obrazie (`kicad-cli.exe`, układ katalogu Freeroutingu) i `egrlab_winpaths.py` (Arial → Liberation).
- Wyniki: P02-R3 i P04-PCB-R2.2 jak w repo; miedź P04 różni się o 1 nm (MSVC/GCC) → `scripts/chmura/porownaj_gerbery.py` (10 nm).
- Moja recenzja: końce linii i manifesty OK. Uwagi drobne na „krok 0” następnej sesji: wersje w Dockerfile/pip nieprzypięte (micromamba latest, openjdk=21, nodejs=22); `porownaj_wyniki.py` klasyfikuje każdy PNG jako RASTER bez progu, a PDF tylko po słowach.
- Koszt: ok. 5 $ z kredytu na Opus 5.5 max za walidację; użytkownik uznał to za drogo. Lokalna sesja idzie z planu **Pro**, nie z kredytu. Proponowane: mechaniczne → Sonnet 5.5 medium, projektowe → Opus 5.5 high, recenzja lokalnie.
- `docs/CHMURA.md` ma sekcję „Koszty” (model/wysiłek, 5 zasad) i gotowe polecenie P02 R4 etap 1 z krokiem 0 (przypięcie wersji, próg PNG, ngspice, czas instalacji).
- **Końce linii sprawdzać Pythonem na bajtach.** `grep -c $'\r$'` w Git Bash pokazał 88 CRLF dla pliku czysto LF. Stan: `STAN-PRAC.md` LF, `CHMURA.md` CRLF, `EGRLab-AKTYWNE.md` mieszany (66 LF). W heredocu wysłanym przez narzędzie Bash `\r`/`\n` zamieniają się w znaki sterujące (3× w tej sesji), a `Path.read_text()` zamienia CRLF na LF — przy edycji w Pythonie działać na bajtach, znaki przez `bytes([92])`/`chr(13)` albo tekst przez narzędzie Write/Edit.
- **Po każdym merge/pull na Windows: `bash scripts/aux-con-indeks.sh`.** Git for Windows (protectNTFS) przy fast-forward PR #1 wyrzucił z indeksu 15 wpisów AUX/CON razem ze skip-worktree; commit usunąłby je z repo. `git diff --cached` pokazywał wtedy fałszywe „D” przy 15 plikach `.zip.sha256` (nazwa następnego wpisu po katalogu z AUX). Kontrola przed commitem: `git write-tree` = `HEAD^{tree}` (przed dodaniem zmian).
- Sterowanie: moje ccd_session_mgmt nie widzą sesji w chmurze (tylko lokalne); ListAgents pokazuje ją jako peer „cloud”, SendMessage działa jednokierunkowo. Model/wysiłek zmienia użytkownik w jej oknie. PR sprawdzać przez `git ls-remote origin 'refs/pull/*'` (gh nie jest zainstalowany).

**Why:** długie zadania (generatory KiCad, Freerouting, ESP-IDF) mogą iść w chmurze bez komputera użytkownika.
**How to apply:** po pracy w chmurze uzgodnić pamięć lokalną z plikami stanu z repo. Przy nowych commitach lokalnie nie ruszać plików skip-worktree. Zob. [[zasilanie-ogniwa-18650]], [[kicad-pipeline-quirks]].
