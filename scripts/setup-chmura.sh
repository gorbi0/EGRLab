#!/usr/bin/env bash
# EGRLab — szkic instalacji narzędzi w kontenerze Ubuntu (sesja Claude Code w chmurze).
# NIE ZBADANE (29.09.2026): nazwę PPA KiCada 10, nazwy pakietów i adres Freeroutingu
# sprawdzić w pierwszej sesji i poprawić w tym pliku. Zob. docs/CHMURA.md.
set -euo pipefail
SUDO="$(command -v sudo || true)"

$SUDO apt-get update
$SUDO apt-get install -y --no-install-recommends \
  software-properties-common ca-certificates curl git \
  python3 python3-pip python3-reportlab python3-pil python3-numpy \
  poppler-utils fonts-liberation fonts-dejavu-core openjdk-21-jre-headless

# KiCad 10.0.x (lokalnie 10.0.6). Dla 9.0 PPA nazywało się ppa:kicad/kicad-9.0-releases.
$SUDO add-apt-repository -y ppa:kicad/kicad-10.0-releases
$SUDO apt-get update
$SUDO apt-get install -y kicad kicad-symbols kicad-footprints
kicad-cli version
python3 -c "import pcbnew; print('pcbnew', pcbnew.Version())"

# Freerouting 2.1.0 (lokalnie ta sama wersja z Javą 21)
TOOLS="$HOME/tools"
mkdir -p "$TOOLS/freerouting"
curl -fL -o "$TOOLS/freerouting/freerouting-2.1.0.jar" \
  "https://github.com/freerouting/freerouting/releases/download/v2.1.0/freerouting-2.1.0.jar"

# Zmienne do parametryzacji skryptów (docs/CHMURA.md, sekcja „Ścieżki Windows”)
{
  echo "export KICAD_LIBRARY_ROOT=/usr/share/kicad"
  echo "export KICAD_CLI=$(command -v kicad-cli)"
  echo "export KICAD_PYTHON=$(command -v python3)"
  echo "export FREEROUTING_JAR=$TOOLS/freerouting/freerouting-2.1.0.jar"
  echo "export EGRLAB_FONT_DIR=/usr/share/fonts/truetype/liberation"
} >> "$HOME/.bashrc"
echo "Gotowe. Otwórz nową powłokę albo: source ~/.bashrc"
