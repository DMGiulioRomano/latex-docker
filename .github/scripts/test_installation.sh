#!/bin/bash
set -e

MIRROR_URL="$1"
LOG_FILE="installation_log_$(date +%Y%m%d_%H%M%S).txt"

echo "Testing installation from: $MIRROR_URL" | tee "$LOG_FILE"
echo "Timestamp: $(date)" | tee -a "$LOG_FILE"

# Crea directory di test
TEST_DIR="/tmp/texlive_test_$(date +%s)"
mkdir -p "$TEST_DIR"
cd "$TEST_DIR"

echo "Creating test directory: $TEST_DIR" | tee -a "$LOG_FILE"

# Funzione per pulire alla fine
cleanup() {
    echo "Cleaning up..." | tee -a "$LOG_FILE"
    cd /tmp
    rm -rf "$TEST_DIR"
}
trap cleanup EXIT

# Download installer
echo "Downloading installer..." | tee -a "$LOG_FILE"
if ! wget --timeout=60 --tries=3 "$MIRROR_URL/install-tl-unx.tar.gz" >> "$LOG_FILE" 2>&1; then
    echo "❌ FAILED: Cannot download installer" | tee -a "$LOG_FILE"
    exit 1
fi

# Estrai installer
echo "Extracting installer..." | tee -a "$LOG_FILE"
if ! tar xzf install-tl-unx.tar.gz >> "$LOG_FILE" 2>&1; then
    echo "❌ FAILED: Cannot extract installer" | tee -a "$LOG_FILE"
    exit 1
fi

cd install-tl-*

# Test versioni e piattaforma
echo "Testing installer basics..." | tee -a "$LOG_FILE"
if ! ./install-tl --version >> "$LOG_FILE" 2>&1; then
    echo "❌ FAILED: Installer version check failed" | tee -a "$LOG_FILE"
    exit 1
fi

echo "Platform: $(./install-tl --print-platform)" | tee -a "$LOG_FILE"

# Test accesso repository
echo "Testing repository access..." | tee -a "$LOG_FILE"
if ! ./install-tl --location "$MIRROR_URL" --no-interaction --version >> "$LOG_FILE" 2>&1; then
    echo "❌ FAILED: Repository access test failed" | tee -a "$LOG_FILE"
    exit 1
fi

# Test installazione minima (solo se richiesto esplicitamente)
if [[ "$2" == "full" ]]; then
    echo "Starting minimal installation test..." | tee -a "$LOG_FILE"
    
    # Crea profile minimale
    cat > minimal.profile << EOF
selected_scheme scheme-minimal
instopt_adjustpath 0
tlpdbopt_install_docfiles 0
tlpdbopt_install_srcfiles 0
TEXDIR $TEST_DIR/texlive
TEXMFLOCAL $TEST_DIR/texlive/texmf-local
TEXMFSYSCONFIG $TEST_DIR/texlive/texmf-config
TEXMFSYSVAR $TEST_DIR/texlive/texmf-var
TEXMFHOME $TEST_DIR/texlive/texmf-home
EOF

    if ./install-tl --profile minimal.profile --location "$MIRROR_URL" >> "$LOG_FILE" 2>&1; then
        echo "✅ SUCCESS: Minimal installation completed" | tee -a "$LOG_FILE"
    else
        echo "❌ FAILED: Minimal installation failed" | tee -a "$LOG_FILE"
        exit 1
    fi
else
    echo "✅ SUCCESS: Basic installation tests passed" | tee -a "$LOG_FILE"
    echo "Use 'full' argument to test complete installation" | tee -a "$LOG_FILE"
fi

echo "All tests completed successfully!" | tee -a "$LOG_FILE"