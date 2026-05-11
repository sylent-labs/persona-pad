#!/usr/bin/env sh
# Decrypts the git-crypt protected persona data once at container start, then
# execs the supplied command (uvicorn by default).
#
# Why at runtime instead of build time:
#   - Render's Docker builds don't expose runtime env vars during `docker
#     build`, so we'd otherwise need build args + a separate secret pipeline.
#   - The plaintext persona content stays out of the image layers; it only
#     materializes inside the running container's writable layer.
#
# Required env: GIT_CRYPT_KEY_B64 = base64-encoded git-crypt symmetric key
#   Generate locally with:
#       git-crypt export-key /tmp/persona-pad.key
#       base64 < /tmp/persona-pad.key
#   Paste the output into Render -> service -> Environment.

set -eu

if [ -z "${GIT_CRYPT_KEY_B64:-}" ]; then
  echo "FATAL: GIT_CRYPT_KEY_B64 is required to decrypt persona data" >&2
  exit 1
fi

REPO_ROOT="/app"

if [ ! -d "$REPO_ROOT/.git" ]; then
  echo "FATAL: $REPO_ROOT/.git is missing; rebuild with full repo context" >&2
  exit 1
fi

KEY_FILE="$(mktemp)"
trap 'rm -f "$KEY_FILE"' EXIT INT TERM

printf '%s' "$GIT_CRYPT_KEY_B64" | base64 -d > "$KEY_FILE"

cd "$REPO_ROOT"

if [ -f .git/git-crypt/keys/default ]; then
  echo "git-crypt already unlocked, skipping" >&2
else
  git-crypt unlock "$KEY_FILE"
fi

rm -f "$KEY_FILE"
trap - EXIT INT TERM

cd "$REPO_ROOT/backend"

exec "$@"
