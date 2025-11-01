# Cambia questo con il tuo username su Docker Hub / GHCR
IMAGE_ID ?= DMGiulioRomano/latex-docker-ubuntu
VERSION ?= latest

TL_MIRROR ?= https://ctan.mirror.garr.it/mirrors/ctan/systems/texlive/tlnet

_default: all

# I comandi 'docker build' ora usano implicitamente il nostro nuovo Dockerfile.
# Non c'è più bisogno del flag '-f'.
all: minimal basic small medium full

minimal:
	docker build . -t $(IMAGE_ID):$(VERSION)-minimal \
	    --build-arg TL_MIRROR="$(TL_MIRROR)" \
	    --build-arg TL_SCHEME_BASIC=n \
	    --build-arg TL_SCHEME_SMALL=n \
	    --build-arg TL_SCHEME_MEDIUM=n \
	    --build-arg TL_SCHEME_FULL=n

basic:
	docker build . -t $(IMAGE_ID):$(VERSION)-basic \
	    --build-arg TL_MIRROR="$(TL_MIRROR)" \
	    --build-arg TL_SCHEME_BASIC=y \
	    --build-arg TL_SCHEME_SMALL=n \
	    --build-arg TL_SCHEME_MEDIUM=n \
	    --build-arg TL_SCHEME_FULL=n

small:
	docker build . -t $(IMAGE_ID):$(VERSION)-small \
	    --build-arg TL_MIRROR="$(TL_MIRROR)" \
	    --build-arg TL_SCHEME_BASIC=y \
	    --build-arg TL_SCHEME_SMALL=y \
	    --build-arg TL_SCHEME_MEDIUM=n \
	    --build-arg TL_SCHEME_FULL=n

medium:
	docker build . -t $(IMAGE_ID):$(VERSION)-medium \
	    --build-arg TL_MIRROR="$(TL_MIRROR)" \
	    --build-arg TL_SCHEME_BASIC=y \
	    --build-arg TL_SCHEME_SMALL=y \
	    --build-arg TL_SCHEME_MEDIUM=y \
	    --build-arg TL_SCHEME_FULL=n

full:
	docker build . -t $(IMAGE_ID):$(VERSION)-full -t $(IMAGE_ID):$(VERSION) \
	    --build-arg TL_MIRROR="$(TL_MIRROR)" \
	    --build-arg TL_SCHEME_BASIC=y \
	    --build-arg TL_SCHEME_SMALL=y \
	    --build-arg TL_SCHEME_MEDIUM=y \
	    --build-arg TL_SCHEME_FULL=y

test-%: %
	IMAGE_ID=$(IMAGE_ID) VERSION=$(VERSION) \
	    docker compose -f test.compose.yaml run --build sut-$<

test: minimal basic small medium full
	IMAGE_ID=$(IMAGE_ID) VERSION=$(VERSION) \
	    docker compose -f test.compose.yaml run --build sut

.PHONY: *
