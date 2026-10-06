# syntax=docker/dockerfile:1.7

ARG WOLFI_IMAGE=cgr.dev/usace-cwbi/chainguard-base-fips:20230214

# ==============================================================================
# Builder Stage
# ==============================================================================
FROM --platform=linux/amd64 ${WOLFI_IMAGE} AS builder

USER root

# Use a conservative default. Override with:
#   --build-arg BUILD_JOBS=12
ARG BUILD_JOBS=8

# Toggle external integrations at build time.
ARG ENABLE_OCI=ON
ARG ENABLE_TILEDB=ON
ARG ENABLE_SFCGAL=ON
ARG ENABLE_NETCDF=ON
ARG ENABLE_POSTGRESQL=ON
ARG ENABLE_ARROW=ON
ARG ENABLE_HDF5=ON
ARG ENABLE_GEOS=ON

# Component versions.
ARG ARROW_VERSION=16.1.0
ARG AWSSDK_VERSION=1.11.874
ARG BOOST_VERSION=1.91.0
ARG CGAL_VERSION=6.1.2
ARG DEFLATE_VERSION=1.25
ARG GDAL_VERSION=3.13.3
ARG GEOS_VERSION=3.14.1
ARG GEOTIFF_VERSION=1.7.4
ARG GIF_VERSION=5.2.2
ARG HDF5_VERSION=2.1.1
ARG KML_VERSION=1.3.0
ARG MAGIC_VERSION=5.46
ARG MINIZIP_VERSION=4.2.2
ARG NETCDF_VERSION=4.10.1
ARG NLOHMANN_JSON_VERSION=3.12.0
ARG OPENJPEG_VERSION=2.5.4
ARG ORACLE_VERSION=21.20.0.0.0
ARG POSTGRESQL_VERSION=18.4
ARG PROJ_VERSION=9.8.1
ARG SFCGAL_VERSION=2.2.0
ARG SPDLOG_VERSION=1.17.0
ARG TILEDB_VERSION=2.29.2
ARG URIPARSER_VERSION=1.0.2
ARG WEBP_VERSION=1.6.0
ARG ZSTD_VERSION=1.5.7

ENV BUILD=/buildtmp \
    PREFIX=/usr \
    ORACLE_BASE=/usr/lib/instantclient \
    ORACLE_HOME=/usr/lib/instantclient \
    LD_LIBRARY_PATH=/usr/lib/instantclient:/usr/lib \
    CCACHE_DIR=/root/.cache/ccache \
    CCACHE_COMPILERCHECK=content \
    CCACHE_MAXSIZE=10G \
    CMAKE_C_COMPILER_LAUNCHER=ccache \
    CMAKE_CXX_COMPILER_LAUNCHER=ccache

# Build dependencies.
RUN apk add --no-cache \
    autoconf \
    automake \
    bison \
    build-base \
    bzip2-dev \
    ccache \
    cmake \
    curl \
    curl-dev \
    diffutils \
    expat-dev \
    file \
    flex \
    git \
    glib-dev \
    gmp-dev \
    icu-dev \
    libaio-dev \
    libarchive-dev \
    libjpeg-turbo-dev \
    libpng-dev \
    libtool \
    libxml2-dev \
    linux-headers \
    lz4-dev \
    lz4-static \
    make \
    mpfr-dev \
    ninja-build \
    openjpeg-dev \
    openssl-4.0-dev \
    patch \
    pcre-dev \
    pcre2-dev \
    pkgconf \
    py3-numpy \
    py3-setuptools \
    python3-dev \
    sqlite \
    sqlite-dev \
    swig \
    thrift-dev \
    tiff-dev \
    unzip \
    utf8proc-dev \
    wget \
    xsimd-dev \
    xz-dev \
    zlib-dev \
    zstd-dev \
    zstd-static

# Ensure ccache is used by Makefile/autotools projects as well as CMake projects.
RUN mkdir -p /usr/local/lib/ccache \
    && ln -sf /usr/bin/ccache /usr/local/lib/ccache/cc \
    && ln -sf /usr/bin/ccache /usr/local/lib/ccache/c++ \
    && ln -sf /usr/bin/ccache /usr/local/lib/ccache/gcc \
    && ln -sf /usr/bin/ccache /usr/local/lib/ccache/g++ \
    && ln -sf /usr/bin/ccache /usr/local/lib/ccache/clang \
    && ln -sf /usr/bin/ccache /usr/local/lib/ccache/clang++ \
    && mkdir -p "${BUILD}" /build_thirdparty/usr/lib /build_proj/usr /build_gdal/usr

ENV PATH=/usr/local/lib/ccache:${PATH}

RUN if [ -f /usr/lib64/liblz4.a ] && [ ! -e /usr/lib/liblz4.a ]; then \
        ln -s /usr/lib64/liblz4.a /usr/lib/liblz4.a; \
    fi

WORKDIR ${BUILD}

# ==============================================================================
# JSON-C
# ==============================================================================
RUN --mount=type=cache,target=/root/.cache/ccache,id=gdal-ccache,sharing=locked \
    set -eux; \
    git clone --depth 1 https://github.com/json-c/json-c.git json-c; \
    cmake -S json-c -B json-c-build \
      -DDISABLE_WERROR=ON \
      -DCMAKE_BUILD_TYPE=Release \
      -DCMAKE_INSTALL_PREFIX=/usr; \
    cmake --build json-c-build --parallel "${BUILD_JOBS}"; \
    cmake --install json-c-build; \
    DESTDIR=/build_thirdparty cmake --install json-c-build; \
    mkdir -p /build_thirdparty/usr/lib; \
    cp -P /usr/lib/libjson-c*.so* /build_thirdparty/usr/lib; \
    rm -rf json-c json-c-build

