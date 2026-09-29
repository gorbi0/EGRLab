#!/usr/bin/env bash
# EGRLab — przygotowanie narzędzi w kontenerze sesji Claude Code w chmurze (Ubuntu 24.04).
# Sprawdzone 29.09.2026 w pierwszej sesji (gałąź chmura-srodowisko), opis: docs/CHMURA.md.
#
# KiCad NIE z PPA: polityka sieci środowiska (Default) odrzuca ppa.launchpadcontent.net (403),
# a także mirrory Debiana (deb.debian.org, security.debian.org) i downloads.kicad.org.
# Dostępne są Docker Hub, pobieranie wydań z GitHuba, PyPI, npm, conda-forge i archive.ubuntu.com.
# Dlatego: oficjalny obraz kicad/kicad:10.0.6 (Debian 13, Python 3.13 z pcbnew) + dodatki
# zbudowane lokalnie jako egrlab-kicad:10.0.6 (scripts/chmura/Dockerfile).
#
# Użycie:   bash scripts/setup-chmura.sh          (ok. 2–3 min przy pustej pamięci podręcznej Dockera)
# Potem:    scripts/egrlab-docker python3 src/run_release.py      (w katalogu pakietu)
set -euo pipefail
REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CTX="$REPO/scripts/chmura"
C="$CTX/.cache"            # pliki pobrane na hoście (w .gitignore)
KICAD_IMAGE=kicad/kicad:10.0.6
IMAGE=egrlab-kicad:10.0.6
mkdir -p "$C/wheels" "$C/fonts"
t0=$(date +%s)
step() { echo "== [$(( $(date +%s) - t0 )) s] $*"; }

step "Docker"
if ! docker info >/dev/null 2>&1; then
  # W kontenerze sesji demon nie startuje sam.
  (dockerd >/tmp/dockerd.log 2>&1 &)
  for _ in $(seq 1 30); do docker info >/dev/null 2>&1 && break; sleep 1; done
fi
docker info --format 'serwer {{.ServerVersion}}, sterownik {{.Driver}}'

step "Certyfikat proxy wyjściowego (tylko na czas budowania obrazu)"
CA="${SSL_CERT_FILE:-/root/.ccr/ca-bundle.crt}"
[ -f "$CA" ] || CA=/etc/ssl/certs/ca-certificates.crt
cp "$CA" "$C/proxy-ca.crt"

# Wersje przypięte do tabeli „Narzędzia” w docs/CHMURA.md; zmiana tutaj = zmiana tam i w Dockerfile.
MICROMAMBA_VER=2.9.0-0
MICROMAMBA_SHA=366cd9cd8be14df1ab8ed50352a82111082a36686b2d389fdb79a92c3fafb3e3
WHEELS="pip==25.2 numpy==2.5.3 pillow==12.3.0 reportlab==4.4.9 pdfplumber==0.11.10"

step "micromamba $MICROMAMBA_VER (conda-forge: poppler 26.09.0, OpenJDK 21.0.10, Node 22.23.2)"
echo "$MICROMAMBA_SHA  $C/micromamba" | sha256sum -c --status - 2>/dev/null || curl -fsSL -o "$C/micromamba" \
  "https://github.com/mamba-org/micromamba-releases/releases/download/$MICROMAMBA_VER/micromamba-linux-64"
echo "$MICROMAMBA_SHA  $C/micromamba" | sha256sum -c -
chmod +x "$C/micromamba"

step "Koła Pythona dla Pythona KiCada (3.13): $WHEELS"
# Obraz KiCada nie ma pip ani curl; koła pobiera host (PyPI jest dostępne), instaluje je Dockerfile.
PY=$(command -v python3)
"$PY" -m pip download -q --disable-pip-version-check -d "$C/wheels" --only-binary=:all: --python-version 3.13 \
  --platform manylinux2014_x86_64 --platform manylinux_2_17_x86_64 --platform manylinux_2_28_x86_64 \
  $WHEELS
ls "$C"/wheels/reportlab-5* >/dev/null 2>&1 && rm -f "$C"/wheels/reportlab-5* || true

