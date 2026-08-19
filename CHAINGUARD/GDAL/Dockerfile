    # Start from Chainguard Wolfi as the base image
ARG platform=linux/amd64
FROM --platform=${platform} cgr.dev/chainguard/wolfi-base AS builder

# Toggle selected external integrations at build time (ON/OFF)
ARG ENABLE_OCI=ON
ARG ENABLE_TILEDB=ON
ARG ENABLE_SFCGAL=ON
ARG ENABLE_NETCDF=ON
ARG ENABLE_POSTGRESQL=ON
ARG ENABLE_ARROW=ON
ARG ENABLE_HDF5=ON
ARG ENABLE_GEOS=ON

# LATEST GDAL is 3.9.2 but postgis won't build
ENV \
    ARROW_VERSION=16.1.0 \
    AWSSDK_VERSION=1.11.350 \
    BOOST_VERSION=1.91.0 \
    CGAL_VERSION=6.1.1 \
    DEFLATE_VERSION=1.25 \
    GDAL_VERSION=3.13.3 \
    GEOS_VERSION=3.14.0 \
    GEOTIFF_VERSION=1.7.4 \
    GIF_VERSION=5.2.2 \
    HDF5_VERSION=2.1.1 \
    KML_VERSION=1.3.0 \
    MAGIC_VERSION=5.46 \
    MINIZIP_VERSION=4.2.1 \
    NETCDF_VERSION=4.10.0 \
    NLOHMANN_JSON_VERSION=3.12.0 \
    OPENJPEG_VERSION=2.5.4 \
    ORACLE_VERSION=21.20.0.0.0 \
    POSTGRESQL_VERSION=18.4 \
    PROJ_VERSION=9.8.1 \
    SFCGAL_VERSION=2.2.0 \
    SPDLOG_VERSION=1.17.0 \
    TILEDB_VERSION=2.29.2 \
    URIPARSER_VERSION=1.0.2 \
    WEBP_VERSION=1.6.0 \
    ZLIB_VERSION=1.3.1 \
    ZSTD_VERSION=1.5.6

# Paths to things
ENV \
    BUILD=/buildtmp \
    PREFIX=/usr \
    ORACLE_BASE=/usr/lib/instantclient \
    LD_LIBRARY_PATH=/usr/lib/instantclient:/usr/lib \
    ORACLE_HOME=/usr/lib/instantclient

# Install dependencies for building PROJ and GDAL via apk
RUN apk update && apk add --no-cache \
    wget \
    curl \
    unzip \
    make \
    libtool \
    autoconf \
    automake \
    pkgconf \
    ninja \
    build-base \
    sqlite \
    sqlite-dev \
    linux-headers \
    libarchive-dev \
    curl-dev \
    tiff-dev \
    zlib-dev \
    lz4-dev \
    lz4-static \
    libjpeg-turbo-dev \
    libpng-dev \
    libxml2-dev \
    expat-dev \
    python3-dev \
    py3-setuptools \
    py3-numpy \
    pcre-dev \
    pcre2-dev \
    libaio-dev \
    cmake \
    git \
    patch \
    diffutils \
    file \
    glib-dev \
    bzip2-dev \
    icu-dev \
    gmp-dev \
    mpfr-dev \
    xz-dev \
    openssl-dev \
    swig \
    thrift-dev \
    utf8proc-dev \
    xsimd-dev \
    zstd-static

RUN if [ -f /usr/lib64/liblz4.a ] && [ ! -e /usr/lib/liblz4.a ]; then \
        ln -s /usr/lib64/liblz4.a /usr/lib/liblz4.a; \
    fi


RUN mkdir -p /buildtmp /build_thirdparty/usr/lib

# switch to a build directory
WORKDIR /buildtmp

# JSON-C
RUN cd ${BUILD} && \
    git clone https://github.com/json-c/json-c.git && \
    mkdir json-c-build && \
    cd json-c-build && \
    cmake -DDISABLE_WERROR=ON -DCMAKE_INSTALL_PREFIX=/usr ../json-c &&\
    make && \
    make install && \
    make DESTDIR="/build_thirdparty" install && \
    mkdir -p /build_thirdparty/usr/lib && \
    cp -P /usr/lib/libjson-c*.so* /build_thirdparty/usr/lib && \
    cd ${BUILD} && \
    rm -rf json-c

