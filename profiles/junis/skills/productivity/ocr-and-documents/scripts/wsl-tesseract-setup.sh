#!/bin/bash
# WSL Tesseract 5.5 setup — no sudo required
# Installs a full offline tesseract + Chinese OCR via deb extraction
set -euo pipefail

TESSDIR="${1:-$HOME/.local/tesseract}"
mkdir -p "$TESSDIR"
mkdir -p "$HOME/.local/bin"

echo "[1/3] Downloading deb packages..."
for pkg in tesseract-ocr libtesseract5 libleptonica6 libarchive13t64 \
  libjpeg-turbo8 libgif7 libtiff6 liblerc4 libjbig0 libdeflate0; do
  URL=$(apt-cache show "$pkg" 2>/dev/null | grep "Filename:" | head -1 | \
    awk '{print "http://archive.ubuntu.com/ubuntu/" $2}')
  if [ -n "$URL" ]; then
    echo "  $pkg"
    wget -q --timeout=30 "$URL" -O "/tmp/${pkg}.deb"
  else
    echo "  WARNING: $pkg not found in apt cache"
  fi
done

echo "[2/3] Extracting to $TESSDIR..."
for deb in /tmp/tesseract-ocr.deb /tmp/libtesseract5.deb /tmp/libleptonica6.deb \
  /tmp/libarchive13t64.deb /tmp/libjpeg-turbo8.deb /tmp/libgif7.deb \
  /tmp/libtiff6.deb /tmp/liblerc4.deb /tmp/libjbig0.deb /tmp/libdeflate0.deb; do
  [ -f "$deb" ] && dpkg --extract "$deb" "$TESSDIR" 2>/dev/null
done

echo "[2b/3] Downloading Chinese language data..."
wget -q "https://github.com/tesseract-ocr/tessdata/raw/main/chi_sim.traineddata" \
  -O "$TESSDIR/usr/share/tesseract-ocr/5/tessdata/chi_sim.traineddata" 2>/dev/null || {
  # Fallback: extract from deb
  URL=$(apt-cache show tesseract-ocr-chi-sim 2>/dev/null | grep "Filename:" | head -1 | \
    awk '{print "http://archive.ubuntu.com/ubuntu/" $2}')
  wget -q "$URL" -O /tmp/tesseract-ocr-chi-sim.deb
  dpkg --extract /tmp/tesseract-ocr-chi-sim.deb "$TESSDIR" 2>/dev/null
}

echo "[3/3] Creating wrapper script..."
cat > "$HOME/.local/bin/hermes-ocr" << 'WRAPPER'
#!/bin/bash
export TESSDIR="${TESSDIR:-$HOME/.local/tesseract}"
export LD_LIBRARY_PATH="$TESSDIR/usr/lib/x86_64-linux-gnu${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}"
export TESSDATA_PREFIX="$TESSDIR/usr/share/tesseract-ocr/5/tessdata"
exec "$TESSDIR/usr/bin/tesseract" "$@"
WRAPPER
chmod +x "$HOME/.local/bin/hermes-ocr"

echo ""
echo "=== Verification ==="
export PATH="$HOME/.local/bin:$PATH"
hermes-ocr --version 2>&1 | head -1
hermes-ocr --list-langs 2>&1
echo ""
echo "Setup complete. Add to ~/.bashrc:"
echo '  export PATH="$HOME/.local/bin:$PATH"'
