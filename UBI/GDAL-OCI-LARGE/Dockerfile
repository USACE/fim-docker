# Start from UBI9 as the base image
ARG platform=linux/amd64 
FROM --platform=${platform} registry.access.redhat.com/ubi9/ubi AS builder

# LATEST GDAL is 3.9.2 but postgis won't build
ENV \
    BOOST_VERSION=1.81.0 \
    CGAL_VERSION=5.6.1 \
    DEFLATE_VERSION=1.21 \
    GDAL_VERSION=3.8.5 \    
    GEOS_VERSION=3.13.0 \
    GEOTIFF_VERSION=1.7.3 \    
    GIF_VERSION=5.1.0 \   
    HDF5_VERSION=1.14.4.3 \  
    KML_VERSION=1.3.0 \
    MAGIC_VERSION=5.45 \
    MINIZIP_VERSION=1.3.0 \
    NETCDF_VERSION=4.9.2 \
    OPENJPEG_VERSION=2.3.1 \
    ORACLE_VERSION=21.15.0.0.0 \
    POSTGRESQL_VERSION=16.4 \    
    PROJ_VERSION=master \
    SFCGAL_VERSION=1.5.0 \
    SPDLOG_VERSION=1.14.1 \    
    TILEDB_VERSION=2.26.0 \
    URIPARSER_VERSION=0.9.8 \
    WEBP_VERSION=1.4.0 \
    ZLIB_VERSION=1.3.1 \
    ZSTD_VERSION=1.5.6 

# Paths to things
ENV \
	BUILD=/buildtmp \
    PREFIX=/usr \
    ORACLE_BASE=/usr/lib64/instantclient \
    LD_LIBRARY_PATH=/usr/lib64/instantclient:/usr/lib:/usr/lib64 \
    ORACLE_HOME=/usr/lib64/instantclient

# Install dependencies for building PROJ and GDAL
RUN dnf config-manager --set-enabled ubi-9-codeready-builder-rpms && \
    dnf update -y && dnf install -y --allowerasing \
    wget \
    curl \
    unzip \
    make \
    libtool \
    autoconf \
    automake \
    pkgconfig \
    ninja-build \
    gcc-c++ \
    sqlite \
    sqlite-devel \
    kernel-headers \
    libarchive \
    libcurl-devel \
    libtiff-devel \
    zlib-devel \
    libjpeg-devel \
    lz4-devel \
    libjpeg-turbo-devel \
    libpng-devel \
    libxml2-devel \
    expat-devel \
    python3-devel \
    python3-setuptools \
    pcre-devel \
    pcre2-devel \
    libaio \
    cmake \
    git \
    patch \
    glib2-devel \
    glibc-locale-source \
    glibc-gconv-extra \
    bzip2-devel \
    libicu-devel \
    expat-devel \
    gmp-devel \
    mpfr-devel \
    xz \
    xz-devel \
    bzip2 \
    openssl-devel


RUN mkdir -p /buildtmp /build_thirdparty/usr/lib64

# switch to a build directory
WORKDIR /buildtmp

# Install SWIG no idea why this doesn't show in the repo but it doesn't
RUN curl -o swig.rpm https://cdn-ubi.redhat.com/content/public/ubi/dist/ubi9/9/x86_64/codeready-builder/os/Packages/s/swig-4.1.1-1.module+el9.2.0+17621+ec36a39e.x86_64.rpm -SL \
    && dnf install -y swig.rpm

# JSON-C
RUN cd ${BUILD} && \
    git clone https://github.com/json-c/json-c.git && \
    mkdir json-c-build && \
    cd json-c-build && \
    cmake -DCMAKE_INSTALL_PREFIX=${PREFIX} -DCMAKE_BUILD_TYPE=Release ../json-c &&\
    make && \
    make install && \
    make DESTDIR="/build_thirdparty" install && \ 
    mkdir -p /build_thirdparty/usr/lib64 && \
    cp -P /usr/lib64/libjson-c*.so* /build_thirdparty/usr/lib64 && \
    cd ${BUILD} && \
    rm -rf json-c