# ==============================================================================
# libdeflate
# ==============================================================================
RUN --mount=type=cache,target=/root/.cache/ccache,id=gdal-ccache,sharing=locked \
    set -eux; \
    mkdir deflate; \
    wget -qO- "https://github.com/ebiggers/libdeflate/releases/download/v${DEFLATE_VERSION}/libdeflate-${DEFLATE_VERSION}.tar.gz" \
      | tar -xvz -C deflate --strip-components=1; \
    cmake -S deflate -B deflate/build \
      -DBUILD_SHARED_LIBS=ON \
      -DCMAKE_BUILD_TYPE=Release \
      -DCMAKE_INSTALL_PREFIX=/usr; \
    cmake --build deflate/build --parallel "${BUILD_JOBS}"; \
    cmake --install deflate/build; \
    DESTDIR=/build_thirdparty cmake --install deflate/build; \
    mkdir -p /build_thirdparty/usr/lib; \
    cp -P /usr/lib/libdeflate*.so* /build_thirdparty/usr/lib; \
    rm -rf deflate

# ==============================================================================
# Boost
# ==============================================================================
RUN --mount=type=cache,target=/root/.cache/ccache,id=gdal-ccache,sharing=locked \
    set -eux; \
    boost_v="$(echo "${BOOST_VERSION}" | tr '.' '_')"; \
    mkdir boost; \
    wget -qO- "https://archives.boost.io/release/${BOOST_VERSION}/source/boost_${boost_v}.tar.gz" \
      | tar -xvz -C boost --strip-components=1; \
    cd boost; \
    ./bootstrap.sh --prefix=/usr --libdir=/usr/lib; \
    ./b2 install \
      -j"${BUILD_JOBS}" \
      link=shared \
      cxxflags="-fPIC" \
      cflags="-fPIC"; \
    mkdir -p /build_thirdparty/usr/include /build_thirdparty/usr/lib; \
    cp -a /usr/include/boost /build_thirdparty/usr/include/; \
    cp -a /usr/lib/libboost_*.so* /build_thirdparty/usr/lib/; \
    rm -rf "${BUILD}/boost"

# ==============================================================================
# Minizip-NG
# ==============================================================================
RUN --mount=type=cache,target=/root/.cache/ccache,id=gdal-ccache,sharing=locked \
    set -eux; \
    mkdir minizip; \
    wget -q "https://github.com/zlib-ng/minizip-ng/archive/refs/tags/${MINIZIP_VERSION}.tar.gz" \
      -O minizip.tar.gz; \
    tar -xvzf minizip.tar.gz -C minizip --strip-components=1; \
    cmake -S minizip -B minizip/build \
      -DCMAKE_INSTALL_PREFIX=/usr \
      -DCMAKE_BUILD_TYPE=Release \
      -DBUILD_SHARED_LIBS=ON \
      -DCMAKE_POSITION_INDEPENDENT_CODE=ON; \
    cmake --build minizip/build --parallel "${BUILD_JOBS}"; \
    cmake --install minizip/build; \
    DESTDIR=/build_thirdparty cmake --install minizip/build; \
    mkdir -p /build_thirdparty/usr/lib; \
    cp -P /usr/lib/libminizip*.so* /build_thirdparty/usr/lib 2>/dev/null || true; \
    rm -rf minizip minizip.tar.gz

# ==============================================================================
# uriparser
# ==============================================================================
RUN --mount=type=cache,target=/root/.cache/ccache,id=gdal-ccache,sharing=locked \
    set -eux; \
    mkdir uri; \
    wget -q "https://github.com/uriparser/uriparser/releases/download/uriparser-${URIPARSER_VERSION}/uriparser-${URIPARSER_VERSION}.tar.gz" \
      -O uri.tar.gz; \
    tar -xvzf uri.tar.gz -C uri --strip-components=1; \
    cmake -S uri -B uri/build \
      -DCMAKE_BUILD_TYPE=Release \
      -DCMAKE_INSTALL_PREFIX=/usr \
      -DURIPARSER_BUILD_TESTS=OFF \
      -DURIPARSER_BUILD_DOCS=OFF; \
    cmake --build uri/build --parallel "${BUILD_JOBS}"; \
    cmake --install uri/build; \
    DESTDIR=/build_thirdparty cmake --install uri/build; \
    rm -rf uri uri.tar.gz

# ==============================================================================
# CGAL
# ==============================================================================
RUN --mount=type=cache,target=/root/.cache/ccache,id=gdal-ccache,sharing=locked \
    set -eux; \
    mkdir cgal; \
    wget -qO- "https://github.com/CGAL/cgal/releases/download/v${CGAL_VERSION}/CGAL-${CGAL_VERSION}.tar.xz" \
      | tar xvJ -C cgal --strip-components=1; \
    cmake -S cgal -B cgal/build \
      -DCMAKE_BUILD_TYPE=Release \
      -DCMAKE_INSTALL_PREFIX=/usr; \
    cmake --build cgal/build --parallel "${BUILD_JOBS}"; \
    cmake --install cgal/build; \
    DESTDIR=/build_thirdparty cmake --install cgal/build; \
    ldconfig /usr/lib; \
    rm -rf cgal

# ==============================================================================
# SFCGAL
# ==============================================================================
RUN --mount=type=cache,target=/root/.cache/ccache,id=gdal-ccache,sharing=locked \
    set -eux; \
    if [ "${ENABLE_SFCGAL}" = "ON" ]; then \
        mkdir sfcgal; \
        wget -qO- "https://gitlab.com/SFCGAL/SFCGAL/-/archive/v${SFCGAL_VERSION}/SFCGAL-v${SFCGAL_VERSION}.tar.gz" \
          | tar xvz -C sfcgal --strip-components=1; \
        sed -i 's/\bsystem\b//g' sfcgal/CMakeLists.txt; \
        cmake -S sfcgal -B sfcgal/build \
          -DCMAKE_BUILD_TYPE=Release \
          -DCMAKE_INSTALL_PREFIX=/usr; \
        cmake --build sfcgal/build --parallel "${BUILD_JOBS}"; \
        cmake --install sfcgal/build; \
        DESTDIR=/build_thirdparty cmake --install sfcgal/build; \
        rm -rf sfcgal; \
    else \
        echo "Skipping SFCGAL build (ENABLE_SFCGAL=${ENABLE_SFCGAL})"; \
    fi

