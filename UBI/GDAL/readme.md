# UBI GDAL Image Build Guide

This directory contains a configurable GDAL build based on UBI9.

## Build From Repository Root

Run commands from the repository root folder.

Default build with all optional integrations enabled:

```bash
docker build --platform linux/amd64 -f UBI/GDAL/Dockerfile -t ubi-gdal:full .
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
docker build --platform linux/amd64 -f UBI/GDAL/Dockerfile \
	--build-arg ENABLE_OCI=OFF \
	--build-arg ENABLE_TILEDB=OFF \
	-t ubi-gdal:no-oci-no-tiledb .
```

Example: leaner build (disable Arrow/Parquet, NetCDF, PostgreSQL, SFCGAL):

```bash
docker build --platform linux/amd64 -f UBI/GDAL/Dockerfile \
	--build-arg ENABLE_ARROW=OFF \
	--build-arg ENABLE_NETCDF=OFF \
	--build-arg ENABLE_POSTGRESQL=OFF \
	--build-arg ENABLE_SFCGAL=OFF \
	-t ubi-gdal:lean .
```

Note: Parquet support follows ENABLE_ARROW in this Dockerfile.
Note: NetCDF support requires ENABLE_HDF5=ON.

Example: disable HDF5 (and NetCDF):

```bash
docker build --platform linux/amd64 -f UBI/GDAL/Dockerfile \
	--build-arg ENABLE_HDF5=OFF \
	--build-arg ENABLE_NETCDF=OFF \
	-t ubi-gdal:no-hdf5 .
```

Example: disable GEOS:

```bash
docker build --platform linux/amd64 -f UBI/GDAL/Dockerfile \
	--build-arg ENABLE_GEOS=OFF \
	-t ubi-gdal:no-geos .
```

## Verify Build

Check GDAL version:

```bash
docker run --rm ubi-gdal:full gdalinfo --version
```

List raster and vector drivers:

```bash
docker run --rm ubi-gdal:full gdalinfo --formats
docker run --rm ubi-gdal:full ogr2ogr --formats
```

## Troubleshooting

- If build fails after changing flags, retry with no cache:

```bash
docker build --no-cache --platform linux/amd64 -f UBI/GDAL/Dockerfile -t ubi-gdal:full .
```

- If Oracle download fails, set ENABLE_OCI=OFF and rebuild.
