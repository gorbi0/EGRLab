---
name: claude-msix-appdata-view
description: "Procesy uruchamiane z Claude Desktop widzą %APPDATA%\\Claude jako wirtualny widok LocalCache pakietu MSIX, więc przy liczeniu zajętości dysku nie wolno sumować obu ścieżek"
metadata:
  node_type: memory
  type: reference
  originSessionId: 3865af86-b552-4ae8-8505-576f94f56226
  modified: 2026-09-25T06:36:47.041Z
---

PowerShell i Bash uruchamiane z Claude Desktop działają w kontenerze MSIX `Claude_pzs8sxrjxfjjc`. Dlatego `C:\Users\tgorbacz\AppData\Roaming\Claude\...` i `AppData\Local\packages\Claude_pzs8sxrjxfjjc\LocalCache\Roaming\Claude\...` wskazują te same pliki: `fsutil file queryfileid` zwraca identyczny File ID, a `fsutil hardlink list` pokazuje tylko ścieżkę LocalCache. Rekurencyjny skan dysku liczy je podwójnie, 25.09.2026 było to ~9,8 GB, w tym obraz VM `vm_bundles\claudevm.bundle\rootfs.vhdx` o rozmiarze 7,6 GB.

**Why:** w analizie miejsca na dysku 25.09.2026 wyglądało to na 10 GB duplikatów. Dopiero porównanie File ID pokazało, że to jeden plik.
**How to apply:** przy każdej analizie zajętości dysku z tego środowiska odejmuj ścieżkę `AppData\Roaming\Claude` albo sprawdzaj File ID, zanim nazwiesz coś duplikatem.
