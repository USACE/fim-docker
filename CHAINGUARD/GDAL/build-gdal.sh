#!/usr/bin/env bash
#
# Build the Wolfi GDAL image with Buildx and persistent cache support.
#
# Examples:
#   ./build-gdal.sh
#   BUILD_JOBS=16 ./build-gdal.sh
#   PLATFORM=linux/arm64 ./build-gdal.sh
#   CACHE_MODE=registry \
#   CACHE_REF=registry.example.mil/geospatial/gdal:buildcache \
#   IMAGE=registry.example.mil/geospatial/gdal:3.13.3 \
#   PUSH=true \
#   ./build-gdal.sh
#

set -Eeuo pipefail

# ------------------------------------------------------------------------------
# Configuration: override any value through environment variables.
# ------------------------------------------------------------------------------

DOCKERFILE="${DOCKERFILE:-Dockerfile}"
CONTEXT_DIR="${CONTEXT_DIR:-.}"

PLATFORM="${PLATFORM:-linux/amd64}"
IMAGE="${IMAGE:-local/gdal-wolfi:3.13.3}"

# Set BUILD_JOBS based on builder memory/CPU capacity.
BUILD_JOBS="${BUILD_JOBS:-8}"

# Cache modes: local or registry.
CACHE_MODE="${CACHE_MODE:-local}"

# Local cache paths.
LOCAL_CACHE_DIR="${LOCAL_CACHE_DIR:-.buildx-cache}"

# Required only when CACHE_MODE=registry.
CACHE_REF="${CACHE_REF:-}"

# Local builds normally load the result into the local Docker image store.
# Registry builds normally push the final image.
PUSH="${PUSH:-false}"
LOAD="${LOAD:-true}"

# Optional build toggles.
ENABLE_OCI="${ENABLE_OCI:-ON}"
ENABLE_TILEDB="${ENABLE_TILEDB:-ON}"
ENABLE_SFCGAL="${ENABLE_SFCGAL:-ON}"
ENABLE_NETCDF="${ENABLE_NETCDF:-ON}"
ENABLE_POSTGRESQL="${ENABLE_POSTGRESQL:-ON}"
ENABLE_ARROW="${ENABLE_ARROW:-ON}"
ENABLE_HDF5="${ENABLE_HDF5:-ON}"
ENABLE_GEOS="${ENABLE_GEOS:-ON}"

# Use only when intentionally forcing the GDAL layer to rebuild.
GDAL_CACHE_BUST="${GDAL_CACHE_BUST:-0}"

# Optional custom base image override.
WOLFI_IMAGE="${WOLFI_IMAGE:-cgr.dev/usace-cwbi/chainguard-base-fips:20230214}"

# Dedicated Buildx builder to use for this build.
BUILDER="${BUILDER:-gdal-builder}"

# ------------------------------------------------------------------------------
# Functions
# ------------------------------------------------------------------------------

log() {
    printf '\n==> %s\n' "$*"
}

fail() {
    printf '\nERROR: %s\n' "$*" >&2
    exit 1
}

require_command() {
    command -v "$1" >/dev/null 2>&1 || fail "Required command not found: $1"
}

is_true() {
    case "$(printf '%s' "$1" | tr '[:upper:]' '[:lower:]')" in
        true|1|yes|y|on)
            return 0
            ;;
        *)
            return 1
            ;;
    esac
}

cleanup() {
    if [[ -n "${NEW_LOCAL_CACHE_DIR:-}" && -d "${NEW_LOCAL_CACHE_DIR}" ]]; then
        rm -rf "${NEW_LOCAL_CACHE_DIR}"
    fi
}

# ------------------------------------------------------------------------------
# Validation
# ------------------------------------------------------------------------------

require_command docker

[[ -f "${DOCKERFILE}" ]] || fail "Dockerfile not found: ${DOCKERFILE}"
[[ -d "${CONTEXT_DIR}" ]] || fail "Build context directory not found: ${CONTEXT_DIR}"

docker buildx version >/dev/null 2>&1 || fail \
    "Docker Buildx is unavailable. Install or enable Docker Buildx before running this script."

docker buildx inspect "${BUILDER}" >/dev/null 2>&1 || fail \
    "Buildx builder '${BUILDER}' does not exist. Create it with:

        docker buildx create \
        --name ${BUILDER} \
        --driver docker-container \
        --use \
        --bootstrap"

case "${CACHE_MODE}" in
    local|registry)
        ;;
    *)
        fail "CACHE_MODE must be either 'local' or 'registry'; received: ${CACHE_MODE}"
        ;;
esac

if [[ "${CACHE_MODE}" == "registry" && -z "${CACHE_REF}" ]]; then
    fail "CACHE_REF must be set when CACHE_MODE=registry."
