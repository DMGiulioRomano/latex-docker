# Base image è ora Ubuntu 22.04 LTS (Long-Term Support)
FROM ubuntu:22.04

# Impostazioni di installazione
ARG TL_MIRROR="https://ctan.mirror.garr.it/mirrors/ctan/systems/texlive/tlnet"

# Usa 'apt-get' per installare le dipendenze di base per Ubuntu.
# - 'DEBIAN_FRONTEND=noninteractive' evita che apt-get faccia domande.
# - '--no-install-recommends' mantiene l'immagine più leggera.
# - 'apt-get clean' e 'rm' puliscono la cache per ridurre le dimensioni finali.
RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
    wget \
    perl \
    fontconfig \
    gnupg \
    ca-certificates \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# La logica di installazione di TeX Live è robusta e viene mantenuta.
# Funziona perfettamente anche su Ubuntu.
RUN mkdir "/tmp/texlive" && cd "/tmp/texlive" && \
    wget "$TL_MIRROR/install-tl-unx.tar.gz" && \
    tar xzvf ./install-tl-unx.tar.gz && \
    ( \
        echo "selected_scheme scheme-minimal" && \
        echo "instopt_adjustpath 0" && \
        echo "tlpdbopt_install_docfiles 0" && \
        echo "tlpdbopt_install_srcfiles 0" && \
        echo "TEXDIR /opt/texlive/" && \
        echo "TEXMFLOCAL /opt/texlive/texmf-local" && \
        echo "TEXMFSYSCONFIG /opt/texlive/texmf-config" && \
        echo "TEXMFSYSVAR /opt/texlive/texmf-var" && \
        echo "TEXMFHOME ~/.texmf" \
    ) > "/tmp/texlive.profile" && \
    "./install-tl-"*"/install-tl" --location "$TL_MIRROR" -profile "/tmp/texlive.profile" && \
    rm -vf "/opt/texlive/install-tl" && \
    rm -vf "/opt/texlive/install-tl.log" && \
    rm -vrf /tmp/*

# PUNTO CRUCIALE: Corretto il PATH per i binari su architettura Ubuntu (glibc).
#ENV PATH="${PATH}:/opt/texlive/bin/x86_64-linux"
ENV PATH="${PATH}:/opt/texlive/bin/*"

# La logica per l'installazione incrementale degli schemi viene mantenuta.
ARG TL_SCHEME_BASIC="y"
RUN if [ "$TL_SCHEME_BASIC" = "y" ]; then tlmgr install scheme-basic; fi

ARG TL_SCHEME_SMALL="y"
RUN if [ "$TL_SCHEME_SMALL" = "y" ]; then tlmgr install scheme-small; fi

ARG TL_SCHEME_MEDIUM="y"
RUN if [ "$TL_SCHEME_MEDIUM" = "y" ]; then tlmgr install scheme-medium; fi

ARG TL_SCHEME_FULL="y"
RUN if [ "$TL_SCHEME_FULL" = "y" ]; then tlmgr install scheme-full; fi
