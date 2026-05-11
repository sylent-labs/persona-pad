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
#
# All log lines go to stdout so Render's "Logs" tab surfaces them with the
# same prominence as application logs. Errors that should kill the container
# go to stderr right before the exit.

set -eu

log() {
  printf '[entrypoint] %s\n' "$*"
}

fatal() {
  printf '[entrypoint] FATAL: %s\n' "$*" >&2
  exit 1
}

log "starting persona-pad container"

if [ -z "${GIT_CRYPT_KEY_B64:-}" ]; then
  fatal "GIT_CRYPT_KEY_B64 is not set. In Render -> service -> Environment, paste the base64-encoded git-crypt key. Generate locally with: git-crypt export-key /tmp/persona-pad.key && base64 < /tmp/persona-pad.key"
fi

REPO_ROOT="/app"

if [ ! -d "$REPO_ROOT/.git" ]; then
  fatal "$REPO_ROOT/.git is missing; the image was built without the .git directory. Verify .dockerignore does not exclude .git and that dockerContext is the repo root."
fi

log "decoding git-crypt key"

KEY_FILE="$(mktemp)"
trap 'rm -f "$KEY_FILE"' EXIT INT TERM

# Strip any whitespace (newlines, spaces, tabs) the user may have introduced
# when copy-pasting the base64 value into Render's env var UI. GNU base64 is
# usually lenient, but pasted values from terminals often include line wraps
# that break decoding on some platforms.
printf '%s' "$GIT_CRYPT_KEY_B64" | tr -d '[:space:]' | base64 -d > "$KEY_FILE" 2>/tmp/base64.err || {
  err="$(cat /tmp/base64.err 2>/dev/null || true)"
  fatal "failed to base64-decode GIT_CRYPT_KEY_B64. Make sure the env var holds the *base64* of the git-crypt key, not the raw key. base64 stderr: ${err}"
}

if [ ! -s "$KEY_FILE" ]; then
  fatal "decoded git-crypt key is empty. The env var is probably missing content."
fi

log "decoded git-crypt key ($(wc -c < "$KEY_FILE") bytes)"

cd "$REPO_ROOT"

if [ -f .git/git-crypt/keys/default ]; then
  log "git-crypt already unlocked, skipping"
else
  log "running git-crypt unlock"
  if ! git-crypt unlock "$KEY_FILE" >/tmp/unlock.out 2>/tmp/unlock.err; then
    out="$(cat /tmp/unlock.out 2>/dev/null || true)"
    err="$(cat /tmp/unlock.err 2>/dev/null || true)"
    fatal "git-crypt unlock failed. stdout: ${out} | stderr: ${err}"
  fi
  log "git-crypt unlock succeeded"
fi

rm -f "$KEY_FILE"
trap - EXIT INT TERM

# Sanity check: the decrypted profile.md should be readable text, not the
# git-crypt binary header. If unlock silently no-op'd, this catches it.
SAMPLE="$REPO_ROOT/backend/app/data/persona/van_keith/profile.md"
if [ -f "$SAMPLE" ]; then
  if head -c 9 "$SAMPLE" | grep -q "GITCRYPT"; then
    fatal "persona files are still encrypted after unlock. The git-crypt key likely does not match this repo."
  fi
  log "persona data verified decrypted"
else
  log "warning: $SAMPLE not present, skipping decryption sanity check"
fi

cd "$REPO_ROOT/backend"

log "execing: $*"
exec "$@"
