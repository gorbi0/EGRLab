---
name: repo-chmura
description: "Repozytorium github.com/gorbi0/EGRLab (prywatne, 29.09.2026) pod sesje Claude w chmurze: * -text, zipy recenzji poza repo, 15 plików AUX/CON jako skip-worktree, e-mail lokalny gorbi@adres.pl; docs/CHMURA.md"
metadata:
  node_type: memory
  type: project
  originSessionId: 1bdb3685-394a-4886-bbc7-14b9957d5ea4
  modified: 2026-09-29T07:41:03.910Z
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

**Why:** długie zadania (generatory KiCad, Freerouting, ESP-IDF) mogą iść w chmurze bez komputera użytkownika.
**How to apply:** po pracy w chmurze uzgodnić pamięć lokalną z plikami stanu z repo. Przy nowych commitach lokalnie nie ruszać plików skip-worktree. Zob. [[zasilanie-ogniwa-18650]], [[kicad-pipeline-quirks]].