# ==============================================================================
# libkml
# ==============================================================================
RUN --mount=type=cache,target=/root/.cache/ccache,id=gdal-ccache,sharing=locked \
    set -eux; \
    mkdir libkml; \
    wget -q "https://github.com/libkml/libkml/archive/refs/tags/${KML_VERSION}.tar.gz" \
      -O libkml.tar.gz; \
    tar -xvzf libkml.tar.gz -C libkml --strip-components=1; \
    sed -i '/#include "boost\/intrusive_ptr.hpp"/a\
namespace kmlbase {\
class Referent;\
void intrusive_ptr_add_ref(Referent*);\
void intrusive_ptr_release(Referent*);\
}' libkml/src/kml/dom/kml_ptr.h; \
    sed -i '/typedef boost::intrusive_ptr<Element> ElementPtr;/i\
template <typename T>\
inline void intrusive_ptr_add_ref(T* r) { kmlbase::intrusive_ptr_add_ref(reinterpret_cast<kmlbase::Referent*>(r)); }\
template <typename T>\
inline void intrusive_ptr_release(T* r) { kmlbase::intrusive_ptr_release(reinterpret_cast<kmlbase::Referent*>(r)); }\
' libkml/src/kml/dom/kml_ptr.h; \
    cmake -S libkml -B libkml/build \
      -DCMAKE_BUILD_TYPE=Release \
      -DCMAKE_INSTALL_PREFIX=/usr \
      -DCMAKE_POLICY_VERSION_MINIMUM=3.5; \
    cmake --build libkml/build --parallel "${BUILD_JOBS}"; \
    cmake --install libkml/build; \
    DESTDIR=/build_thirdparty cmake --install libkml/build; \
    rm -rf libkml libkml.tar.gz

# ==============================================================================
# HDF5
# ==============================================================================
RUN --mount=type=cache,target=/root/.cache/ccache,id=gdal-ccache,sharing=locked \
    set -eux; \
    if [ "${ENABLE_HDF5}" = "ON" ]; then \
        wget -q "https://github.com/HDFGroup/hdf5/releases/download/${HDF5_VERSION}/hdf5-${HDF5_VERSION}.tar.gz" \
          -O hdf5.tar.gz; \
        tar -xvzf hdf5.tar.gz; \
        cmake -S "hdf5-${HDF5_VERSION}" -B "hdf5-${HDF5_VERSION}/build" \
          -DCMAKE_INSTALL_PREFIX=/usr \
          -DCMAKE_BUILD_TYPE=Release \
          -DBUILD_SHARED_LIBS=ON \
          -DHDF5_BUILD_CPP_LIB=ON \
          -DHDF5_BUILD_HL_LIB=ON \
          -DHDF5_ENABLE_Z_LIB_SUPPORT=ON \
          -DHDF5_ENABLE_ZLIB_SUPPORT=ON \
          -DZLIB_INCLUDE_DIR=/usr/include \
          -DZLIB_LIBRARY_RELEASE=/usr/lib/libz.so \
          -DZLIB_LIBRARY=/usr/lib/libz.so; \
        cmake --build "hdf5-${HDF5_VERSION}/build" --parallel "${BUILD_JOBS}"; \
        cmake --install "hdf5-${HDF5_VERSION}/build"; \
        DESTDIR=/build_thirdparty cmake --install "hdf5-${HDF5_VERSION}/build"; \
        rm -rf "hdf5-${HDF5_VERSION}" hdf5.tar.gz; \
    else \
        echo "Skipping HDF5 build (ENABLE_HDF5=${ENABLE_HDF5})"; \
    fi

# ==============================================================================
# NetCDF-C
# ==============================================================================
RUN --mount=type=cache,target=/root/.cache/ccache,id=gdal-ccache,sharing=locked \
    set -eux; \
    if [ "${ENABLE_NETCDF}" = "ON" ]; then \
        mkdir netcdf; \
        wget -q "https://downloads.unidata.ucar.edu/netcdf-c/${NETCDF_VERSION}/netcdf-c-${NETCDF_VERSION}.tar.gz" \
          -O netcdf.tar.gz; \
        tar -xvzf netcdf.tar.gz -C netcdf --strip-components=1; \
        cmake -S netcdf -B netcdf/build \
          -DCMAKE_INSTALL_PREFIX=/usr \
          -DCMAKE_INSTALL_LIBDIR=lib \
          -DCMAKE_PREFIX_PATH=/usr \
          -DHDF5_DIR=/usr/lib/cmake/hdf5 \
          -DBUILD_SHARED_LIBS=ON \
          -DNETCDF_ENABLE_HDF5=ON \
          -DENABLE_DAP=OFF \
          -DENABLE_BYTERANGE=ON; \
        cmake --build netcdf/build --parallel "${BUILD_JOBS}"; \
        cmake --install netcdf/build; \
        DESTDIR=/build_thirdparty cmake --install netcdf/build; \
        mkdir -p /build_thirdparty/usr/lib/cmake/netCDF; \
        cp -r /usr/lib/cmake/netCDF/. /build_thirdparty/usr/lib/cmake/netCDF/ 2>/dev/null || true; \
        rm -rf netcdf netcdf.tar.gz; \
    else \
        echo "Skipping NetCDF build (ENABLE_NETCDF=${ENABLE_NETCDF})"; \
    fi