# ZSTD
RUN cd ${BUILD} && \
    mkdir zstd && \
    wget -qO- https://github.com/facebook/zstd/releases/download/v${ZSTD_VERSION}/zstd-${ZSTD_VERSION}.tar.gz | tar -xvz -C zstd --strip-components=1 && \
    cd zstd/build/cmake  \
    && cmake . -DBUILD_SHARED_LIBS=ON -DCMAKE_BUILD_TYPE=Release \
    -DCMAKE_INSTALL_PREFIX=/usr \
    && make -j$(nproc) && \
    make install && \
    make DESTDIR="/build_thirdparty" install && \
    mkdir -p /build_thirdparty/usr/lib && \
    cp -P /usr/lib/libzstd*.so* /build_thirdparty/usr/lib && \
    cd ${BUILD} && \
    rm -rf zstd

# DEFLATE
RUN cd ${BUILD} && \
    mkdir deflate && \
    wget -qO- https://github.com/ebiggers/libdeflate/releases/download/v${DEFLATE_VERSION}/libdeflate-${DEFLATE_VERSION}.tar.gz | tar -xvz -C deflate --strip-components=1 && \
    cd deflate  && \
    mkdir build && \
    cd build && \
    cmake .. -DBUILD_SHARED_LIBS=ON -DCMAKE_BUILD_TYPE=Release \
    -DCMAKE_INSTALL_PREFIX=/usr \
    && make -j$(nproc) && \
    make install && \
    make DESTDIR="/build_thirdparty" install && \
    mkdir -p /build_thirdparty/usr/lib && \
    cp -P /usr/lib/libdeflate*.so* /build_thirdparty/usr/lib && \
    cd ${BUILD} && \
    rm -rf deflate

# BOOST
ARG BoostV
RUN cd ${BUILD}  && \
    mkdir boost && \
    BoostV=$(echo "$BOOST_VERSION" | tr '.' '_') && \
    wget -qO- https://archives.boost.io/release/${BOOST_VERSION}/source/boost_${BoostV}.tar.gz | tar -xvz -C boost --strip-components=1 && \
    cd boost && \
    ./bootstrap.sh --prefix=${PREFIX} --libdir=/usr/lib && \
    ./b2 install -j$(nproc) link=shared cxxflags="-fPIC" cflags="-fPIC" && \
    ./bootstrap.sh --prefix="/build_thirdparty/usr" --libdir="/build_thirdparty/usr/lib" && \
    ./b2 install -j$(nproc) link=shared cxxflags="-fPIC" cflags="-fPIC" && \
    cd ${BUILD} && \
    rm -rf boost

# Minizip-NG
RUN cd ${BUILD} && \
    mkdir minizip && \
    wget https://github.com/zlib-ng/minizip-ng/archive/refs/tags/${MINIZIP_VERSION}.tar.gz -O minizip.tar.gz && \
    tar -xvzf minizip.tar.gz -C minizip --strip-components=1 && \
    cd minizip && \
    mkdir build && \
    cmake -S . -B build \
    -DCMAKE_INSTALL_PREFIX=/usr \
    -DCMAKE_BUILD_TYPE=Release \
    -DBUILD_SHARED_LIBS=ON \
    -DCMAKE_POSITION_INDEPENDENT_CODE=ON && \
    cmake --build build && \
    cd build && \
    make -j$(nproc) && \
    make install && \
    make DESTDIR="/build_thirdparty" install && \
    mkdir -p /build_thirdparty/usr/lib && \
    cp -P /usr/lib/libminizip*.so* /build_thirdparty/usr/lib 2>/dev/null || true && \
    cd ${BUILD} && \
    rm -rf minizip minizip.tar.gz

# URIParser for kml 
RUN cd ${BUILD} && \
    mkdir uri && \
    wget https://github.com/uriparser/uriparser/releases/download/uriparser-${URIPARSER_VERSION}/uriparser-${URIPARSER_VERSION}.tar.gz -O uri.tar.gz && \
    tar -xvzf uri.tar.gz  -C uri --strip-components=1 && \
    cd uri && \
    mkdir build && \
    cd build && \
    cmake .. -DCMAKE_BUILD_TYPE=Release -DCMAKE_INSTALL_PREFIX=/usr -DURIPARSER_BUILD_TESTS=OFF -DURIPARSER_BUILD_DOCS=OFF && \
    make -j$(nproc) && \
    make install && \
    make DESTDIR="/build_thirdparty" install && \
    cd ${BUILD} && \
    rm -rf uri

# CGAL
RUN cd ${BUILD} && \
    mkdir cgal && \
    wget -qO- https://github.com/CGAL/cgal/releases/download/v${CGAL_VERSION}/CGAL-${CGAL_VERSION}.tar.xz \
    | tar xvJ -C cgal --strip-components=1 && \
    cd cgal && \
    cmake . -DCMAKE_INSTALL_PREFIX=${PREFIX} && \
    make install && \
    make DESTDIR="/build_thirdparty" install && \
    ldconfig /usr/lib && \
    cd ${BUILD} && \
    rm -rf cgal

