---
name: ubuntu-24-7
description: Komputer 24/7 z Ubuntu 22.04 (od 30.09) = rejestrator monitoringu Frigate, który ma pierwszeństwo; projekty w /home/tgorbacz/AI/Claude/<projekt>; Docker egrlab-kicad z limitem CPU; gałęzie zadań push przez SSH, main wypycha użytkownik
metadata:
  node_type: memory
  type: project
  originSessionId: cb9bcc34-135b-58ad-be17-9604396c28c1
  modified: 2026-09-30T20:00:00.000Z
---

Komputer 24/7 (Ubuntu **22.04**, 12 wątków, 31 GB). Projekty Claude w `/home/tgorbacz/AI/Claude/<projekt>`, EGRLab w `/home/tgorbacz/AI/Claude/EGRLab`, pamięć w `~/.claude/projects/-home-tgorbacz-AI-Claude-EGRLab/memory/`. Opis: `docs/UBUNTU-24-7.md`.

- **Rejestrator monitoringu (Frigate) ma pierwszeństwo** (użytkownik 30.09): `scripts/egrlab-docker` daje kontenerom `--cpu-shares 2` i `--cpus 2`; najwyżej 2 ciężkie zadania naraz; limitu nie podnosić bez zgody. Kontrola: `docker exec frigate curl -s http://127.0.0.1:5000/api/stats` (`skipped_fps` = 0). Kamera cam5_tyl_2 nie działa (przegryziony kabel, naprawi użytkownik) — nie diagnozować.
- Obraz `egrlab-kicad:10.0.6` z `scripts/setup-chmura.sh` (czcionki z przypiętych paczek noble, bo 22.04 nie ma `fonts-liberation-sans-narrow`).
- Git: tożsamość lokalnie w repo (Tomasz Gorbaczuk <gorbi@adres.pl>); `gh` nie ma. Od 1.10 push przez SSH: remote `git@github-egrlab:gorbi0/EGRLab.git` (alias w `~/.ssh/config`, klucz `~/.ssh/egrlab_deploy`). Gałęzie zadań wypycha sesja; push na `main` robi użytkownik (klasyfikator uprawnień go blokuje); PR-y otwiera użytkownik z linku po pushu.
- Kolejne płytki równolegle w worktree `.worktrees/<gałąź>` (wykluczone w `.git/info/exclude`), żeby nie przełączać gałęzi w trakcie przebiegów.
- Wiadomości do innych sesji tylko po „wyślij”; scalanie po „scal”.

**Why:** użytkownik chce, żeby zadania nie zależały od laptopa; maszyna nagrywa monitoring.
**How to apply:** ciężkie przebiegi zawsze przez `egrlab-docker`, kontrolować Frigate. Zob. [[repo-chmura]], [[p03-r6-state]].
