#!/usr/bin/env bash
# Build and (re)deploy LLOT with docker compose, verify health, roll back on failure.
#
# Usage: scripts/deploy.sh [--pull] [--skip-tests] [-f compose-file]
#   --pull         git pull --ff-only before deploying
#   --skip-tests   don't run the unit tests before building
#   -f FILE        compose file (default: docker-compose.yml)
set -euo pipefail

cd "$(dirname "$0")/.."

COMPOSE_FILE="docker-compose.yml"
PULL=false
RUN_TESTS=true
SERVICE="llot"
HEALTH_TIMEOUT=90

while [[ $# -gt 0 ]]; do
    case "$1" in
        --pull) PULL=true ;;
        --skip-tests) RUN_TESTS=false ;;
        -f) COMPOSE_FILE="$2"; shift ;;
        -h|--help) sed -n '2,8p' "$0"; exit 0 ;;
        *) echo "Unknown option: $1" >&2; exit 2 ;;
    esac
    shift
done

compose() { docker compose -f "$COMPOSE_FILE" "$@"; }
log() { printf '\033[36m==>\033[0m %s\n' "$*"; }

[[ -f .env ]] || { echo "Missing .env (copy .env.example and edit it)" >&2; exit 1; }

if $PULL; then
    log "Pulling latest code"
    git pull --ff-only
fi

if $RUN_TESTS; then
    if [[ -x .venv/bin/pytest ]]; then
        log "Running unit tests"
        .venv/bin/pytest -q
    else
        log "No .venv found, skipping tests (make install to enable)"
    fi
fi

IMAGE="$(compose config --images | head -1)"
if docker image inspect "$IMAGE" >/dev/null 2>&1; then
    log "Keeping current image as ${IMAGE%%:*}:previous for rollback"
    docker tag "$IMAGE" "${IMAGE%%:*}:previous"
    HAVE_PREVIOUS=true
else
    HAVE_PREVIOUS=false
fi

log "Building image $IMAGE"
compose build
log "Starting containers"
compose up -d

wait_healthy() {
    local container status deadline=$((SECONDS + HEALTH_TIMEOUT))
    container="$(compose ps -q "$SERVICE")"
    while (( SECONDS < deadline )); do
        status="$(docker inspect -f '{{.State.Health.Status}}' "$container" 2>/dev/null || echo missing)"
        [[ "$status" == healthy ]] && return 0
        [[ "$status" == unhealthy ]] && return 1
        sleep 2
    done
    return 1
}

check_api() {
    local port overall
    port="$(compose port "$SERVICE" 8080 | sed 's/.*://')"
    overall="$(curl -fsS "http://localhost:${port}/api/health" | python3 -c 'import json,sys; print(json.load(sys.stdin)["overall"])')"
    log "API health: $overall"
    [[ "$overall" != error ]]
}

if wait_healthy && check_api; then
    log "Deployed successfully"
    docker image prune -f >/dev/null
    exit 0
fi

echo "Deployment failed health checks" >&2
compose logs --tail 50 "$SERVICE" >&2 || true
if $HAVE_PREVIOUS; then
    log "Rolling back to previous image"
    docker tag "${IMAGE%%:*}:previous" "$IMAGE"
    compose up -d --no-build
fi
exit 1
