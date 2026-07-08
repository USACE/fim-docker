# Chainguard GDAL Image Build Guide

This directory contains a configurable GDAL build based on Chainguard Wolfi.

## Build From Repository Root

Run commands from the repository root folder.

Default build with all optional integrations enabled:

```bash
docker build --platform linux/amd64 -f CHAINGUARD/GDAL/Dockerfile -t gdal-chainguard:full .
```

## Optional Feature Toggles

The Dockerfile supports build-time toggles using ON or OFF values:

- ENABLE_OCI
- ENABLE_TILEDB
- ENABLE_SFCGAL
- ENABLE_NETCDF
- ENABLE_POSTGRESQL
- ENABLE_ARROW
- ENABLE_HDF5
- ENABLE_GEOS

Example: disable OCI and TileDB:

```bash
docker build --platform linux/amd64 -f CHAINGUARD/GDAL/Dockerfile \
	--build-arg ENABLE_OCI=OFF \
	--build-arg ENABLE_TILEDB=OFF \
	-t gdal-chainguard:no-oci-no-tiledb .
```

Example: leaner build (disable Arrow/Parquet, NetCDF, PostgreSQL, SFCGAL):

```bash
docker build --platform linux/amd64 -f CHAINGUARD/GDAL/Dockerfile \
	--build-arg ENABLE_ARROW=OFF \
	--build-arg ENABLE_NETCDF=OFF \
	--build-arg ENABLE_POSTGRESQL=OFF \
	--build-arg ENABLE_SFCGAL=OFF \
	-t gdal-chainguard:lean .
```

Note: Parquet support follows ENABLE_ARROW in this Dockerfile.
Note: NetCDF support requires ENABLE_HDF5=ON.

Example: disable HDF5 (and NetCDF):

```bash
docker build --platform linux/amd64 -f CHAINGUARD/GDAL/Dockerfile \
	--build-arg ENABLE_HDF5=OFF \
	--build-arg ENABLE_NETCDF=OFF \
	-t gdal-chainguard:no-hdf5 .
```

Example: disable GEOS:

```bash
docker build --platform linux/amd64 -f CHAINGUARD/GDAL/Dockerfile \
	--build-arg ENABLE_GEOS=OFF \
	-t gdal-chainguard:no-geos .
```

Example: minimal with oci:

```bash
docker build --platform linux/amd64 -f CHAINGUARD/GDAL/Dockerfile \
	--build-arg ENABLE_GEOS=OFF \
	--build-arg ENABLE_TILEDB=OFF \
	--build-arg ENABLE_SFCGAL=OFF \
	--build-arg ENABLE_NETCDF=OFF \
	--build-arg ENABLE_POSTGRESQL=OFF \
	--build-arg ENABLE_ARROW=OFF \
	--build-arg ENABLE_HDF5=OFF \
	--build-arg ENABLE_GEOS=OFF \
	-t gdal-chainguard:oci-only .
```

## Verify Build

Check GDAL version:

```bash
docker run --rm gdal-chainguard:full gdalinfo --version
```

List raster and vector drivers:

```bash
docker run --rm gdal-chainguard:full gdalinfo --formats
docker run --rm gdal-chainguard:full ogr2ogr --formats
```

## Troubleshooting

- If build fails after changing flags, retry with no cache:

```bash
docker build --no-cache --platform linux/amd64 -f CHAINGUARD/GDAL/Dockerfile -t gdal-chainguard:full .
```

- If Oracle download fails, set ENABLE_OCI=OFF and rebuild.