# RUN cd ${BUILD} && \
#     mkdir zlib && \
#     wget https://zlib.net/zlib-${ZLIB_VERSION}.tar.gz -O - \
#     | tar xz -C zlib --strip-components=1 && \
#     cd zlib && \
#     ./configure && \
#     make && \
#     make install && \
#     make DESTDIR="/build_thirdparty" install && \    
#     mkdir -p /build_thirdparty/usr/lib64 && \
#     cp -P /usr/lib64/libzlib*.so* /build_thirdparty/usr/lib64 && \
#     strip -s /build_thirdparty/usr/lib64/* || /bin/true && \
#     cd ${BUILD} && \
#     rm -rf zlib

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
    mkdir -p /build_thirdparty/usr/lib64 && \
    cp -P /usr/lib64/libzstd*.so* /build_thirdparty/usr/lib64 && \
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
    mkdir -p /build_thirdparty/usr/lib64 && \
    cp -P /usr/lib64/libdeflate*.so* /build_thirdparty/usr/lib64 && \
    cd ${BUILD} && \
    rm -rf deflate

# BOOST
ARG BoostV
RUN cd ${BUILD} && \
    mkdir boost && \
    BoostV=$(echo "$BOOST_VERSION" | tr '.' '_') && \
    wget -qO- https://boostorg.jfrog.io/artifactory/main/release/${BOOST_VERSION}/source/boost_${BoostV}.tar.gz | tar -xvz -C boost --strip-components=1 && \
    cd boost && \
    ./bootstrap.sh --prefix=${PREFIX} && \
    ./b2 headers install && \ 
    ./bootstrap.sh --prefix="/build_thirdparty/usr" && \
    ./b2 headers install && \
    cd ${BUILD} && \
    rm -rf boost

# MINIzip for kml and gdal
RUN cd ${BUILD} && \
    mkdir minizip && \
    wget http://sourceforge.net/projects/libkml-files/files/${MINIZIP_VERSION}/minizip.tar.gz/download -O minizip.tar.gz && \
    tar -xvf  minizip.tar.gz  -C minizip --strip-components=1 && \
    cd minizip && \
    mkdir build && \
    cmake -S . -B build -D CMAKE_INSTALL_PREFIX=/usr -D CMAKE_BUILD_TYPE=Release && \
    cmake --build build && \
    cd build && \
    make -j$(nproc) && \
    make install && \
    make DESTDIR="/build_thirdparty" install && \
    cd ${BUILD} && \
    rm -rf minizip

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
    ldconfig && \
    cd ${BUILD} && \
    rm -rf cgal

# SFCGAL
RUN cd ${BUILD} && \
    mkdir sfcgal && \
    wget -qO- https://gitlab.com/SFCGAL/SFCGAL/-/archive/v${SFCGAL_VERSION}/SFCGAL-v${SFCGAL_VERSION}.tar.gz \
        | tar xvz -C sfcgal --strip-components=1 && \
    cd sfcgal && \
    cmake -S . -DCMAKE_INSTALL_PREFIX=${PREFIX} -B build && \
    cmake --build build && \
    cmake --install build && \
    cd build && \
    make DESTDIR="/build_thirdparty" install && \  
    cd ${BUILD} && \
    rm -rf sfcgal
    
# KML
RUN cd ${BUILD} && \
    mkdir libkml && \
    wget https://github.com/libkml/libkml/archive/refs/tags/${KML_VERSION}.tar.gz -O libkml.tar.gz && \
    tar -xvzf libkml.tar.gz -C libkml --strip-components=1 && \
    cd libkml  && \
    mkdir build && \
    cd build && \
    cmake .. -DCMAKE_BUILD_TYPE=Release -DCMAKE_INSTALL_PREFIX=${PREFIX} && \
    make -j$(nproc) && \
    make install && \
    make DESTDIR="/build_thirdparty" install && \ 
    cd ${BUILD} && \
    rm -rf libkml