# ==============================================================================
# Oracle Instant Client
# ==============================================================================
RUN set -eux; \
    if [ "${ENABLE_OCI}" = "ON" ]; then \
        oracle_mjr="$(echo "${ORACLE_VERSION}" | tr -d '.')"; \
        mkdir oic; \
        cd oic; \
        curl -fL -o instantclient-basiclite.zip \
          "https://download.oracle.com/otn_software/linux/instantclient/${oracle_mjr}/instantclient-basic-linux.x64-${ORACLE_VERSION}dbru.zip"; \
        curl -fL -o instantclient-sdk.zip \
          "https://download.oracle.com/otn_software/linux/instantclient/${oracle_mjr}/instantclient-sdk-linux.x64-${ORACLE_VERSION}dbru.zip"; \
        curl -fL -o instantclient-sqlplus.zip \
          "https://download.oracle.com/otn_software/linux/instantclient/${oracle_mjr}/instantclient-sqlplus-linux.x64-${ORACLE_VERSION}dbru.zip"; \
        unzip instantclient-basiclite.zip; \
        unzip -o instantclient-sdk.zip; \
        unzip -o instantclient-sqlplus.zip; \
        mv instantclient*/ /usr/lib/instantclient; \
        echo '/usr/lib/instantclient' > /etc/ld.so.conf.d/oracle_instantclient.conf; \
        ldconfig /usr/lib; \
        mkdir -p /build_thirdparty/usr/lib/instantclient; \
        cp -Pa /usr/lib/instantclient/. /build_thirdparty/usr/lib/instantclient/; \
        cd "${BUILD}"; \
        rm -rf oic; \
    else \
        echo "Skipping Oracle Instant Client build (ENABLE_OCI=${ENABLE_OCI})"; \
    fi

# ==============================================================================
# PROJ datum grids
# ==============================================================================
RUN set -eux; \
    mkdir -p /build_projgrids/usr/share/proj; \
    curl -fL -o proj-datumgrid-latest.zip \
      http://download.osgeo.org/proj/proj-datumgrid-latest.zip; \
    unzip -q -j -u -o proj-datumgrid-latest.zip -d /build_projgrids/usr/share/proj; \
    rm -f proj-datumgrid-latest.zip

# ==============================================================================
# PROJ
# ==============================================================================
RUN --mount=type=cache,target=/root/.cache/ccache,id=gdal-ccache,sharing=locked \
    set -eux; \
    mkdir proj; \
    wget -qO- "https://github.com/OSGeo/PROJ/archive/${PROJ_VERSION}.tar.gz" \
      | tar xz -C proj --strip-components=1; \
    cmake -S proj -B proj/build \
      -DBUILD_SHARED_LIBS=ON \
      -DCMAKE_BUILD_TYPE=Release \
      -DCMAKE_INSTALL_PREFIX=/usr \
      -DENABLE_IPO=OFF \
      -DBUILD_TESTING=OFF; \
    cmake --build proj/build --parallel "${BUILD_JOBS}"; \
    cmake --install proj/build; \
    DESTDIR=/build_proj cmake --install proj/build; \
    rm -rf proj

# ==============================================================================
# GeoTIFF
# ==============================================================================
RUN --mount=type=cache,target=/root/.cache/ccache,id=gdal-ccache,sharing=locked \
    set -eux; \
    mkdir geotiff; \
    wget -q "https://download.osgeo.org/geotiff/libgeotiff/libgeotiff-${GEOTIFF_VERSION}.tar.gz" \
      -O geotiff.tar.gz; \
    tar -xvzf geotiff.tar.gz -C geotiff --strip-components=1; \
    cd geotiff; \
    ./configure \
      --prefix=/usr \
      --with-proj=/usr \
      --with-jpeg=/usr \
      --with-zip=yes; \
    make -j"${BUILD_JOBS}"; \
    make install; \
    make DESTDIR=/build_thirdparty install; \
    mkdir -p /build_thirdparty/usr/lib; \
    cp -P /usr/lib/libgeotiff*.so* /build_thirdparty/usr/lib; \
    cd "${BUILD}"; \
    rm -rf geotiff geotiff.tar.gz

# ==============================================================================
# GIFLIB
# ==============================================================================
RUN --mount=type=cache,target=/root/.cache/ccache,id=gdal-ccache,sharing=locked \
    set -eux; \
    mkdir giflib; \
    cd giflib; \
    wget -q "https://sourceforge.net/projects/giflib/files/giflib-${GIF_VERSION}.tar.gz/download" \
      -O giflib.tar.gz; \
    tar -xvzf giflib.tar.gz; \
    cd "giflib-${GIF_VERSION}"; \
    cp pic/gifgrid.gif doc/giflib-logo.gif; \
    make -j"${BUILD_JOBS}"; \
    make PREFIX=/usr install; \
    make PREFIX=/usr DESTDIR=/build_thirdparty install; \
    cd "${BUILD}"; \
    rm -rf giflib

# ==============================================================================
# GEOS
# ==============================================================================
RUN --mount=type=cache,target=/root/.cache/ccache,id=gdal-ccache,sharing=locked \
    set -eux; \
    if [ "${ENABLE_GEOS}" = "ON" ]; then \
        mkdir geos; \
        wget -qO- "https://download.osgeo.org/geos/geos-${GEOS_VERSION}.tar.bz2" \
          | tar -xvj -C geos --strip-components=1; \
        cmake -S geos -B geos/build \
          -DCMAKE_BUILD_TYPE=Release \
          -DCMAKE_INSTALL_PREFIX=/usr \
          -DBUILD_TESTING=OFF; \
        cmake --build geos/build --parallel "${BUILD_JOBS}"; \
        cmake --install geos/build; \
        DESTDIR=/build_thirdparty cmake --install geos/build; \
        rm -rf geos; \
    else \
        echo "Skipping GEOS build (ENABLE_GEOS=${ENABLE_GEOS})"; \
    fi