step "Czcionki Liberation (metrycznie zgodne z Arial i Arial Narrow) z archive.ubuntu.com"
if [ ! -f "$C/fonts/LiberationSansNarrow-Regular.ttf" ]; then
  tmp=$(mktemp -d); ( cd "$tmp" && apt-get download fonts-liberation fonts-liberation-sans-narrow >/dev/null 2>&1 )
  for d in "$tmp"/*.deb; do dpkg -x "$d" "$tmp/x"; done
  find "$tmp/x" -name '*.ttf' -exec cp {} "$C/fonts/" \;
  rm -rf "$tmp"
fi
ls "$C/fonts" | grep -c ttf

step "Źródła locale pl_PL (KiCad na Windows pracuje po polsku; opisy DRC idą za językiem)"
if [ ! -f "$C/i18n/locales/pl_PL" ]; then
  [ -f /usr/share/i18n/locales/pl_PL ] || { apt-get download locales >/dev/null 2>&1 && dpkg -x locales_*.deb /tmp/locales-x && rm -f locales_*.deb; }
  SRC=/usr/share/i18n; [ -f "$SRC/locales/pl_PL" ] || SRC=/tmp/locales-x/usr/share/i18n
  mkdir -p "$C/i18n"; cp -a "$SRC/locales" "$SRC/charmaps" "$C/i18n/"
  gunzip -kf "$C/i18n/charmaps/UTF-8.gz"
fi

step "Freerouting 2.1.0"
[ -f "$C/freerouting-2.1.0.jar" ] || curl -fsSL -o "$C/freerouting-2.1.0.jar" \
  https://github.com/freerouting/freerouting/releases/download/v2.1.0/freerouting-2.1.0.jar
echo "2c07d58f75dac03782664081e7a58b41c25400d871a9fcf166a2ea6fe60d5def  $C/freerouting-2.1.0.jar" | sha256sum -c -

step "Obraz $KICAD_IMAGE (ok. 0,8 GB; Docker Hub, zapasowo mirror.gcr.io)"
# Docker Hub bywa odrzucany limitem anonimowych pobrań (429 Too Many Requests — wspólny adres wyjściowy
# kontenerów). mirror.gcr.io podaje ten sam obraz; digest sprawdzony 29.09.2026 w obu źródłach.
KICAD_DIGEST=sha256:18693567392b80da435f9fa952ce3a3e534c66eb5a6033f5b9c80aa3b19dd3ec
have_kicad() { docker image inspect "$KICAD_IMAGE" --format '{{json .RepoDigests}}' 2>/dev/null | grep -q "$KICAD_DIGEST"; }
if ! have_kicad; then
  for src in docker.io/kicad/kicad mirror.gcr.io/kicad/kicad docker.io/kicad/kicad; do
    for wait in 0 10 30; do
      sleep "$wait"
      if docker pull -q "$src@$KICAD_DIGEST" >/dev/null 2>&1; then
        docker tag "$src@$KICAD_DIGEST" "$KICAD_IMAGE"; break 2
      fi
      echo "  $src: pobranie nieudane, ponawiam"
    done
  done
fi
have_kicad || { echo "BŁĄD: brak $KICAD_IMAGE o digescie $KICAD_DIGEST"; exit 1; }

step "Budowanie $IMAGE"
docker build -q --network host \
  --build-arg HTTPS_PROXY="${HTTPS_PROXY:-}" --build-arg https_proxy="${HTTPS_PROXY:-}" \
  -t "$IMAGE" "$CTX" >/dev/null

step "Test dymny"
"$REPO/scripts/egrlab-docker" bash -c '
  set -e
  v=$(kicad-cli version); echo "kicad-cli $v"; [ "$v" = 10.0.6 ]
  python3 -c "import pcbnew,numpy,PIL,reportlab,pdfplumber; print(\"pcbnew\",pcbnew.Version(),\"| Python\",__import__(\"sys\").version.split()[0],\"| numpy\",numpy.__version__,\"| Pillow\",PIL.__version__,\"| reportlab\",reportlab.Version)"
  python3 -c "import pcbnew; assert pcbnew.Version()==\"10.0.6\""
  pdftoppm -v 2>&1 | head -1
  java -version 2>&1 | grep -i "openjdk version"
  echo "node $(node -v)"; node -e "require(process.env.EGRLAB_SHARP); console.log(\"sharp ok\")"
  EGRLAB_WINPATHS_VERBOSE=1 python3 -c "from reportlab.pdfbase.ttfonts import TTFont; TTFont(\"A\",\"C:/Windows/Fonts/arial.ttf\")"
  locale | grep LC_ALL
  python3 -c "import ctypes,os; ctypes.CDLL(os.environ[\"NGSPICE_LIBRARY\"]); print(\"ngspice\", os.environ[\"NGSPICE_LIBRARY\"])"'
step "Gotowe. Polecenia uruchamiaj przez scripts/egrlab-docker (zob. docs/CHMURA.md)."
