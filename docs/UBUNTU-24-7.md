# Komputer 24/7 (Ubuntu) — praca Claude Code

*30.09.2026. Od tego dnia długie zadania (layout i trasowanie PCB, generatory, kontrole, paczki) idą na komputerze użytkownika z Ubuntu, działającym całą dobę. Laptop z Windows zostaje do pomiarów, sklepów i przeglądarki. Użytkownik łączy się z sesjami przez Remote Control (aplikacja Claude na laptopie lub telefonie).*

## Katalogi i sesje

- Wszystkie projekty Claude na tym komputerze: **`/home/tgorbacz/AI/Claude/<projekt>`** (decyzja użytkownika 30.09.2026). EGRLab: **`/home/tgorbacz/AI/Claude/EGRLab`**.
- Jedna sesja Claude Code na projekt, uruchomiona w jego katalogu (np. w `tmux`: `cd /home/tgorbacz/AI/Claude/EGRLab && claude --remote-control`). Tylko wtedy ładują się `CLAUDE.md` projektu i jego pamięć.
- Sesja „frigate-claude” (Remote Control) służyła do jednorazowego przygotowania środowiska; bieżąca praca nad EGRLab idzie w sesji uruchomionej w katalogu EGRLab.

## Czym różni się od chmury (`docs/CHMURA.md`)

To komputer użytkownika i jego plan, nie kredyt chmury: **layout i trasowanie PCB są tu dozwolone** (zasady 6 i 8 z CHMURA.md dotyczą płatnej chmury), procesy mogą trwać długo, ale wynik trzeba wypychać po każdym etapie. Pozostałe zasady bez zmian: `CLAUDE.md`, praca na gałęzi i pull request, scalanie dopiero po „scal” użytkownika, wiadomości do innych sesji dopiero po „wyślij”, zamkniętych pakietów nie zmieniać, `.gitattributes` bez zmian (`* -text`), pliki bajt w bajt.

## Środowisko (jednorazowo)

Kroki wymagające hasła lub tokenu robi użytkownik (Claude nie wpisuje haseł ani tokenów):
1. Docker z usługą systemową i użytkownik w grupie `docker` (`sudo usermod -aG docker $USER`, ponowne logowanie).
2. `gh auth login` (dostęp do prywatnego `github.com/gorbi0/EGRLab`), git z nazwą i e-mailem użytkownika.

Potem sesja Claude Code:
3. `git clone https://github.com/gorbi0/EGRLab.git /home/tgorbacz/AI/Claude/EGRLab` (katalog istnieje; klon wymaga, żeby był pusty — jeśli nie jest, zatrzymać się i zapytać użytkownika) i `git checkout` gałęzi zadania. Na Linuksie arkusze AUX/CON odtwarzają się normalnie; `scripts/aux-con-indeks.sh` jest tylko dla Windows.
4. `bash scripts/setup-chmura.sh` — buduje obraz `egrlab-kicad:10.0.6` (KiCad 10.0.6, Python z pcbnew, reportlab, poppler, OpenJDK 21, Freerouting 2.1.0 w `/opt/egrlab/freerouting`, Node + sharp, czcionki Liberation, `pl_PL.UTF-8`). Skrypt był pisany pod kontener chmury (certyfikat proxy, ręczny start `dockerd`); na zwykłym Ubuntu te kroki przechodzą jałowo — jeśli nie, poprawić skrypt na gałęzi zadania.
5. Uruchamianie w kontenerze: `scripts/egrlab-docker python3 src/run_schematic.py` w katalogu pakietu (repozytorium montowane pod tą samą ścieżką, bez sieci). Zmienne `EGRLAB_*`, `KICAD_*` ustawia obraz; `PDFTOPPM` w razie potrzeby podać jako `/opt/egrlab/env/bin/pdftoppm`.
6. Test zgodności: zamknięty pakiet na kopii (np. `P02-R4-review` → katalog tymczasowy) i `scripts/chmura/porownaj_wyniki.py` jak w CHMURA.md.

## Pamięć Claude

Kopia pamięci: `docs/pamiec-claude/` (indeks `MEMORY.md`). Na Ubuntu pliki idą do katalogu pamięci projektu: **`~/.claude/projects/-home-tgorbacz-AI-Claude-EGRLab/memory/`** (Claude Code tworzy nazwę z pełnej ścieżki projektu, zamieniając `/` na `-`). Po istotnych zmianach aktualizować pamięć i jej kopię w repozytorium w tym samym commicie.

## Bieżące zadanie

P03 R6, layout: `Plytki/P03-R6-review/STAN-PRAC.md` (gałąź `p03-r6-pcb`).