# ==============================================================================
# WebP
# ==============================================================================
RUN --mount=type=cache,target=/root/.cache/ccache,id=gdal-ccache,sharing=locked \
    set -eux; \
    mkdir webp; \
    wget -qO- "https://storage.googleapis.com/downloads.webmproject.org/releases/webp/libwebp-${WEBP_VERSION}.tar.gz" \
      | tar xz -C webp --strip-components=1; \
    cmake -S webp -B webp/build \
      -DCMAKE_BUILD_TYPE=Release \
      -DCMAKE_INSTALL_PREFIX=/usr \
      -DCMAKE_PREFIX_PATH=/usr \
      -DBUILD_SHARED_LIBS=ON; \
    cmake --build webp/build --parallel "${BUILD_JOBS}"; \
    cmake --install webp/build; \
    DESTDIR=/build_thirdparty cmake --install webp/build; \
    mkdir -p /build_thirdparty/usr/lib; \
    cp -P /usr/lib/libwebp*.so* /build_thirdparty/usr/lib 2>/dev/null || true; \
    cp -P /usr/lib/libsharpyuv*.so* /build_thirdparty/usr/lib 2>/dev/null || true; \
    rm -rf webp

# ==============================================================================
# libmagic
# ==============================================================================
RUN --mount=type=cache,target=/root/.cache/ccache,id=gdal-ccache,sharing=locked \
    set -eux; \
    mkdir magic; \
    wget -qO- "http://ftp.astron.com/pub/file/file-${MAGIC_VERSION}.tar.gz" \
      | tar xz -C magic --strip-components=1; \
    cd magic; \
    ./configure --prefix=/usr; \
    make -j"${BUILD_JOBS}"; \
    make install; \
    make DESTDIR=/build_thirdparty install; \
    cd "${BUILD}"; \
    rm -rf magic

# ==============================================================================
# fmt
# ==============================================================================
RUN --mount=type=cache,target=/root/.cache/ccache,id=gdal-ccache,sharing=locked \
    set -eux; \
    git clone --depth 1 --branch 11.0.2 https://github.com/fmtlib/fmt.git fmt; \
    cmake -S fmt -B fmt/build \
      -DCMAKE_INSTALL_PREFIX=/usr \
      -DCMAKE_INSTALL_LIBDIR=lib \
      -DBUILD_SHARED_LIBS=ON \
      -DCMAKE_POSITION_INDEPENDENT_CODE=ON; \
    cmake --build fmt/build --parallel "${BUILD_JOBS}"; \
    cmake --install fmt/build; \
    DESTDIR=/build_thirdparty cmake --install fmt/build; \
    rm -rf fmt

# ==============================================================================
# spdlog
# ==============================================================================
RUN --mount=type=cache,target=/root/.cache/ccache,id=gdal-ccache,sharing=locked \
    set -eux; \
    mkdir spdlog; \
    wget -qO- "https://github.com/gabime/spdlog/archive/refs/tags/v${SPDLOG_VERSION}.tar.gz" \
      | tar xz -C spdlog --strip-components=1; \
    cmake -S spdlog -B spdlog/build \
      -DCMAKE_INSTALL_PREFIX=/usr \
      -DCMAKE_INSTALL_LIBDIR=lib \
      -DCMAKE_POSITION_INDEPENDENT_CODE=ON \
      -DSPDLOG_INSTALL=ON \
      -DSPDLOG_BUILD_EXAMPLE=OFF \
      -DSPDLOG_BUILD_TESTS=OFF \
      -DSPDLOG_BUILD_BENCH=OFF \
      -DSPDLOG_FMT_EXTERNAL=ON \
      -DCMAKE_PREFIX_PATH=/usr; \
    cmake --build spdlog/build --parallel "${BUILD_JOBS}"; \
    cmake --install spdlog/build; \
    DESTDIR=/build_thirdparty cmake --install spdlog/build; \
    rm -rf spdlog

# ==============================================================================
# nlohmann-json
# ==============================================================================
RUN --mount=type=cache,target=/root/.cache/ccache,id=gdal-ccache,sharing=locked \
    set -eux; \
    mkdir nlohmann_json; \
    wget -qO- "https://github.com/nlohmann/json/archive/refs/tags/v${NLOHMANN_JSON_VERSION}.tar.gz" \
      | tar xvz -C nlohmann_json --strip-components=1; \
    cmake -S nlohmann_json -B nlohmann_json/build \
      -DCMAKE_INSTALL_PREFIX=/usr \
      -DCMAKE_INSTALL_LIBDIR=lib \
      -DJSON_BuildTests=OFF \
      -DJSON_Install=ON; \
    cmake --build nlohmann_json/build --parallel "${BUILD_JOBS}"; \
    cmake --install nlohmann_json/build; \
    DESTDIR=/build_thirdparty cmake --install nlohmann_json/build; \
    rm -rf nlohmann_json

