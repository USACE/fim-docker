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

## Dynamic Color Classification (MapScript)

This image now includes an optional MapScript-based CGI gateway for dynamic raster class colors.

### What It Does

- Keeps normal requests on native `mapserv`.
- Routes only colorized requests (query params like `custom_color_1` or `c1r`) through a Python MapScript gateway:
	- `runtime/usr/local/bin/mapserv_wrapper`
	- `runtime/usr/local/bin/mapserv_mapscript_gateway.py`
- Applies color overrides to `cog_xyz` custom classes at request time, then dispatches OWS normally.

### Build/Runtime Requirement

The Docker build enables Python MapScript (`-DWITH_PYTHON=1` in `Dockerfile`).
If your container is already running, rebuild and redeploy before testing dynamic color requests.

### Supported Color Parameter Formats

1. Hex colors:
- `custom_color_1=#D0F0FF`
- `custom_color_2=#70B8E6`
- `custom_color_3=#3A78C2`
- `custom_color_4=#1F3F7A`

2. Verbose RGB triplets:
- `custom_color_1_r=208&custom_color_1_g=240&custom_color_1_b=255`
- Repeat for `custom_color_2_*`, `custom_color_3_*`, `custom_color_4_*`

3. Short RGB triplets:
- `c1r=208&c1g=240&c1b=255`
- Repeat for `c2*`, `c3*`, `c4*`

Rules:
- RGB channels must be integers in `0..255`.
- Partial triplets are rejected (`400 Bad Request`).
- At least one valid color slot must be provided on the gateway path.

### Example: Hex Colors

```text
/inundation?SERVICE=WMS&REQUEST=GetMap&LAYERS=cog_xyz&CLASSGROUP=custom4
&class_1_1=0&class_1_2=2
&class_2_1=2&class_2_2=6
&class_3_1=6&class_3_2=15
&class_4_1=15
&custom_color_1=%23D0F0FF
&custom_color_2=%2370B8E6
&custom_color_3=%233A78C2
&custom_color_4=%231F3F7A
```

### Example: Short RGB

```text
/inundation?SERVICE=WMS&REQUEST=GetMap&LAYERS=cog_xyz&CLASSGROUP=custom4
&class_1_1=0&class_1_2=2
&class_2_1=2&class_2_2=6
&class_3_1=6&class_3_2=15
&class_4_1=15
&c1r=208&c1g=240&c1b=255
&c2r=112&c2g=184&c2b=230
&c3r=58&c3g=120&c3b=194
&c4r=31&c4g=63&c4b=122
```

### Notes

- Existing dynamic class break parameters (for example `class_1_1`, `class_1_2`, etc.) continue to work.
- This gateway currently targets layer name `cog_xyz` in the selected mapfile.