# SFCGAL
RUN if [ "${ENABLE_SFCGAL}" = "ON" ]; then \
        cd ${BUILD} && \
        mkdir sfcgal && \
        wget -qO- https://gitlab.com/SFCGAL/SFCGAL/-/archive/v${SFCGAL_VERSION}/SFCGAL-v${SFCGAL_VERSION}.tar.gz \
        | tar xvz -C sfcgal --strip-components=1 && \
        cd sfcgal && \
        sed -i 's/\bsystem\b//g' CMakeLists.txt && \
        cmake -S . -DCMAKE_INSTALL_PREFIX=${PREFIX} -B build && \
        cmake --build build && \
        cmake --install build && \
        cd build && \
        make DESTDIR="/build_thirdparty" install && \
        cd ${BUILD} && \
        rm -rf sfcgal; \
    else \
        echo "Skipping SFCGAL build (ENABLE_SFCGAL=${ENABLE_SFCGAL})"; \
    fi

# KML
RUN cd ${BUILD} && \
    mkdir libkml && \
    wget https://github.com/libkml/libkml/archive/refs/tags/${KML_VERSION}.tar.gz -O libkml.tar.gz && \
    tar -xvzf libkml.tar.gz -C libkml --strip-components=1 && \
    cd libkml  && \
    sed -i '/#include "boost\/intrusive_ptr.hpp"/a\
namespace kmlbase {\
class Referent;\
void intrusive_ptr_add_ref(Referent*);\
void intrusive_ptr_release(Referent*);\
}\
' src/kml/dom/kml_ptr.h && \
    sed -i '/typedef boost::intrusive_ptr<Element> ElementPtr;/i\
template <typename T>\
inline void intrusive_ptr_add_ref(T* r) { kmlbase::intrusive_ptr_add_ref(reinterpret_cast<kmlbase::Referent*>(r)); }\
template <typename T>\
inline void intrusive_ptr_release(T* r) { kmlbase::intrusive_ptr_release(reinterpret_cast<kmlbase::Referent*>(r)); }\
' src/kml/dom/kml_ptr.h && \
    mkdir build && \
    cd build && \
    cmake .. -DCMAKE_BUILD_TYPE=Release -DCMAKE_INSTALL_PREFIX=${PREFIX} -DCMAKE_POLICY_VERSION_MINIMUM=3.5 && \
    make -j$(nproc) && \
    make install && \
    make DESTDIR="/build_thirdparty" install && \
    cd ${BUILD} && \
    rm -rf libkml

# HDF5
RUN if [ "${ENABLE_HDF5}" = "ON" ]; then \
        cd ${BUILD} && \
        wget https://github.com/HDFGroup/hdf5/releases/download/${HDF5_VERSION}/hdf5-${HDF5_VERSION}.tar.gz -O hdf5.tar.gz && \
        tar -xvzf hdf5.tar.gz && \
        cd hdf5-${HDF5_VERSION} && \
        mkdir build && \
        cmake -S . -B build \
        -DCMAKE_INSTALL_PREFIX=${PREFIX} \
        -DCMAKE_BUILD_TYPE=Release \
        -DBUILD_SHARED_LIBS=ON \
        -DHDF5_BUILD_CPP_LIB=ON \
        -DHDF5_BUILD_HL_LIB=ON \
        -DHDF5_ENABLE_Z_LIB_SUPPORT=ON \
        -DHDF5_ENABLE_ZLIB_SUPPORT=ON \
        -DZLIB_INCLUDE_DIR=/usr/include \
        -DZLIB_LIBRARY_RELEASE=/usr/lib/libz.so \
        -DZLIB_LIBRARY=/usr/lib/libz.so \
        && cmake --build build -j$(nproc) && \
        cmake --install build && \
        cmake --install build --prefix="/build_thirdparty/usr" && \
        cd ${BUILD} && \
        rm -rf hdf5-${HDF5_VERSION} hdf5.tar.gz; \
    else \
        echo "Skipping HDF5 build (ENABLE_HDF5=${ENABLE_HDF5})"; \
    fi

