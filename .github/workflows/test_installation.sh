#!/bin/bash
# .github/scripts/test_installation.sh

set -e  # Exit on error

echo "Starting installation tests..."

# Legge i mirror validi dal file generato dallo script Python
if [ ! -f valid_mirrors.txt ]; then
    echo "Error: valid_mirrors.txt not found"
    exit 1
fi

while read mirror; do
    echo "Testing installation from: $mirror"
    cd /tmp
    mkdir -p test_install
    cd test_install

    # Scarica l'installer
    if wget --timeout=30 "${mirror}install-tl-unx.tar.gz"; then
        echo "Downloaded installer from $mirror"
    else
        echo "Failed to download installer from $mirror"
        continue
    fi

    tar xzf install-tl-unx.tar.gz
    cd install-tl-*

    # Test di base dell'installer
    echo "Testing installer version..."
    ./install-tl --version

    echo "Testing platform detection..."
    ./install-tl --print-platform

    echo "Testing repository access..."
    ./install-tl --location "$mirror" --no-interaction --version

    echo "✅ Installation test passed for $mirror"
    cd /tmp
    rm -rf test_install
done < valid_mirrors.txt

echo "All installation tests completed."