# ==============================================================================
# AWS SDK for C++
# ==============================================================================
RUN --mount=type=cache,target=/root/.cache/ccache,id=gdal-ccache,sharing=locked \
    set -eux; \
    git clone --recurse-submodules --depth 1 \
      --branch "${AWSSDK_VERSION}" \
      https://github.com/aws/aws-sdk-cpp.git; \
    git -C aws-sdk-cpp/crt/aws-crt-cpp/crt/s2n fetch \
      --depth 1 \
      https://github.com/aws/s2n-tls.git \
      b170000016fb44fa4dfdd86ed0b75bd28241e707; \
    git -C aws-sdk-cpp/crt/aws-crt-cpp/crt/s2n checkout \
      --detach b170000016fb44fa4dfdd86ed0b75bd28241e707; \
    cmake -S aws-sdk-cpp -B aws-sdk-cpp/build \
      -DCMAKE_INSTALL_PREFIX=/usr \
      -DCMAKE_INSTALL_LIBDIR=lib \
      -DCMAKE_BUILD_TYPE=Release \
      -DCMAKE_POLICY_VERSION_MINIMUM=3.5 \
      -DBUILD_ONLY="s3;sts;identity-management" \
      -DENABLE_TESTING=OFF \
      -DENFORCE_SUBMODULE_VERSIONS=OFF \
      -DBUILD_SHARED_LIBS=ON \
      -DMINIMIZE_SIZE=ON; \
    cmake --build aws-sdk-cpp/build --parallel "${BUILD_JOBS}"; \
    cmake --install aws-sdk-cpp/build; \
    DESTDIR=/build_thirdparty cmake --install aws-sdk-cpp/build; \
    rm -rf aws-sdk-cpp

# ==============================================================================
# TileDB
# ==============================================================================
RUN --mount=type=cache,target=/root/.cache/ccache,id=gdal-ccache,sharing=locked \
    set -eux; \
    if [ "${ENABLE_TILEDB}" = "ON" ]; then \
        mkdir tiledb; \
        wget -qO- "https://github.com/TileDB-Inc/TileDB/archive/refs/tags/${TILEDB_VERSION}.tar.gz" \
          | tar xz -C tiledb --strip-components=1; \
        cmake -S tiledb -B tiledb/build_cmake \
          -DCMAKE_BUILD_TYPE=Release \
          -DCMAKE_INSTALL_PREFIX=/usr \
          -DCMAKE_DISABLE_FIND_PACKAGE_lz4=TRUE \
          -DTILEDB_S3=OFF \
          -DTILEDB_WERROR=OFF \
          -DTILEDB_DISABLE_AUTO_VCPKG=TRUE \
          -DTILEDB_TESTS=OFF \
          -DCOMPILER_SUPPORTS_AVX2=FALSE; \
        cmake --build tiledb/build_cmake --parallel "${BUILD_JOBS}"; \
        cmake --install tiledb/build_cmake; \
        DESTDIR=/build_thirdparty cmake --install tiledb/build_cmake; \
        find /build_thirdparty/usr/lib -type f -exec strip -s {} + 2>/dev/null || true; \
        find /build_thirdparty/usr/bin -type f -exec strip -s {} + 2>/dev/null || true; \
        rm -rf tiledb; \
    else \
        echo "Skipping TileDB build (ENABLE_TILEDB=${ENABLE_TILEDB})"; \
    fi

# Required by the PostgreSQL build in this image.
RUN mkdir -p /usr/local/share/perl5/5.32 \
    && cat > /usr/local/share/perl5/5.32/FindBin.pm <<'EOF'
package FindBin;
use strict;
use warnings;
use Exporter 'import';
our @EXPORT_OK = qw($Bin $Script $RealBin $RealScript);
our ($Bin, $Script, $RealBin, $RealScript);
BEGIN {
my $script = $0 // '';
$Script = $script;
$RealScript = $script;
if ($script =~ m{^(.*)/[^/]+$}) {
$Bin = $1;
$RealBin = $1;
} else {
$Bin = '.';
$RealBin = '.';
}
}
1;
EOF

# ==============================================================================
# PostgreSQL
# ==============================================================================
RUN --mount=type=cache,target=/root/.cache/ccache,id=gdal-ccache,sharing=locked \
    set -eux; \
    if [ "${ENABLE_POSTGRESQL}" = "ON" ]; then \
        mkdir postgresql; \
        wget -qO- "https://ftp.postgresql.org/pub/source/v${POSTGRESQL_VERSION}/postgresql-${POSTGRESQL_VERSION}.tar.gz" \
          | tar xvz -C postgresql --strip-components=1; \
        cd postgresql; \
        ./configure \
          --with-openssl \
          --without-readline \
          --prefix=/usr; \
        make -j"${BUILD_JOBS}"; \
        make install; \
        make DESTDIR=/build_thirdparty install; \
        ldconfig /usr/lib; \
        cd "${BUILD}"; \
        rm -rf postgresql; \
    else \
        echo "Skipping PostgreSQL build (ENABLE_POSTGRESQL=${ENABLE_POSTGRESQL})"; \
    fi