# NetCDF-C
RUN if [ "${ENABLE_NETCDF}" = "ON" ]; then \
        cd ${BUILD} && \
        mkdir netcdf && \
        wget https://downloads.unidata.ucar.edu/netcdf-c/${NETCDF_VERSION}/netcdf-c-${NETCDF_VERSION}.tar.gz -O netcdf.tar.gz && \
        tar -xvzf netcdf.tar.gz  -C netcdf --strip-components=1 && \
        cd netcdf && \
        mkdir build && \
        cd build && \
        cmake .. \
        -DCMAKE_INSTALL_PREFIX=${PREFIX} \
        -DCMAKE_INSTALL_LIBDIR=lib \
        -DCMAKE_PREFIX_PATH=${PREFIX} \
        -DHDF5_DIR=${PREFIX}/lib/cmake/hdf5 \
        -DBUILD_SHARED_LIBS=ON \
        -DNETCDF_ENABLE_HDF5=ON \
        -DENABLE_DAP=OFF \
        -DENABLE_BYTERANGE=ON \
        && make -j$(nproc) && \
        make install && \
        make DESTDIR="/build_thirdparty" install && \
        mkdir -p /build_thirdparty/usr/lib/cmake/netCDF && \
        cp -r ${PREFIX}/lib/cmake/netCDF/* /build_thirdparty/usr/lib/cmake/netCDF/ 2>/dev/null || true && \
        cd ${BUILD} && \
        rm -rf netcdf netcdf.tar.gz; \
    else \
        echo "Skipping NetCDF build (ENABLE_NETCDF=${ENABLE_NETCDF})"; \
    fi

# Install Oracle Instant Client
ARG OracleMJR
RUN if [ "${ENABLE_OCI}" = "ON" ]; then \
        cd ${BUILD} && \
        mkdir oic && \
        OracleMJR=$(echo "$ORACLE_VERSION" | tr -d '.') && \
        curl -o instantclient-basiclite.zip https://download.oracle.com/otn_software/linux/instantclient/$OracleMJR/instantclient-basic-linux.x64-${ORACLE_VERSION}dbru.zip -SL && \
        unzip instantclient-basiclite.zip && \
        curl -o instantclient-sdk.zip https://download.oracle.com/otn_software/linux/instantclient/$OracleMJR/instantclient-sdk-linux.x64-${ORACLE_VERSION}dbru.zip -SL && \
        unzip -o instantclient-sdk.zip && \
        curl -o instantclient-sqlplus.zip https://download.oracle.com/otn_software/linux/instantclient/$OracleMJR/instantclient-sqlplus-linux.x64-${ORACLE_VERSION}dbru.zip -SL && \
        unzip -o instantclient-sqlplus.zip && \
        mv instantclient*/ ${PREFIX}/lib/instantclient && \
        rm instantclient-basiclite.zip && \
        rm instantclient-sdk.zip && \
        rm instantclient-sqlplus.zip && \
        echo '/usr/lib/instantclient' | tee -a /etc/ld.so.conf.d/oracle_instantclient.conf && \
        ldconfig /usr/lib && \
        mkdir -p /build_thirdparty/usr/lib && \
        cp -Pa ${PREFIX}/lib/instantclient/. /build_thirdparty/usr/lib/instantclient; \
    else \
        echo "Skipping Oracle Instant Client build (ENABLE_OCI=${ENABLE_OCI})"; \
    fi

# OpenJPEG
RUN cd ${BUILD} && \
    mkdir openjpeg && \
    wget -q https://github.com/uclouvain/openjpeg/archive/v${OPENJPEG_VERSION}.tar.gz -O openjpeg.tar.gz && \
    tar -xvzf openjpeg.tar.gz  -C openjpeg --strip-components=1 && \
    cd openjpeg && \
    cmake . -DBUILD_SHARED_LIBS=ON -DBUILD_STATIC_LIBS=OFF -DCMAKE_BUILD_TYPE=Release \
    -DCMAKE_INSTALL_PREFIX=${PREFIX} \
    && make -j$(nproc)  && \
    make install && \
    make install DESTDIR="/build_thirdparty" \
    && mkdir -p /build_thirdparty/usr/lib \
    && cd ${BUILD} \
    && rm -rf openjpeg

# Build and install PROJ
ARG PROJ_DATUMGRID_LATEST_LAST_MODIFIED
RUN mkdir -p /build_projgrids/usr/share/proj \
    && curl -LOs http://download.osgeo.org/proj/proj-datumgrid-latest.zip \
    && unzip -q -j -u -o proj-datumgrid-latest.zip -d /build_projgrids/usr/share/proj \
    && rm -f *.zip

