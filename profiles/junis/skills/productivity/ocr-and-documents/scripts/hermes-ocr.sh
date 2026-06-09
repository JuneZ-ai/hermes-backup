#!/bin/bash
# Hermes-WSL Tesseract wrapper — sourced from wsl-tesseract-setup.sh
# Usage: hermes-ocr <image> [options]
export TESSDIR="${TESSDIR:-/home/hermes/.local/tesseract}"
export LD_LIBRARY_PATH="$TESSDIR/usr/lib/x86_64-linux-gnu${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}"
export TESSDATA_PREFIX="$TESSDIR/usr/share/tesseract-ocr/5/tessdata"
exec "$TESSDIR/usr/bin/tesseract" "$@"
