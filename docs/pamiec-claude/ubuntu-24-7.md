---
name: ubuntu-24-7
description: "Od 30.09.2026 długie zadania EGRLab idą na komputerze użytkownika z Ubuntu (24/7, sesja Claude Code „frigate-claude” z Remote Control); środowisko Docker z scripts/setup-chmura.sh; layout/trasowanie dozwolone"
metadata:
  node_type: memory
  type: reference
  originSessionId: 1bdb3685-394a-4886-bbc7-14b9957d5ea4
  modified: 2026-09-30T15:22:15.069Z
---

Komputer 24/7 z Ubuntu, sesja Claude Code „frigate-claude” (Remote Control; widoczna w ListAgents z laptopa). Opis środowiska i zasad: `docs/UBUNTU-24-7.md`.

- Narzędzia: obraz Docker `egrlab-kicad:10.0.6` z `scripts/setup-chmura.sh`, polecenia przez `scripts/egrlab-docker` (KiCad 10.0.6, Freerouting 2.1.0 w `/opt/egrlab/freerouting`, reportlab, poppler, Node/sharp, czcionki Liberation).
- To komputer i plan użytkownika, nie płatna chmura: layout i trasowanie wolno tu robić (zasady kosztowe z CHMURA.md nie obowiązują, [[chmura-limity]] dotyczy chmury).
- Hasła i tokeny (sudo, `gh auth login`) wpisuje użytkownik.
- Wiadomości z laptopa do tej sesji tylko po „wyślij” użytkownika; scalanie po „scal”.

**Why:** użytkownik chce, żeby zadania nie zależały od laptopa (30.09.2026).
**How to apply:** nowe zadania prowadzić tam; pamięć przywracać z `docs/pamiec-claude/` do `~/.claude/projects/<ścieżka repo z „-”>/memory/`. Zob. [[repo-chmura]], [[p03-r6-state]].