RUN cd ${BUILD} \
    && mkdir proj \
    && wget -q https://github.com/OSGeo/PROJ/archive/${PROJ_VERSION}.tar.gz -O - \
    | tar xz -C proj --strip-components=1 \
    && cd proj \
    && cmake . \
    -DBUILD_SHARED_LIBS=ON \
    -DCMAKE_BUILD_TYPE=Release \
    -DCMAKE_INSTALL_PREFIX=${PREFIX} \
    -DENABLE_IPO=OFF \
    -DBUILD_TESTING=OFF \
    && make -j$(nproc) \
    && make install \
    && make install DESTDIR="/build_proj" \
    && cd .. \
    && rm -rf proj

# GeoTiff
RUN cd ${BUILD} && \
    mkdir geotiff && \
    wget https://download.osgeo.org/geotiff/libgeotiff/libgeotiff-${GEOTIFF_VERSION}.tar.gz -O geotiff.tar.gz && \
    tar -xvzf geotiff.tar.gz  -C geotiff --strip-components=1 && \
    cd geotiff && \
    ./configure --prefix=${PREFIX} \
    --with-proj=${PREFIX} --with-jpeg=${PREFIX} --with-zip=yes && \
    make -j ${NPROC} && \
    make install && \
    make DESTDIR="/build_thirdparty" install && \
    mkdir -p /build_thirdparty/usr/lib && \
    cp -P /usr/lib/libgeotiff*.so* /build_thirdparty/usr/lib && \
    cd ${BUILD} && \
    rm -rf geotiff

# GIF
RUN cd ${BUILD} && \
    mkdir giflib && \
    cd giflib && \
    wget https://sourceforge.net/projects/giflib/files/giflib-${GIF_VERSION}.tar.gz/download -O giflib.tar.gz && \
    tar -xvzf giflib.tar.gz && \
    cd giflib-${GIF_VERSION} && \
    cp pic/gifgrid.gif doc/giflib-logo.gif && \
    make -j$(nproc) && \
    make PREFIX=${PREFIX} install && \
    make PREFIX=${PREFIX} DESTDIR="/build_thirdparty" install && \
    cd ${BUILD} && \
    rm -rf giflib

# GEOS
RUN if [ "${ENABLE_GEOS}" = "ON" ]; then \
        cd ${BUILD} && \
        mkdir geos && \
        wget -qO- https://download.osgeo.org/geos/geos-${GEOS_VERSION}.tar.bz2 | tar -xvj -C geos --strip-components=1 && \
        cd geos && \
        cmake . \
        -DCMAKE_BUILD_TYPE=Release \
        -DCMAKE_INSTALL_PREFIX=${PREFIX} \
        -DBUILD_TESTING=OFF && \
        make install && \
        make DESTDIR="/build_thirdparty" install && \
        cd ${BUILD} && \
        rm -rf geos; \
    else \
        echo "Skipping GEOS build (ENABLE_GEOS=${ENABLE_GEOS})"; \
    fi

# WEbP
RUN cd ${BUILD} && \
    mkdir webp && \
    wget -q https://storage.googleapis.com/downloads.webmproject.org/releases/webp/libwebp-${WEBP_VERSION}.tar.gz -O - \
    | tar xz -C webp --strip-components=1 && \
    cd webp  && \
    mkdir build && \
    cd build && \
    cmake .. \
    -DCMAKE_BUILD_TYPE=Release \
    -DCMAKE_INSTALL_PREFIX=${PREFIX} \
    -DCMAKE_PREFIX_PATH=${PREFIX} \
    -DBUILD_SHARED_LIBS=ON \
    && make -j$(nproc) && \
    make install && \
    make DESTDIR="/build_thirdparty" install && \
    mkdir -p /build_thirdparty/usr/lib && \
    cp -P ${PREFIX}/lib/libwebp*.so* /build_thirdparty/usr/lib 2>/dev/null || true && \
    cp -P ${PREFIX}/lib/libsharpyuv*.so* /build_thirdparty/usr/lib 2>/dev/null || true && \
    cd ${BUILD} && \
    rm -rf webp

# LibMAGIC
RUN cd ${BUILD} && \
    mkdir magic && \
    wget -q http://ftp.astron.com/pub/file/file-${MAGIC_VERSION}.tar.gz -O - \
    | tar xz -C magic --strip-components=1 && \
    cd magic && \
    mkdir build && \
    cd build && \
    ../configure --prefix=${PREFIX} && \
    make && \
    make install && \
    make DESTDIR="/build_thirdparty" install && \
    cd ${BUILD} && \
    rm -rf magic

