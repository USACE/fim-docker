# CHAINGUARD MAPSERVER Docker Image

This image builds MapServer on top of the Chainguard GDAL base and runs it with Apache on port `8080`.

## Build

Build from the repository root:

```sh
docker build \
	-f CHAINGUARD/MAPSERVER/Dockerfile \
	-t fim-mapserver:dev \
	.
```

## Build Arguments

- `platform` (default: `linux/amd64`)
- `MAPSERVER_BRANCH` (default: `branch-8-6`)
- `MAPSERVER_REPO` (default: `https://github.com/mapserver/mapserver`)
- `WITH_ORACLE` (default: `ON`)
- `SMOKE_TEST` (default: `0`)
- `BUILD_ENV` (default: `prod`)

## Dev Build (aws-adfs)

When `BUILD_ENV=dev`, the Dockerfile installs `aws-adfs` in the runner image.

```sh
docker build \
	-f CHAINGUARD/MAPSERVER/Dockerfile \
	-t fim-mapserver:dev \
	--build-arg BUILD_ENV=dev \
	.
```

For non-dev builds (default), `aws-adfs` is not installed.

## Optional Oracle Toggle

To build without Oracle Spatial support:

```sh
docker build \
	-f CHAINGUARD/MAPSERVER/Dockerfile \
	-t fim-mapserver:no-oracle \
	--build-arg WITH_ORACLE=OFF \
	.
```

## Run

```sh
docker run --rm -p 8080:8080 fim-mapserver:latest
```

MapServer runtime content is expected under `/etc/mapserver` in the container.
