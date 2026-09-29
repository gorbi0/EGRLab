# EGRLab — obraz narzędzi do sesji w chmurze: oficjalny KiCad 10.0.6 (Debian 13) + dodatki.
# Budowanie wyłącznie przez scripts/setup-chmura.sh (najpierw pobiera pliki do .cache/).
# Dlaczego obraz: PPA KiCada (launchpad) i mirrory Debiana są w chmurze zablokowane,
# Docker Hub, GitHub, PyPI, npm i conda-forge nie.
FROM kicad/kicad:10.0.6
USER root
ARG CA_FILE=.cache/proxy-ca.crt
COPY ${CA_FILE} /usr/local/share/ca-certificates/egrlab-build-proxy.crt
RUN update-ca-certificates >/dev/null

# Python KiCada (/usr/bin/python3, 3.13, z pcbnew): numpy, Pillow, reportlab 4.4.9
# (ta sama wersja co runtime Codexa u użytkownika), pdfplumber. Koła z .cache/wheels.
# Wersje przypięte do tabeli „Narzędzia” w docs/CHMURA.md (te same pobiera setup-chmura.sh).
COPY .cache/wheels /tmp/wheels
RUN PIPWHL=$(ls /tmp/wheels/pip-*.whl) && python3 "$PIPWHL/pip" install --no-index --find-links /tmp/wheels \
      --break-system-packages --no-cache-dir --root-user-action=ignore \
      numpy==2.5.3 pillow==12.3.0 reportlab==4.4.9 pdfplumber==0.11.10 \
 && rm -rf /tmp/wheels

# poppler (pdftoppm), Java 21, Node 22 z conda-forge do /opt/egrlab/env (micromamba 2.9.0, wersje przypięte)
COPY .cache/micromamba /usr/local/bin/micromamba
RUN MAMBA_ROOT_PREFIX=/tmp/mamba micromamba create -y -q -p /opt/egrlab/env \
      -c conda-forge --override-channels poppler=26.09.0 openjdk=21.0.10 nodejs=22.23.2 \
 && rm -rf /tmp/mamba /opt/egrlab/env/pkgs
# sharp dla rasterize.mjs (run_release P01/P02)
RUN mkdir -p /opt/egrlab/node && cd /opt/egrlab/node && export PATH=/opt/egrlab/env/bin:$PATH \
 && npm init -y >/dev/null && npm install --no-audit --no-fund sharp@0.34.5 \
 && node -e "require('/opt/egrlab/node/node_modules/sharp');console.log('sharp ok')"

# Czcionki Liberation (metrycznie zgodne z Arial) i Freerouting 2.1.0
COPY .cache/fonts/ /usr/share/fonts/truetype/liberation/
COPY .cache/freerouting-2.1.0.jar /opt/egrlab/freerouting/freerouting-2.1.0.jar
RUN fc-cache -f >/dev/null
# Locale pl_PL.UTF-8: KiCad na Windows pracuje po polsku, a opisy w raportach DRC idą za językiem.
# Źródła locale z Ubuntu hosta (.cache/i18n), bo mirrory Debiana są zablokowane.
COPY .cache/i18n /tmp/i18n
RUN I18NPATH=/tmp/i18n localedef -f /tmp/i18n/charmaps/UTF-8 -i /tmp/i18n/locales/pl_PL pl_PL.UTF-8 \
 && rm -rf /tmp/i18n && locale -a | grep -qi pl_PL

# Zgodność z zamkniętymi pakietami bez zmiany ich plików:
#  - skrypty biorą kicad-cli jako Path(sys.executable).with_name('kicad-cli.exe')
#  - 'C:/Windows/Fonts/arial*.ttf' tłumaczy egrlab_winpaths.py (ładowany przez .pth)
#  - run_layout.py wołają $EGRLAB_FREEROUTING/jdk-21.0.12.1+1-jre/bin/java.exe (układ katalogu z Windows)
RUN ln -s /usr/bin/kicad-cli /usr/bin/kicad-cli.exe \
 && mkdir -p /opt/egrlab/freerouting/jdk-21.0.12.1+1-jre/bin \
 && ln -s /opt/egrlab/env/bin/java /opt/egrlab/freerouting/jdk-21.0.12.1+1-jre/bin/java.exe \
 && for t in pdftoppm pdftocairo pdftotext pdfinfo java node npm; do ln -s /opt/egrlab/env/bin/$t /usr/local/bin/$t; done
COPY egrlab-entry.sh /usr/local/bin/egrlab-entry
COPY egrlab_winpaths.py /usr/lib/python3/dist-packages/egrlab_winpaths.py
RUN echo "import egrlab_winpaths" > /usr/lib/python3/dist-packages/egrlab_winpaths.pth

# ngspice: obraz KiCada ma libngspice0 (symulator KiCada); ngshared.py z P01 R2/R3 i P09 czyta NGSPICE_LIBRARY.
RUN test -f /usr/lib/x86_64-linux-gnu/libngspice.so.0
RUN rm /usr/local/share/ca-certificates/egrlab-build-proxy.crt && update-ca-certificates --fresh >/dev/null
ENV KICAD_LIBRARY_ROOT=/usr/share/kicad \
    KICAD_CLI=/usr/bin/kicad-cli \
    KICAD_PYTHON=/usr/bin/python3 \
    FREEROUTING_JAR=/opt/egrlab/freerouting/freerouting-2.1.0.jar \
    EGRLAB_FREEROUTING=/opt/egrlab/freerouting \
    EGRLAB_DOC_PYTHON=/usr/bin/python3 \
    EGRLAB_PDFTOPPM=/opt/egrlab/env/bin/pdftoppm \
    EGRLAB_FONT_DIR=/usr/share/fonts/truetype/liberation \
    EGRLAB_PDF_PYTHON=/usr/bin/python3 \
    EGRLAB_NODE=/opt/egrlab/env/bin/node \
    EGRLAB_SHARP=/opt/egrlab/node/node_modules/sharp \
    PDFTOPPM=/opt/egrlab/env/bin/pdftoppm \
    NGSPICE_LIBRARY=/usr/lib/x86_64-linux-gnu/libngspice.so.0 \
    PYTHONDONTWRITEBYTECODE=1 \
    LANG=pl_PL.UTF-8 LC_ALL=pl_PL.UTF-8 LANGUAGE=pl
USER kicad
WORKDIR /repo
ENTRYPOINT ["/usr/local/bin/egrlab-entry"]
CMD ["bash"]