# HDF5
ARG HDF5V
RUN cd ${BUILD} && \
    mkdir hdf5 && \
    HDF5V=$(echo $HDF5_VERSION | sed 's/\([0-9]\)\.\([0-9]\)$/\1-\2/') && \
    wget https://github.com/HDFGroup/hdf5/releases/download/hdf5_${HDF5_VERSION}/hdf5-$HDF5V.tar.gz -O hdf5.tar.gz && \
    tar -xvzf hdf5.tar.gz -C hdf5 --strip-components=2 && \
    cd hdf5 && \
    ./configure --prefix=${PREFIX} --enable-cxx --enable-build-mode=production --enable-unsupported --with-pthread=/usr && \
    make -j$(nproc) && \
    make install && \
    make DESTDIR="/build_thirdparty" install && \    
    mkdir -p /build_thirdparty/usr/lib64 && \
    cp -P ${PREFIX}/lib64/libhdf5*.so* /build_thirdparty/usr/lib64 && \
    cd ${BUILD} && \
    rm -rf hdf5
    
# NetCDF-C
RUN cd ${BUILD} && \
    mkdir netcdf && \
    wget https://downloads.unidata.ucar.edu/netcdf-c/${NETCDF_VERSION}/netcdf-c-${NETCDF_VERSION}.tar.gz -O netcdf.tar.gz && \
    tar -xvzf netcdf.tar.gz  -C netcdf --strip-components=1 && \
    cd netcdf && \
    mkdir build && \
    cd build && \
    cmake .. -DCMAKE_INSTALL_PREFIX=${PREFIX} –DENABLE_NETCDF_4=OFF && \
    make -j$(nproc) && \
    make install && \
    make DESTDIR="/build_thirdparty" install && \    
    mkdir -p /build_thirdparty/usr/lib64 && \
    cp -P /usr/lib64/libnetcdf*.so* /build_thirdparty/usr/lib64 && \
    cd ${BUILD} && \
    rm -rf netcdf

# Install Oracle Instant Client
ARG OracleMJR
RUN cd ${BUILD} && \
    mkdir oic && \
    OracleMJR=$(echo "$ORACLE_VERSION" | tr -d '.') && \
    curl -o instantclient-basiclite.zip https://download.oracle.com/otn_software/linux/instantclient/$OracleMJR/instantclient-basic-linux.x64-${ORACLE_VERSION}dbru.zip -SL && \
    unzip instantclient-basiclite.zip && \
    curl -o instantclient-sdk.zip https://download.oracle.com/otn_software/linux/instantclient/$OracleMJR/instantclient-sdk-linux.x64-${ORACLE_VERSION}dbru.zip -SL && \
    unzip -o instantclient-sdk.zip && \
    curl -o instantclient-sqlplus.zip https://download.oracle.com/otn_software/linux/instantclient/$OracleMJR/instantclient-sqlplus-linux.x64-${ORACLE_VERSION}dbru.zip -SL && \
    unzip -o instantclient-sqlplus.zip && \
    mv instantclient*/ ${PREFIX}/lib64/instantclient && \
    rm instantclient-basiclite.zip && \
    rm instantclient-sdk.zip && \
    rm instantclient-sqlplus.zip && \
    echo '/usr/lib64/instantclient' | tee -a /etc/ld.so.conf.d/oracle_instantclient.conf && \
    ldconfig && \
    mkdir -p /build_thirdparty/usr/lib64 && \
    cp -Pa ${PREFIX}/lib64/instantclient/. /build_thirdparty/usr/lib64/instantclient 

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
    && mkdir -p /build_thirdparty/usr/lib64 \
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
    mkdir -p /build_thirdparty/usr/lib64 && \
    cp -P /usr/lib64/libgeotiff*.so* /build_thirdparty/usr/lib64 && \
    cd ${BUILD} && \
    rm -rf geotiff

# GIF
RUN cd ${BUILD} && \
    mkdir giflib &&\
    cd giflib &&\
    wget https://sourceforge.net/projects/giflib/files/giflib-${GIF_VERSION}.tar.gz/download -O giflib.tar.gz && \
    tar -xvzf giflib.tar.gz && \
    cd giflib-${GIF_VERSION} && \
    ./autogen.sh --prefix=${PREFIX} && \
    make -j ${NPROC} install && \
    make DESTDIR="/build_thirdparty" install && \  
	cd ${BUILD} && \
    rm -rf giflib

# GEOS
RUN cd ${BUILD} && \
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
    rm -rf geos

