# Build context for this Dockerfile is the repo root. Render's Docker build
# strips the .git directory out of the build context delivered to BuildKit
# even though their clone step downloads the full repo, so we cannot rely on
# the original .git surviving the COPY. git-crypt needs a git repo with the
# encrypted blobs at HEAD to be able to decrypt, so the build below
# reconstructs a minimal single-commit git repo over the copied files when
# .git is absent. Local builds that already include .git skip this step and
# use the real history.

FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        ca-certificates \
        git \
        git-crypt \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY backend/requirements.txt /app/backend/requirements.txt
RUN pip install -r /app/backend/requirements.txt

COPY . /app

# If the build context didn't include .git (Render), synthesise a fresh repo
# with the encrypted files as the only commit. The GITCRYPT magic header on
# each encrypted blob is preserved by COPY, so when the runtime entrypoint
# runs `git-crypt unlock`, git's smudge filter re-checks out HEAD and
# decrypts those blobs in place. No clean filter is configured at add-time,
# so git stores the encrypted bytes verbatim, which is exactly what
# `git-crypt unlock` expects to find.
RUN cd /app \
    && if [ ! -d .git ]; then \
         git init -q \
         && git config user.email "build@persona-pad" \
         && git config user.name "build" \
         && git add -A \
         && git commit -q -m "build snapshot"; \
       fi

RUN chmod +x /app/docker-entrypoint.sh

WORKDIR /app/backend

EXPOSE 8000

ENTRYPOINT ["/app/docker-entrypoint.sh"]
CMD ["sh", "-c", "exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