# ==============================================================================
# Apache Arrow
# ==============================================================================
RUN --mount=type=cache,target=/root/.cache/ccache,id=gdal-ccache,sharing=locked \
    set -eux; \
    if [ "${ENABLE_ARROW}" = "ON" ]; then \
        mkdir arrow; \
        wget -qO- "https://github.com/apache/arrow/archive/refs/tags/apache-arrow-${ARROW_VERSION}.tar.gz" \
          | tar xvz -C arrow --strip-components=1; \
        cd arrow/cpp; \
        sed -i 's@include(AWSSDKVariables)@include(${CMAKE_CURRENT_SOURCE_DIR}/cmake_modules/AWSSDKVariables.cmake)@' \
          cmake_modules/ThirdpartyToolchain.cmake; \
        sed -i 's@include(san-config)@include(${CMAKE_CURRENT_SOURCE_DIR}/cmake_modules/san-config.cmake)@' \
          CMakeLists.txt; \
        sed -i 's/resolve_dependency(lz4Alt/resolve_dependency(lz4/g' \
          cmake_modules/ThirdpartyToolchain.cmake; \
        sed -i '/set(EP_COMMON_CMAKE_ARGS/a\  list(APPEND EP_COMMON_CMAKE_ARGS "-DCMAKE_POLICY_VERSION_MINIMUM=3.5")' \
          cmake_modules/ThirdpartyToolchain.cmake; \
        cmake -S . -B build \
          -DCMAKE_INSTALL_PREFIX=/usr \
          -DCMAKE_INSTALL_LIBDIR=lib \
          -DCMAKE_POLICY_VERSION_MINIMUM=3.5 \
          -DCMAKE_MODULE_PATH="${BUILD}/arrow/cpp/cmake_modules" \
          -DCMAKE_BUILD_TYPE=Release \
          -DCMAKE_POSITION_INDEPENDENT_CODE=ON \
          -DARROW_DEPENDENCY_SOURCE=BUNDLED \
          -DThrift_SOURCE=SYSTEM \
          -Dlz4_SOURCE=SYSTEM \
          -Dlz4Alt_SOURCE=SYSTEM \
          -DZLIB_SOURCE=SYSTEM \
          -Dzstd_SOURCE=BUNDLED \
          -Dutf8proc_SOURCE=BUNDLED \
          -Dxsimd_SOURCE=SYSTEM \
          -DARROW_PARQUET=ON \
          -DARROW_FILESYSTEM=ON \
          -DARROW_DATASET=ON \
          -DARROW_COMPUTE=OFF \
          -DARROW_IPC=OFF \
          -DARROW_WITH_LZ4=OFF \
          -DARROW_WITH_ZLIB=ON \
          -DARROW_WITH_ZSTD=ON \
          -DARROW_BUILD_SHARED=ON \
          -DARROW_BUILD_STATIC=OFF \
          -DARROW_JEMALLOC=OFF \
          -DARROW_MIMALLOC=OFF \
          -DARROW_BUILD_TESTS=OFF; \
        cmake --build build --parallel "${BUILD_JOBS}"; \
        cmake --install build; \
        DESTDIR=/build_thirdparty cmake --install build; \
        cd "${BUILD}"; \
        rm -rf arrow; \
    else \
        echo "Skipping Arrow build (ENABLE_ARROW=${ENABLE_ARROW})"; \
    fi

RUN find /build_thirdparty/usr/lib -type f -exec strip -s {} + 2>/dev/null || true \
    && find /build_proj/usr/bin -type f -exec strip -s {} + 2>/dev/null || true

# ==============================================================================
# GDAL
# ==============================================================================
ARG GDAL_CACHE_BUST=0

RUN --mount=type=cache,target=/root/.cache/ccache,id=gdal-ccache,sharing=locked \
    set -eux; \
    echo "GDAL cache bust value: ${GDAL_CACHE_BUST}"; \
    mkdir gdal; \
    curl -fL --retry 5 --retry-delay 3 --retry-all-errors \
      --http1.1 --connect-timeout 20 --max-time 600 \
      "https://github.com/OSGeo/gdal/releases/download/v${GDAL_VERSION}/gdal-${GDAL_VERSION}.tar.gz" \
      -o "/tmp/gdal-${GDAL_VERSION}.tar.gz" \
    || curl -fL --retry 8 --retry-delay 3 --retry-all-errors \
      --http1.1 --connect-timeout 20 --max-time 600 \
      "https://codeload.github.com/OSGeo/gdal/tar.gz/refs/tags/v${GDAL_VERSION}" \
      -o "/tmp/gdal-${GDAL_VERSION}.tar.gz"; \
    tar xzf "/tmp/gdal-${GDAL_VERSION}.tar.gz" -C gdal --strip-components=1; \
    rm -f "/tmp/gdal-${GDAL_VERSION}.tar.gz"; \
    cmake -S gdal -B gdal/build \
      -DCMAKE_INSTALL_PREFIX=/usr \
      -DCMAKE_PREFIX_PATH="/usr:/build_thirdparty/usr" \
      -DCMAKE_BUILD_TYPE=Release \
      -DBUILD_PYTHON_BINDINGS=ON \
      -DBUILD_TESTING=OFF \
      -DGDAL_USE_ARCHIVE=OFF \
      -DGDAL_USE_ARMADILLO=OFF \
      -DGDAL_USE_ARROW=${ENABLE_ARROW} \
      -DGDAL_USE_BASISU=OFF \
      -DGDAL_USE_BLOSC=OFF \
      -DGDAL_USE_BRUNSLI=OFF \
      -DGDAL_USE_CFITSIO=OFF \
      -DGDAL_USE_CRNLIB=OFF \
      -DGDAL_USE_CURL=ON \
      -DGDAL_USE_CRYPTOPP=OFF \
      -DGDAL_USE_DEFLATE=ON \
      -DGDAL_USE_ECW=OFF \
      -DGDAL_USE_EXPAT=ON \
      -DGDAL_USE_FILEGDB=OFF \
      -DGDAL_USE_FREEXL=OFF \
      -DGDAL_USE_FYBA=OFF \
      -DGDAL_USE_GEOTIFF=ON \
      -DGDAL_USE_GEOTIFF_INTERNAL=OFF \
      -DGDAL_USE_GEOS=${ENABLE_GEOS} \
      -DGDAL_USE_GIF=ON \
      -DGDAL_USE_GIF_INTERNAL=OFF \
      -DGDAL_USE_GTA=OFF \
      -DGDAL_USE_HEIF=OFF \
      -DGDAL_USE_HDF4=OFF \
      -DGDAL_USE_HDF5=${ENABLE_HDF5} \
      -DGDAL_USE_HDFS=OFF \
      -DGDAL_USE_ICONV=ON \
      -DGDAL_USE_IDB=OFF \
      -DGDAL_USE_JPEG_INTERNAL=OFF \
      -DGDAL_USE_JPEG=ON \
      -DGDAL_USE_JPEG12_INTERNAL=OFF \
      -DGDAL_USE_JSONC=ON \
      -DGDAL_USE_JSONC_INTERNAL=OFF \
      -DGDAL_USE_JXL=OFF \
      -DGDAL_USE_KDU=OFF \
      -DGDAL_USE_KEA=OFF \
      -DGDAL_USE_LERC=OFF \
      -DGDAL_USE_LERC_INTERNAL=ON \
      -DGDAL_USE_LIBAEC=OFF \
      -DGDAL_USE_LIBKML=ON \
      -DGDAL_USE_LIBLZMA=ON \
      -DGDAL_USE_LIBQB3=OFF \
      -DGDAL_USE_LIBXML2=ON \
      -DGDAL_USE_LIBLZ4=ON \
      -DGDAL_USE_LURATECH=OFF \
      -DGDAL_USE_LZ4=ON \
      -DGDAL_USE_MONGOCXX=OFF \
      -DGDAL_USE_MRSID=OFF \
      -DGDAL_USE_MSSQL_NCLI=OFF \
      -DGDAL_USE_MSSQL_ODBC=OFF \
      -DGDAL_USE_MYSQL=OFF \
      -DGDAL_USE_NETCDF=${ENABLE_NETCDF} \
      -DNetCDF_ROOT=/usr \
      -DGDAL_USE_ODBC=OFF \
      -DGDAL_USE_ODBCCPP=OFF \
      -DGDAL_USE_OGDI=OFF \
      -DGDAL_USE_OPENCAD=OFF \
      -DGDAL_USE_OPENCAD_INTERNAL=OFF \
      -DGDAL_USE_OPENCL=OFF \
      -DGDAL_USE_OPENEXR=OFF \
      -DGDAL_USE_OPENJPEG=ON \
      -DGDAL_USE_OPENSSL=ON \
      -DOracle_ROOT=/usr/lib/instantclient \
      -DGDAL_USE_ORACLE=${ENABLE_OCI} \
      -DGDAL_USE_PARQUET=${ENABLE_ARROW} \
      -DGDAL_USE_PCRE2=ON \
      -DGDAL_USE_PDFIUM=OFF \
      -DGDAL_USE_PNG=ON \
      -DGDAL_USE_PNG_INTERNAL=OFF \
      -DGDAL_USE_POPPLER=OFF \
      -DGDAL_USE_POSTGRESQL=${ENABLE_POSTGRESQL} \
      -DGDAL_USE_QHULL=OFF \
      -DGDAL_USE_QHULL_INTERNAL=OFF \
      -DGDAL_USE_RASTERLITE2=OFF \
      -DGDAL_USE_RDB=OFF \
      -DGDAL_USE_SPATIALITE=OFF \
      -DGDAL_USE_SFCGAL=${ENABLE_SFCGAL} \
      -DGDAL_USE_SQLITE3=ON \
      -DGDAL_USE_TILEDB=${ENABLE_TILEDB} \
      -DGDAL_USE_WEBP=ON \
      -DGDAL_USE_ZLIB=ON \
      -DGDAL_USE_ZSTD=ON; \
    cmake --build gdal/build --parallel "${BUILD_JOBS}"; \
    cmake --install gdal/build; \
    DESTDIR=/build_gdal cmake --install gdal/build; \
    rm -rf gdal

