#!/bin/bash
# profile-gateway-start.sh — Source .env and start Hermes Gateway for a named profile
# Usage: ./profile-gateway-start.sh <profile_name>
#
# Designed to be run inside tmux for persistence:
#   tmux new-session -d -s <name> "/path/to/profile-gateway-start.sh <name>"
#
# This script ensures the profile's .env is sourced BEFORE the gateway starts,
# which hermes -p <name> gateway run --replace does NOT do automatically.

set -euo pipefail

PROFILE="${1:?Usage: $0 <profile_name>}"
ENV_FILE="$HOME/.hermes/profiles/${PROFILE}/.env"
LOG_FILE="$HOME/.hermes/logs/${PROFILE}.log"

if [ ! -f "$ENV_FILE" ]; then
  echo "ERROR: .env file not found at $ENV_FILE" | tee -a "$LOG_FILE"
  exit 1
fi

# Source the .env file (set -a exports all vars automatically)
set -a
source "$ENV_FILE"
set +a

exec python -m hermes_cli.main gateway run --profile "$PROFILE" &>> "$LOG_FILE"
