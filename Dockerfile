# CAMBIATO: Base image ora è Ubuntu 22.04 LTS (Long-Term Support)
FROM ubuntu:22.04

# installation settings
ARG TL_MIRROR="https://texlive.info/CTAN/systems/texlive/tlnet"

#    - 'DEBIAN_FRONTEND=noninteractive' evita che apt-get faccia domande.
#    - '--no-install-recommends' mantiene l'immagine più piccola.
#    - Aggiunto 'wget' che è usato nello script, 'ca-certificates' per connessioni sicure.
#    - Mantenuti 'perl', 'fontconfig', 'gnupg'.
RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
    wget \
    perl \
    fontconfig \
    gnupg \
    ca-certificates \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

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

# Il path per i binari su Ubuntu (glibc) è diverso da Alpine (musl).
#    Sostituito 'x86_64-linuxmusl' con 'x86_64-linux'. Questo è un punto CRUCIALE.
ENV PATH="${PATH}:/opt/texlive/bin/x86_64-linux"

ARG TL_SCHEME_BASIC="y"
RUN if [ "$TL_SCHEME_BASIC" = "y" ]; then tlmgr install scheme-basic; fi

ARG TL_SCHEME_SMALL="y"
RUN if [ "$TL_SCHEME_SMALL" = "y" ]; then tlmgr install scheme-small; fi

ARG TL_SCHEME_MEDIUM="y"
RUN if [ "$TL_SCHEME_MEDIUM" = "y" ]; then tlmgr install scheme-medium; fi

ARG TL_SCHEME_FULL="y"
RUN if [ "$TL_SCHEME_FULL" = "y" ]; then tlmgr install scheme-full; fi