fi

if is_true "${PUSH}" && is_true "${LOAD}"; then
    fail "PUSH and LOAD cannot both be true in the same build."
fi

if [[ "${CACHE_MODE}" == "registry" ]] && ! is_true "${PUSH}"; then
    log "CACHE_MODE=registry selected; enabling PUSH=true."
    PUSH=true
    LOAD=false
fi

# ------------------------------------------------------------------------------
# Build setup
# ------------------------------------------------------------------------------

log "Build configuration"
printf '  %-22s %s\n' \
    "Dockerfile:" "${DOCKERFILE}" \
    "Context:" "${CONTEXT_DIR}" \
    "Platform:" "${PLATFORM}" \
    "Image:" "${IMAGE}" \
    "Build jobs:" "${BUILD_JOBS}" \
    "Cache mode:" "${CACHE_MODE}" \
    "Push:" "${PUSH}" \
    "Load:" "${LOAD}"

BUILD_ARGS=(
    "--build-arg" "BUILD_JOBS=${BUILD_JOBS}"
    "--build-arg" "WOLFI_IMAGE=${WOLFI_IMAGE}"
    "--build-arg" "ENABLE_OCI=${ENABLE_OCI}"
    "--build-arg" "ENABLE_TILEDB=${ENABLE_TILEDB}"
    "--build-arg" "ENABLE_SFCGAL=${ENABLE_SFCGAL}"
    "--build-arg" "ENABLE_NETCDF=${ENABLE_NETCDF}"
    "--build-arg" "ENABLE_POSTGRESQL=${ENABLE_POSTGRESQL}"
    "--build-arg" "ENABLE_ARROW=${ENABLE_ARROW}"
    "--build-arg" "ENABLE_HDF5=${ENABLE_HDF5}"
    "--build-arg" "ENABLE_GEOS=${ENABLE_GEOS}"
    "--build-arg" "GDAL_CACHE_BUST=${GDAL_CACHE_BUST}"
)

BUILD_COMMAND=(
    docker buildx build
    "--builder" "${BUILDER}"
    "--file" "${DOCKERFILE}"
    "--platform" "${PLATFORM}"
    "--tag" "${IMAGE}"
    "--progress=plain"
)

BUILD_COMMAND+=("${BUILD_ARGS[@]}")

# ------------------------------------------------------------------------------
# Cache configuration
# ------------------------------------------------------------------------------

if [[ "${CACHE_MODE}" == "local" ]]; then
    # Export to a new directory, then rotate it only after a successful build.
    # This avoids corrupting the usable cache when a build fails.
    NEW_LOCAL_CACHE_DIR="$(mktemp -d "${LOCAL_CACHE_DIR}.new.XXXXXX")"
    trap cleanup EXIT

    if [[ -d "${LOCAL_CACHE_DIR}" ]]; then
        BUILD_COMMAND+=(
            "--cache-from" "type=local,src=${LOCAL_CACHE_DIR}"
        )
    fi

    BUILD_COMMAND+=(
        "--cache-to" "type=local,dest=${NEW_LOCAL_CACHE_DIR},mode=max"
    )
else
    BUILD_COMMAND+=(
        "--cache-from" "type=registry,ref=${CACHE_REF}"
        "--cache-to" "type=registry,ref=${CACHE_REF},mode=max"
    )
fi

# ------------------------------------------------------------------------------
# Output configuration
# ------------------------------------------------------------------------------

if is_true "${PUSH}"; then
    BUILD_COMMAND+=("--push")
elif is_true "${LOAD}"; then
    BUILD_COMMAND+=("--load")
else
    log "Neither PUSH nor LOAD is enabled. The image will remain only in Buildx cache."
fi

BUILD_COMMAND+=("${CONTEXT_DIR}")

# ------------------------------------------------------------------------------
# Execute build
# ------------------------------------------------------------------------------

log "Starting build"
printf '  %q' "${BUILD_COMMAND[@]}"
printf '\n\n'

"${BUILD_COMMAND[@]}"

# Rotate the local cache only after successful completion.
if [[ "${CACHE_MODE}" == "local" ]]; then
    log "Updating local Buildx cache"

    rm -rf "${LOCAL_CACHE_DIR}"
    mv "${NEW_LOCAL_CACHE_DIR}" "${LOCAL_CACHE_DIR}"

    unset NEW_LOCAL_CACHE_DIR
fi

log "Build completed successfully"
printf '  Image: %s\n' "${IMAGE}"

if is_true "${LOAD}"; then
    printf '  Verify: docker run --rm %s gdalinfo --version\n' "${IMAGE}"
fi