# WEbP
RUN cd ${BUILD} && \
    mkdir webp && \
    wget -q https://storage.googleapis.com/downloads.webmproject.org/releases/webp/libwebp-${WEBP_VERSION}.tar.gz -O - \
        | tar xz -C webp --strip-components=1 && \
    cd webp  && \
    mkdir build && \
    cd build && \ 
    cmake .. -DCMAKE_BUILD_TYPE=Release -DCMAKE_PREFIX_PATH=${PREFIX} && \
    make -j$(nproc) && \
    make install && \
    make DESTDIR="/build_thirdparty" install && \    
    mkdir -p /build_thirdparty/usr/lib64 && \
    cp -P /usr/lib64/libwebp*.so* /build_thirdparty/usr/lib64 && \
    cd ${BUILD} && \
    rm -rf libwebp
    
# # SPDLog for TileDB
# RUN cd ${BUILD} && \
#     mkdir spdlog && \
#     wget -q https://github.com/gabime/spdlog/archive/refs/tags/v${SPDLOG_VERSION}.tar.gz -O - \
#         | tar xz -C spdlog --strip-components=1 && \
#     cd spdlog && \
#     mkdir build && \
#     cd build && \ 
#     cmake .. -DCMAKE_POSITION_INDEPENDENT_CODE=ON -DSPDLOG_INSTALL=ON -DCMAKE_PREFIX_PATH=${prefix} && \
#     make -j$(nproc) && \
#     make install &&\
#     make DESTDIR="/build_thirdparty" install && \
#     cd ${BUILD} && \
#     rm -rf spdlog

# # AWS s3
# RUN cd ${BUILD} && \
#     git clone --recurse-submodules https://github.com/aws/aws-sdk-cpp &&\
#     cd aws-sdk-cpp && \
#     mkdir build && \
#     cd build && \
#     cmake .. \
#     -DCMAKE_BUILD_TYPE=Release \
#     -DCMAKE_INSTALL_PREFIX=${PREFIX} \
#     -DBUILD_ONLY="s3;sts;cognito-identity;identity-management" \
#     && make install && \
#     make DESTDIR="/build_thirdparty" install && \
#     cd ${BUILD} && \
#     rm -rf aws-sdk-cpp

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
   
# # LZ4
# RUN cd ${BUILD} && \
#     mkdir lz4 && \
#     wget -q https://github.com/lz4/lz4/releases/download/v1.10.0/lz4-1.10.0.tar.gz -O - \
#         | tar xz -C lz4 --strip-components=1 && \
#     cd lz4 && \    
#     make && \
#     make install && \
#     ldconfig && \
#     make DESTDIR="/build_thirdparty" install && \
#     cd ${BUILD} && \
#     rm -rf lz4

# # TileDB
# RUN cd ${BUILD} && \
#     mkdir tiledb && \
#     wget -q https://github.com/TileDB-Inc/TileDB/archive/refs/tags/${TILEDB_VERSION}.tar.gz -O - \
#         | tar xz -C tiledb --strip-components=1 && \
#     cd tiledb && \
#     mkdir build_cmake \
#     && cd build_cmake && \
#     cmake .. -DCMAKE_BUILD_TYPE=Release -DCMAKE_PREFIX_PATH=${PREFIX} -DCMAKE_MODULE_PATH=${PREFIX} -DTILEDB_S3=ON -DCMAKE_INSTALL_PREFIX=${PREFIX} -DTILEDB_WERROR=OFF -DTILEDB_DISABLE_AUTO_VCPKG=TRUE \
#         -DTILEDB_TESTS=OFF -DCOMPILER_SUPPORTS_AVX2=FALSE  \
#         -DOPENSSL_INCLUDE_DIR=${PREFIX} -DOPENSSL_CRYPTO_LIBRARY=${PREFIX}/lib64/libcrypto.so -DOPENSSL_SSL_LIBRARY=${PREFIX}/lib64/libssl.so && \
#     make \
#     && make install \
#     && make DESTDIR="/build_thirdparty" install \    
#     && for i in /build_thirdparty/usr/lib64/*; do strip -s $i 2>/dev/null || /bin/true; done \
#     && for i in /build_thirdparty/usr/bin/*; do strip -s $i 2>/dev/null || /bin/true; done \
#     && cd ${BUILD} && \
#     rm -rf tiledb