# fmt
RUN cd ${BUILD} && \
    git clone --depth 1 -b 11.0.2 https://github.com/fmtlib/fmt.git && \
    cd fmt && \
    mkdir build && \
    cd build && \
    cmake .. \
    -DCMAKE_INSTALL_PREFIX=${PREFIX} \
    -DCMAKE_INSTALL_LIBDIR=lib \
    -DBUILD_SHARED_LIBS=ON \
    -DCMAKE_POSITION_INDEPENDENT_CODE=ON && \
    make -j$(nproc) && \
    make install && \
    make DESTDIR="/build_thirdparty" install && \
    cd ${BUILD} && \
    rm -rf fmt

# spdlog
RUN cd ${BUILD} && \
    mkdir spdlog && \
    wget -q https://github.com/gabime/spdlog/archive/refs/tags/v${SPDLOG_VERSION}.tar.gz -O - \
    | tar xz -C spdlog --strip-components=1 && \
    cd spdlog && \
    mkdir build && \
    cd build && \
    cmake .. \
    -DCMAKE_INSTALL_PREFIX=${PREFIX} \
    -DCMAKE_INSTALL_LIBDIR=lib \
    -DCMAKE_POSITION_INDEPENDENT_CODE=ON \
    -DSPDLOG_INSTALL=ON \
    -DSPDLOG_BUILD_EXAMPLE=OFF \
    -DSPDLOG_BUILD_TESTS=OFF \
    -DSPDLOG_BUILD_BENCH=OFF \
    -DSPDLOG_FMT_EXTERNAL=ON \
    -DCMAKE_PREFIX_PATH=${PREFIX} && \
    make -j$(nproc) && \
    make install && \
    make DESTDIR="/build_thirdparty" install && \
    cd ${BUILD} && \
    rm -rf spdlog

# nlohmann_json
RUN cd ${BUILD} && \
    mkdir nlohmann_json && \
    wget -qO- https://github.com/nlohmann/json/archive/refs/tags/v${NLOHMANN_JSON_VERSION}.tar.gz \
    | tar xvz -C nlohmann_json --strip-components=1 && \
    cd nlohmann_json && \
    mkdir build && \
    cd build && \
    cmake .. \
    -DCMAKE_INSTALL_PREFIX=${PREFIX} \
    -DCMAKE_INSTALL_LIBDIR=lib \
    -DJSON_BuildTests=OFF \
    -DJSON_Install=ON && \
    make -j$(nproc) && \
    make install && \
    make DESTDIR="/build_thirdparty" install && \
    cd ${BUILD} && \
    rm -rf nlohmann_json

# AWS SDK for C++
RUN cd ${BUILD} && \
    git clone --recurse-submodules --depth 1 -b ${AWSSDK_VERSION} https://github.com/aws/aws-sdk-cpp.git && \
    cd aws-sdk-cpp && \
    mkdir build && \
    cd build && \
    cmake .. \
    -DCMAKE_INSTALL_PREFIX=${PREFIX} \
    -DCMAKE_INSTALL_LIBDIR=lib \
    -DCMAKE_BUILD_TYPE=Release \
    -DCMAKE_POLICY_VERSION_MINIMUM=3.5 \
    -DBUILD_ONLY="s3;sts;identity-management" \
    -DENABLE_TESTING=OFF \
    -DBUILD_SHARED_LIBS=ON \
    -DMINIMIZE_SIZE=ON && \
    make -j$(nproc) && \
    make install && \
    make DESTDIR="/build_thirdparty" install && \
    cd ${BUILD} && \
    rm -rf aws-sdk-cpp