RUN find /build_gdal/usr/lib -type f -name '*.so*' -exec strip -s {} + 2>/dev/null || true \
    && find /build_gdal/usr/bin -type f -exec strip -s {} + 2>/dev/null || true

# Normalize library staging layout for runtime copy.
RUN set -eux; \
    for root in /build_thirdparty/usr /build_proj/usr /build_gdal/usr; do \
        if [ -d "${root}/lib64" ]; then \
            mkdir -p "${root}/lib"; \
            cp -a "${root}/lib64/." "${root}/lib/"; \
            rm -rf "${root}/lib64"; \
        fi; \
    done

# ==============================================================================
# Runtime Stage
# ==============================================================================
FROM --platform=linux/amd64 ${WOLFI_IMAGE} AS runtime

ARG ENABLE_OCI=ON

RUN apk add --no-cache \
    bzip2 \
    curl \
    expat \
    glib \
    gmp \
    icu \
    libaio \
    libgomp \
    libjpeg-turbo \
    liblz4-1 \
    libpng \
    libstdc++ \
    libthrift \
    libxml2 \
    libxml2-16 \
    libzstd1 \
    lz4 \
    mpfr \
    openjpeg \
    openssl \
    pcre2 \
    py3-numpy \
    python3 \
    sqlite \
    tiff \
    tzdata \
    xz \
    zlib

COPY --from=builder /build_thirdparty/usr /usr
COPY --from=builder /build_proj/usr /usr
COPY --from=builder /build_projgrids/usr/share/proj /usr/share/proj
COPY --from=builder /build_gdal/usr /usr

ENV PREFIX=/usr \
    PROJ_LIB=/usr/share/proj \
    GDAL_DATA=/usr/share/gdal \
    ORACLE_BASE=/usr/lib/instantclient \
    ORACLE_HOME=/usr/lib/instantclient \
    LD_LIBRARY_PATH=/usr/lib:/usr/lib/instantclient

RUN set -eux; \
    if [ "${ENABLE_OCI}" = "ON" ]; then \
        echo '/usr/lib/instantclient' > /etc/ld.so.conf.d/oracle_instantclient.conf; \
    fi; \
    ldconfig /usr/lib 2>/dev/null || true

RUN gdalinfo --version \
    && projinfo EPSG:4326 > /dev/null \
    && python3 -c 'from osgeo import gdal, ogr, osr; print("GDAL_PYTHON_VERSION=" + gdal.VersionInfo("--version")); print("OGR_DRIVER_COUNT=" + str(ogr.GetDriverCount())); print("OSR_CLASS=" + osr.SpatialReference().__class__.__name__)'

CMD ["gdalinfo", "--version"]