# PostgreSQL
RUN \
    mkdir postgresql && \
    wget -qO- https://ftp.postgresql.org/pub/source/v${POSTGRESQL_VERSION}/postgresql-${POSTGRESQL_VERSION}.tar.gz \
        | tar xvz -C postgresql --strip-components=1 && \
    cd postgresql && \
    ./configure  --with-openssl --without-readline --prefix=$PREFIX && \
    make install && \
    make DESTDIR="/build_thirdparty" install && \
    ldconfig && \
    cd ${BUILD} && \
    rm -rf postgresql

RUN strip -s /build_thirdparty/usr/lib64/* || /bin/true \
    && strip -s /build_proj/usr/bin/* || /bin/true

# Build and install GDAL
RUN if [ "${HDF4_VERSION}" != "" ] && [ "$(uname -m)" = "x86_64" ]; then \
        dnf install -y libtirpc-devel \
        && export LDFLAGS="-ltirpc ${LDFLAGS}"; \
    fi \
    && mkdir gdal \
    && wget -q https://github.com/OSGeo/gdal/releases/download/v${GDAL_VERSION}/gdal-${GDAL_VERSION}.tar.gz -O - \
        | tar xz -C gdal --strip-components=1 \
    && cd gdal \
    && mkdir build \
    && cd build \
    && cmake .. \
        -DCMAKE_INSTALL_PREFIX=/usr \
        -DCMAKE_BUILD_TYPE=Release \
        -DBUILD_PYTHON_BINDINGS=ON \
        -DBUILD_TESTING=OFF \
        -DGDAL_USE_ARCHIVE=OFF \
        -DGDAL_USE_ARMADILLO=OFF \
        -DGDAL_USE_ARROW=OFF \
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
        -DGDAL_USE_FILE-DGDB=OFF \
        -DGDAL_USE_FREEXL=OFF \
        -DGDAL_USE_FYBA=OFF \
        -DGDAL_USE_GEOTIFF=ON \
        -DGDAL_USE_GEOTIFF_INTERNAL=OFF \
        -DGDAL_USE_GEOS=ON \
        -DGDAL_USE_GIF=ON \
        -DGDAL_USE_GIF_INTERNAL=OFF \
        -DGDAL_USE_GTA=OFF \
        -DGDAL_USE_HEIF=OFF \
        -DGDAL_USE_HDF4=OFF \
        -DGDAL_USE_HDF5=ON \
        -DGDAL_ENABLE_HDF5_GLOBAL_LOCK=ON \
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
        -DGDAL_USE_LIBLZMA=OFF \
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
        -DGDAL_USE_NETCDF=ON \
        -DGDAL_USE_ODBC=OFF \
        -DGDAL_USE_ODBCCPP=OFF \
        -DGDAL_USE_O-DGDI=OFF \
        -DGDAL_USE_OPENCAD=OFF \
        -DGDAL_USE_OPENCAD_INTERNAL=ON \
        -DGDAL_USE_OPENCL=OFF \
        -DGDAL_USE_OPENEXR=OFF \
        -DGDAL_USE_OPENJPEG=ON \
        -DGDAL_USE_OPENSSL=ON \
        -DOracle_ROOT=/usr/lib64/instantclient \
        -DGDAL_USE_ORACLE=ON \
        -DGDAL_USE_PARQUET=OFF \
        -DGDAL_USE_PCRE2=ON \
        -DGDAL_USE_PDFIUM=OFF \
        -DGDAL_USE_PNG=ON \
        -DGDAL_USE_PNG_INTERNAL=OFF \
        -DGDAL_USE_POPPLER=OFF \
        -DGDAL_USE_POSTGRESQL=ON \
        -DGDAL_USE_QHULL=OFF \
        -DGDAL_USE_QHULL_INTERNAL=ON \
        -DGDAL_USE_RASTERLITE2=OFF \
        -DGDAL_USE_RDB=OFF \
        -DGDAL_USE_SPATIALITE=OFF \
        -DGDAL_USE_SQLITE3=ON \
        -DGDAL_USE_SFCGAL=ON \
        -DGDAL_USE_TEIGHA=OFF \
        -DGDAL_USE_TIFF=ON \
        -DGDAL_USE_TIFF_INTERNAL=OFF \
        -DGDAL_USE_TILEDB=OFF \
        -DGDAL_USE_WEBP=OFF \
        -DGDAL_USE_XERCESC=OFF \
        -DGDAL_USE_ZLIB=ON \
        -DGDAL_USE_ZLIB_INTERNAL=OFF \
        -DGDAL_USE_ZSTD=ON \
    && make -j$(nproc) \
    && make install DESTDIR="/build" \
    && (make -j$(nproc) multireadtest && cp apps/multireadtest /build/usr/bin) \
    && cd .. \
    && cd .. \
    && rm -rf gdal \
    && mkdir -p /build_gdal_python/usr/lib64 \
    && mkdir -p /build_gdal_python/usr/bin \
    && mkdir -p /build_gdal_version_changing/usr/include \
    && export py_version=$(python3 -c "import sys; print(str(sys.version_info.major) + '.' + str(sys.version_info.minor))") \
    && mv /build/usr/lib64/python${py_version} /build_gdal_python/usr/lib64 \
    && mv /build/usr/lib64                    /build_gdal_version_changing/usr \
    && mv /build/usr/include/gdal_version.h /build_gdal_version_changing/usr/include \
    && mv /build/usr/bin/*.py               /build_gdal_python/usr/bin \
    && mv /build/usr/bin                    /build_gdal_version_changing/usr \
    && for i in /build_gdal_version_changing/usr/lib64/*; do strip -s $i 2>/dev/null || /bin/true; done \
    && for i in /build_gdal_python/usr/lib64/python${py_version}/site-packages/osgeo/*.so; do strip -s $i 2>/dev/null || /bin/true; done \
    && for i in /build_gdal_version_changing/usr/bin/*; do strip -s $i 2>/dev/null || /bin/true; done \
    && for i in \
            /build/usr/share/gdal/*.svg \
            /build/usr/share/gdal/*.png \
       ;do rm $i; done

# Final image
ARG platform=linux/amd64 
FROM --platform=${platform} registry1.dso.mil/ironbank/redhat/ubi/ubi9-minimal:9.4 AS runner

# ENV \
#     ORACLE_VERSION=21.15.0.0.0

# Paths to things
ENV \
    ORACLE_BASE=/usr/lib64/instantclient \
    LD_LIBRARY_PATH=/usr/lib64/instantclient:/usr/lib \
    ORACLE_HOME=/usr/lib64/instantclient

RUN microdnf install -y \
        libstdc++ \
        sqlite-libs \
        libtiff \
        zlib libzstd lz4-libs libarchive \
        libjpeg-turbo libpng openjpeg2 expat libaio python3-numpy gmp-devel unzip  \
    && rm -f /usr/lib64/libturbojpeg.so* \
    && rm -f /usr/lib64/libwebpmux.so* /usr/lib64/libwebpdemux.so* /usr/lib64/libwebpdecoder.so*

# Update library paths
# ARG OracleMJR
RUN echo '/usr/lib64/instantclient' | tee -a /etc/ld.so.conf.d/oracle_instantclient.conf && \
    ldconfig 

# Order layers starting with less frequently varying ones
COPY --from=builder /build_thirdparty/usr/ /usr/

COPY --from=builder /build_projgrids/usr/ /usr/

COPY --from=builder /build_proj/usr/share/proj/ /usr/share/proj/
COPY --from=builder /build_proj/usr/include/ /usr/include/
COPY --from=builder /build_proj/usr/bin/ /usr/bin/
COPY --from=builder /build_proj/usr/lib64/ /usr/lib64/

# COPY --from=builder  /build/usr/share/java /usr/share/java
COPY --from=builder  /build/usr/share/gdal/ /usr/share/gdal/
COPY --from=builder  /build/usr/include/ /usr/include/
COPY --from=builder  /build_gdal_python/usr/ /usr/
COPY --from=builder  /build_gdal_version_changing/usr/ /usr/