# TileDB
RUN if [ "${ENABLE_TILEDB}" = "ON" ]; then \
        cd ${BUILD} && \
        mkdir tiledb && \
        wget -q https://github.com/TileDB-Inc/TileDB/archive/refs/tags/${TILEDB_VERSION}.tar.gz -O - \
        | tar xz -C tiledb --strip-components=1 && \
        cd tiledb && \
        mkdir build_cmake && \
        cd build_cmake && \
        cmake .. \
        -DCMAKE_BUILD_TYPE=Release \
        -DCMAKE_INSTALL_PREFIX=${PREFIX} \
        -DCMAKE_DISABLE_FIND_PACKAGE_lz4=TRUE \
        -DTILEDB_S3=OFF \
        -DTILEDB_WERROR=OFF \
        -DTILEDB_DISABLE_AUTO_VCPKG=TRUE \
        -DTILEDB_TESTS=OFF \
        -DCOMPILER_SUPPORTS_AVX2=FALSE && \
        make -j$(nproc) && \
        make install && \
        make DESTDIR="/build_thirdparty" install && \
        for i in /build_thirdparty/usr/lib/*; do strip -s $i 2>/dev/null || /bin/true; done && \
        for i in /build_thirdparty/usr/bin/*; do strip -s $i 2>/dev/null || /bin/true; done && \
        cd ${BUILD} && \
        rm -rf tiledb; \
    else \
        echo "Skipping TileDB build (ENABLE_TILEDB=${ENABLE_TILEDB})"; \
    fi

# Build real bison/flex
RUN cd ${BUILD} && \
    mkdir bison-src && \
    wget -qO- https://ftp.gnu.org/gnu/bison/bison-3.8.2.tar.gz \
    | tar xz -C bison-src --strip-components=1 && \
    cd bison-src && \
    ./configure --prefix=/usr && \
    make -j$(nproc) MAKEINFO=true && \
    make install && \
    cd ${BUILD} && \
    rm -rf bison-src && \
    mkdir flex-src && \
    wget -qO- https://github.com/westes/flex/releases/download/v2.6.4/flex-2.6.4.tar.gz \
    | tar xz -C flex-src --strip-components=1 && \
    cd flex-src && \
    ./configure --prefix=/usr && \
    make -j$(nproc) && \
    make install && \
    cd ${BUILD} && \
    rm -rf flex-src

# Create a placeholder FindBin.pm
RUN mkdir -p /usr/local/share/perl5/5.32 && \
    cat > /usr/local/share/perl5/5.32/FindBin.pm <<'EOF'
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

# PostgreSQL
RUN if [ "${ENABLE_POSTGRESQL}" = "ON" ]; then \
        mkdir postgresql && \
        wget -qO- https://ftp.postgresql.org/pub/source/v${POSTGRESQL_VERSION}/postgresql-${POSTGRESQL_VERSION}.tar.gz \
        | tar xvz -C postgresql --strip-components=1 && \
        cd postgresql && \
        ./configure  --with-openssl --without-readline --prefix=$PREFIX && \
        make install && \
        make DESTDIR="/build_thirdparty" install && \
        ldconfig /usr/lib && \
        cd ${BUILD} && \
        rm -rf postgresql; \
    else \
        echo "Skipping PostgreSQL build (ENABLE_POSTGRESQL=${ENABLE_POSTGRESQL})"; \
    fi

# Apache Arrow
RUN if [ "${ENABLE_ARROW}" = "ON" ]; then \
        cd ${BUILD} && \
        mkdir arrow && \
        wget -qO- https://github.com/apache/arrow/archive/refs/tags/apache-arrow-${ARROW_VERSION}.tar.gz \
        | tar xvz -C arrow --strip-components=1 && \
        cd arrow/cpp && \
        sed -i 's@include(AWSSDKVariables)@include(${CMAKE_CURRENT_SOURCE_DIR}/cmake_modules/AWSSDKVariables.cmake)@' cmake_modules/ThirdpartyToolchain.cmake && \
        sed -i 's@include(san-config)@include(${CMAKE_CURRENT_SOURCE_DIR}/cmake_modules/san-config.cmake)@' CMakeLists.txt && \
        sed -i 's/resolve_dependency(lz4Alt/resolve_dependency(lz4/g' cmake_modules/ThirdpartyToolchain.cmake && \
        sed -i '/set(EP_COMMON_CMAKE_ARGS/a\  list(APPEND EP_COMMON_CMAKE_ARGS "-DCMAKE_POLICY_VERSION_MINIMUM=3.5")' cmake_modules/ThirdpartyToolchain.cmake && \
        mkdir build && \
        cd build && \
        cmake .. \
        -DCMAKE_INSTALL_PREFIX=${PREFIX} \
        -DCMAKE_INSTALL_LIBDIR=lib \
        -DCMAKE_POLICY_VERSION_MINIMUM=3.5 \
        -DCMAKE_MODULE_PATH=${BUILD}/arrow/cpp/cmake_modules \
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
        -DARROW_BUILD_TESTS=OFF && \
        make -j$(nproc) && \
        make install && \
        make DESTDIR="/build_thirdparty" install && \
        cd ${BUILD} && \
        rm -rf arrow; \
    else \
        echo "Skipping Arrow build (ENABLE_ARROW=${ENABLE_ARROW})"; \
    fi

RUN strip -s /build_thirdparty/usr/lib/* || /bin/true \
    && strip -s /build_proj/usr/bin/* || /bin/true

# Build and install GDAL
ARG GDAL_CACHE_BUST=1
RUN mkdir gdal \
    && curl -fL --retry 5 --retry-delay 3 --retry-all-errors \
    --http1.1 --connect-timeout 20 --max-time 600 \
    https://github.com/OSGeo/gdal/releases/download/v${GDAL_VERSION}/gdal-${GDAL_VERSION}.tar.gz \
    -o /tmp/gdal-${GDAL_VERSION}.tar.gz \
    || curl -fL --retry 8 --retry-delay 3 --retry-all-errors \
    --http1.1 --connect-timeout 20 --max-time 600 \
    https://codeload.github.com/OSGeo/gdal/tar.gz/refs/tags/v${GDAL_VERSION} \
    -o /tmp/gdal-${GDAL_VERSION}.tar.gz \
    && tar xzf /tmp/gdal-${GDAL_VERSION}.tar.gz -C gdal --strip-components=1 \
    && rm -f /tmp/gdal-${GDAL_VERSION}.tar.gz \
    && cd gdal \
    && mkdir build \
    && cd build \
    && cmake .. \
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
    -DGDAL_USE_OPENDRIVE=OFF \
    -DGDAL_USE_LIBQB3=OFF \
    -DGDAL_USE_LIBXML2=ON \
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
    -DGDAL_USE_SQLITE3=ON \
    -DGDAL_USE_SFCGAL=${ENABLE_SFCGAL} \
    -DGDAL_USE_TILEDB=${ENABLE_TILEDB} \
    -DGDAL_USE_WEBP=ON \
    -DGDAL_USE_ZLIB=ON \
    -DGDAL_USE_ZSTD=ON \
    && make -j$(nproc) \
    && make install \
    && make DESTDIR="/build_gdal" install \
    && cd /buildtmp \
    && rm -rf gdal

# Strip debug symbols from GDAL to reduce final image size
RUN strip -s /build_gdal/usr/lib/*.so* 2>/dev/null || /bin/true \
    && strip -s /build_gdal/usr/bin/* 2>/dev/null || /bin/true

# Normalize staged library layout for runtime copy into Wolfi image.
RUN for root in /build_thirdparty/usr /build_proj/usr /build_gdal/usr; do \
        if [ -d "${root}/lib64" ]; then \
            mkdir -p "${root}/lib"; \
            cp -a "${root}/lib64/." "${root}/lib/"; \
            rm -rf "${root}/lib64"; \
        fi; \
    done

# ==============================================================================
# Final Runtime Stage
# ==============================================================================
FROM --platform=${platform} cgr.dev/chainguard/wolfi-base AS runtime

ARG ENABLE_OCI=ON

# Install only the runtime dependencies (no -dev packages) required by GDAL/PROJ
RUN apk update && apk add --no-cache \
    libstdc++ \
    sqlite \
    curl \
    tiff \
    zlib \
    lz4 \
    liblz4-1 \
    libjpeg-turbo \
    libpng \
    libxml2 \
    libxml2-16 \
    expat \
    python3 \
    py3-numpy \
    pcre2 \
    libaio \
    glib \
    libgomp \
    gmp \
    mpfr \
    icu \
    libthrift \
    openssl \
    xz \
    bzip2 \
    tzdata

# Copy all compiled artifacts from the builder stage
COPY --from=builder /build_thirdparty/usr /usr
COPY --from=builder /build_proj/usr /usr
COPY --from=builder /build_projgrids/usr/share/proj /usr/share/proj
COPY --from=builder /build_gdal/usr /usr

# Configure Environment Variables for Oracle, GDAL, and PROJ
ENV PREFIX=/usr \
    PROJ_LIB=/usr/share/proj \
    GDAL_DATA=/usr/share/gdal \
    ORACLE_BASE=/usr/lib/instantclient \
    ORACLE_HOME=/usr/lib/instantclient \
    LD_LIBRARY_PATH=/usr/lib:/usr/lib/instantclient

# Ensure the dynamic linker knows about the new Oracle and GDAL libraries
RUN if [ "${ENABLE_OCI}" = "ON" ]; then \
        echo '/usr/lib/instantclient' | tee -a /etc/ld.so.conf.d/oracle_instantclient.conf; \
    fi \
    && ldconfig /usr/lib 2>/dev/null || true

# Verify installation, including Python GDAL bindings
RUN gdalinfo --version \
    && projinfo EPSG:4326 > /dev/null \
    && python3 -c 'from osgeo import gdal, ogr, osr; print("GDAL_PYTHON_VERSION=" + gdal.VersionInfo("--version")); print("OGR_DRIVER_COUNT=" + str(ogr.GetDriverCount())); print("OSR_CLASS=" + osr.SpatialReference().__class__.__name__)'

# Set the default command
CMD ["gdalinfo", "--version"]
