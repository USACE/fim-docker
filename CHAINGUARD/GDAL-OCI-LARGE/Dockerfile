##
# Wolfi (Chainguard) based GDAL image
# Multi-stage build: builder compiles from source, runner is a minimal runtime.

ARG WOLFI_BASE=cgr.dev/chainguard/wolfi-base
ARG BUILD_JOBS=4

# ─────────────────────────────────────────────────────────────────────────────
# Stage 1 – builder
# ─────────────────────────────────────────────────────────────────────────────
FROM $WOLFI_BASE AS builder

ARG BUILD_JOBS

ENV \
    ARROW_VERSION=16.1.0 \
    DEFLATE_VERSION=1.25 \
    GDAL_VERSION=3.13.1 \
    GEOS_VERSION=3.14.0 \
    GEOTIFF_VERSION=1.7.4 \
    GIF_VERSION=5.2.2 \
    HDF5_VERSION=2.1.1 \
    KML_VERSION=1.3.0 \
    MINIZIP_VERSION=4.2.1 \
    NETCDF_VERSION=4.10.0 \
    OPENJPEG_VERSION=2.5.4 \
    POSTGRESQL_VERSION=18.4 \
    PROJ_VERSION=9.8.1 \
    URIPARSER_VERSION=1.0.2 \
    WEBP_VERSION=1.6.0 \
    ZLIB_VERSION=1.3.1 \
    ZSTD_VERSION=1.5.6

ENV \
    BUILD=/buildtmp \
    PREFIX=/usr \
    LD_LIBRARY_PATH=/usr/lib

# Install build dependencies available as Wolfi packages
RUN apk add --no-cache \
    build-base \
    cmake \
    ninja \
    curl \
    curl-dev \
    git \
    wget \
    pkgconf \
    autoconf \
    automake \
    bison \
    libtool \
    patch \
    python3 \
    python3-dev \
    py3-numpy \
    py3-setuptools \
    openssl \
    openssl-dev \
    sqlite \
    sqlite-dev \
    tiff \
    tiff-dev \
    zlib \
    zlib-dev \
    libpng \
    libpng-dev \
    libjpeg-turbo \
    libjpeg-turbo-dev \
    libwebp \
    libwebp-dev \
    expat \
    expat-dev \
    libxml2 \
    libxml2-dev \
    lz4 \
    lz4-dev \
    zstd \
    zstd-dev \
    pcre2 \
    pcre2-dev \
    json-c \
    json-c-dev \
    gmp-dev \
    mpfr-dev \
    bzip2 \
    bzip2-dev \
    xz \
    xz-dev \
    icu \
    icu-dev \
    boost-dev \
    swig \
    ca-certificates

RUN mkdir -p ${BUILD} /build /build_thirdparty/usr/lib /build_proj /build_projgrids/usr/share/proj

WORKDIR ${BUILD}

# ── ZSTD (from source to guarantee version) ──────────────────────────────────
RUN mkdir zstd \
    && wget -qO- https://github.com/facebook/zstd/releases/download/v${ZSTD_VERSION}/zstd-${ZSTD_VERSION}.tar.gz \
        | tar -xvz -C zstd --strip-components=1 \
    && cd zstd/build/cmake \
    && cmake . \
        -DBUILD_SHARED_LIBS=ON \
        -DCMAKE_BUILD_TYPE=Release \
        -DCMAKE_INSTALL_PREFIX=${PREFIX} \
    && make -j${BUILD_JOBS} \
    && make install \
    && make DESTDIR="/build_thirdparty" install \
    && cd ${BUILD} \
    && rm -rf zstd

# ── libdeflate ────────────────────────────────────────────────────────────────
RUN mkdir deflate \
    && wget -qO- https://github.com/ebiggers/libdeflate/releases/download/v${DEFLATE_VERSION}/libdeflate-${DEFLATE_VERSION}.tar.gz \
        | tar -xvz -C deflate --strip-components=1 \
    && cd deflate \
    && mkdir build && cd build \
    && cmake .. \
        -DBUILD_SHARED_LIBS=ON \
        -DCMAKE_BUILD_TYPE=Release \
        -DCMAKE_INSTALL_PREFIX=${PREFIX} \
    && make -j${BUILD_JOBS} \
    && make install \
    && make DESTDIR="/build_thirdparty" install \
    && cd ${BUILD} \
    && rm -rf deflate

# ── minizip-ng (required by libkml) ──────────────────────────────────────────
RUN mkdir minizip \
    && wget https://github.com/zlib-ng/minizip-ng/archive/refs/tags/${MINIZIP_VERSION}.tar.gz \
        -O minizip.tar.gz \
    && tar -xvzf minizip.tar.gz -C minizip --strip-components=1 \
    && cd minizip \
    && cmake -S . -B build \
        -DCMAKE_INSTALL_PREFIX=${PREFIX} \
        -DCMAKE_BUILD_TYPE=Release \
        -DBUILD_SHARED_LIBS=ON \
        -DCMAKE_POSITION_INDEPENDENT_CODE=ON \
    && cmake --build build -j${BUILD_JOBS} \
    && cmake --install build \
    && cmake --install build --prefix="/build_thirdparty/usr" \
    && cd ${BUILD} \
    && rm -rf minizip minizip.tar.gz

# ── uriparser (required by libkml) ───────────────────────────────────────────
RUN mkdir uri \
    && wget https://github.com/uriparser/uriparser/releases/download/uriparser-${URIPARSER_VERSION}/uriparser-${URIPARSER_VERSION}.tar.gz \
        -O uri.tar.gz \
    && tar -xvzf uri.tar.gz -C uri --strip-components=1 \
    && cd uri && mkdir build && cd build \
    && cmake .. \
        -DCMAKE_BUILD_TYPE=Release \
        -DCMAKE_INSTALL_PREFIX=${PREFIX} \
        -DURIPARSER_BUILD_TESTS=OFF \
        -DURIPARSER_BUILD_DOCS=OFF \
    && make -j${BUILD_JOBS} \
    && make install \
    && make DESTDIR="/build_thirdparty" install \
    && cd ${BUILD} \
    && rm -rf uri uri.tar.gz

# ── libkml ────────────────────────────────────────────────────────────────────
RUN mkdir libkml \
    && wget https://github.com/libkml/libkml/archive/refs/tags/${KML_VERSION}.tar.gz \
        -O libkml.tar.gz \
    && tar -xvzf libkml.tar.gz -C libkml --strip-components=1 \
    && perl -0pi -e 's@#include "boost/intrusive_ptr\.hpp"\n@#include "boost/intrusive_ptr.hpp"\n\nnamespace kmlbase {\nclass Referent;\nvoid intrusive_ptr_add_ref(Referent* r);\nvoid intrusive_ptr_release(Referent* r);\n}\n\n@' libkml/src/kml/dom/kml_ptr.h \
    && perl -0pi -e 's@namespace kmldom \{\n@namespace kmldom {\ntemplate <typename T>\ninline void intrusive_ptr_add_ref(T* p) {\n  kmlbase::intrusive_ptr_add_ref(static_cast<kmlbase::Referent*>(p));\n}\n\ntemplate <typename T>\ninline void intrusive_ptr_release(T* p) {\n  kmlbase::intrusive_ptr_release(static_cast<kmlbase::Referent*>(p));\n}\n\n@' libkml/src/kml/dom/kml_ptr.h \
    && cd libkml && mkdir build && cd build \
    && cmake .. \
        -DCMAKE_POLICY_VERSION_MINIMUM=3.5 \
        -DCMAKE_BUILD_TYPE=Release \
        -DCMAKE_INSTALL_PREFIX=${PREFIX} \
    && make -j${BUILD_JOBS} \
    && make install \
    && make DESTDIR="/build_thirdparty" install \
    && cd ${BUILD} \
    && rm -rf libkml libkml.tar.gz

# ── OpenJPEG ──────────────────────────────────────────────────────────────────
RUN mkdir openjpeg \
    && wget -q https://github.com/uclouvain/openjpeg/archive/v${OPENJPEG_VERSION}.tar.gz \
        -O openjpeg.tar.gz \
    && tar -xvzf openjpeg.tar.gz -C openjpeg --strip-components=1 \
    && cd openjpeg \
    && cmake . \
        -DBUILD_SHARED_LIBS=ON \
        -DBUILD_STATIC_LIBS=OFF \
        -DCMAKE_BUILD_TYPE=Release \
        -DCMAKE_INSTALL_PREFIX=${PREFIX} \
    && make -j${BUILD_JOBS} \
    && make install \
    && make install DESTDIR="/build_thirdparty" \
    && cd ${BUILD} \
    && rm -rf openjpeg openjpeg.tar.gz

# ── GIF ───────────────────────────────────────────────────────────────────────
RUN mkdir giflib && cd giflib \
    && wget https://sourceforge.net/projects/giflib/files/giflib-${GIF_VERSION}.tar.gz/download \
        -O giflib.tar.gz \
    && tar -xvzf giflib.tar.gz \
    && cd giflib-${GIF_VERSION} \
    && cp pic/gifgrid.gif doc/giflib-logo.gif \
    && make -j${BUILD_JOBS} \
    && make PREFIX=${PREFIX} install \
    && make PREFIX=${PREFIX} DESTDIR="/build_thirdparty" install \
    && cd ${BUILD} \
    && rm -rf giflib

# ── GEOS ──────────────────────────────────────────────────────────────────────
RUN mkdir geos \
    && wget -qO- https://download.osgeo.org/geos/geos-${GEOS_VERSION}.tar.bz2 \
        | tar -xvj -C geos --strip-components=1 \
    && cd geos \
    && cmake . \
        -DCMAKE_BUILD_TYPE=Release \
        -DCMAKE_INSTALL_PREFIX=${PREFIX} \
        -DBUILD_TESTING=OFF \
    && make -j${BUILD_JOBS} \
    && make install \
    && make DESTDIR="/build_thirdparty" install \
    && cd ${BUILD} \
    && rm -rf geos

# ── libwebp (from source to guarantee version) ───────────────────────────────
RUN mkdir webp \
    && wget -q https://storage.googleapis.com/downloads.webmproject.org/releases/webp/libwebp-${WEBP_VERSION}.tar.gz \
        -O - | tar xz -C webp --strip-components=1 \
    && cd webp && mkdir build && cd build \
    && cmake .. \
        -DCMAKE_BUILD_TYPE=Release \
        -DCMAKE_INSTALL_PREFIX=${PREFIX} \
    && make -j${BUILD_JOBS} \
    && make install \
    && make DESTDIR="/build_thirdparty" install \
    && cd ${BUILD} \
    && rm -rf webp

# ── HDF5 ──────────────────────────────────────────────────────────────────────
RUN mkdir hdf5 \
    && wget https://github.com/HDFGroup/hdf5/releases/download/hdf5_${HDF5_VERSION}/hdf5-${HDF5_VERSION}.tar.gz \
        -O hdf5.tar.gz \
    || wget https://github.com/HDFGroup/hdf5/releases/download/${HDF5_VERSION}/hdf5-${HDF5_VERSION}.tar.gz \
        -O hdf5.tar.gz \
    && tar -xvzf hdf5.tar.gz -C hdf5 --strip-components=2 \
    && cmake -S hdf5 -B hdf5/build \
        -DCMAKE_INSTALL_PREFIX=${PREFIX} \
        -DCMAKE_BUILD_TYPE=Release \
        -DBUILD_SHARED_LIBS=ON \
        -DHDF5_BUILD_CPP_LIB=ON \
        -DHDF5_BUILD_HL_LIB=ON \
        -DCMAKE_POSITION_INDEPENDENT_CODE=ON \
        -DHDF5_ENABLE_ZLIB_SUPPORT=ON \
        -DHDF5_ENABLE_SZIP_SUPPORT=OFF \
    && cmake --build hdf5/build -j${BUILD_JOBS} \
    && cmake --install hdf5/build \
    && cmake --install hdf5/build --prefix="/build_thirdparty/usr" \
    && cd ${BUILD} \
    && rm -rf hdf5 hdf5.tar.gz

# ── NetCDF-C ──────────────────────────────────────────────────────────────────
RUN mkdir netcdf \
    && wget https://downloads.unidata.ucar.edu/netcdf-c/${NETCDF_VERSION}/netcdf-c-${NETCDF_VERSION}.tar.gz \
        -O netcdf.tar.gz \
    && tar -xvzf netcdf.tar.gz -C netcdf --strip-components=1 \
    && cmake -S netcdf -B netcdf/build \
        -DCMAKE_INSTALL_PREFIX=${PREFIX} \
        -DENABLE_NETCDF_4=ON \
        -DHDF5_ROOT=${PREFIX} \
        -DCMAKE_PREFIX_PATH=${PREFIX} \
    && cmake --build netcdf/build -j${BUILD_JOBS} \
    && cmake --install netcdf/build \
    && cmake --install netcdf/build --prefix="/build_thirdparty/usr" \
    && cd ${BUILD} \
    && rm -rf netcdf netcdf.tar.gz

# ── PostgreSQL (for libpq) ────────────────────────────────────────────────────
RUN mkdir postgresql \
    && wget -qO- https://ftp.postgresql.org/pub/source/v${POSTGRESQL_VERSION}/postgresql-${POSTGRESQL_VERSION}.tar.gz \
        | tar xvz -C postgresql --strip-components=1 \
    && cd postgresql \
    && ./configure \
        --with-openssl \
        --without-readline \
        --prefix=${PREFIX} \
    && make install \
    && make DESTDIR="/build_thirdparty" install \
    && cd ${BUILD} \
    && rm -rf postgresql

# ── Apache Arrow (with Parquet) ───────────────────────────────────────────────
RUN mkdir arrow \
    && wget -qO- https://github.com/apache/arrow/archive/refs/tags/apache-arrow-${ARROW_VERSION}.tar.gz \
        | tar xvz -C arrow --strip-components=1 \
    && cmake -S arrow/cpp -B arrow/cpp/build \
        -DCMAKE_INSTALL_PREFIX=${PREFIX} \
        -DCMAKE_BUILD_TYPE=Release \
        -DCMAKE_POSITION_INDEPENDENT_CODE=ON \
        -DARROW_PARQUET=ON \
        -DARROW_COMPUTE=OFF \
        -DARROW_IPC=OFF \
        -DARROW_WITH_LZ4=ON \
        -DARROW_WITH_ZLIB=ON \
        -DARROW_WITH_ZSTD=ON \
        -DARROW_BUILD_SHARED=ON \
        -DARROW_BUILD_STATIC=OFF \
        -DARROW_JEMALLOC=OFF \
        -DARROW_MIMALLOC=OFF \
        -DARROW_BUILD_TESTS=OFF \
    && cmake --build arrow/cpp/build -j${BUILD_JOBS} \
    && cmake --install arrow/cpp/build \
    && cmake --install arrow/cpp/build --prefix="/build_thirdparty/usr" \
    && cd ${BUILD} \
    && rm -rf arrow

# ── PROJ datum grids ──────────────────────────────────────────────────────────
RUN curl -LOs http://download.osgeo.org/proj/proj-datumgrid-latest.zip \
    && unzip -q -j -u -o proj-datumgrid-latest.zip \
        -d /build_projgrids/usr/share/proj \
    && rm -f proj-datumgrid-latest.zip

# ── PROJ ──────────────────────────────────────────────────────────────────────
RUN mkdir proj \
    && wget -q https://github.com/OSGeo/PROJ/archive/${PROJ_VERSION}.tar.gz -O - \
        | tar xz -C proj --strip-components=1 \
    && cd proj \
    && cmake . \
        -DBUILD_SHARED_LIBS=ON \
        -DCMAKE_BUILD_TYPE=Release \
        -DCMAKE_INSTALL_PREFIX=${PREFIX} \
        -DENABLE_IPO=OFF \
        -DBUILD_TESTING=OFF \
    && make -j${BUILD_JOBS} \
    && make install \
    && make install DESTDIR="/build_proj" \
    && cd ${BUILD} \
    && rm -rf proj

# ── libgeotiff ────────────────────────────────────────────────────────────────
RUN mkdir geotiff \
    && wget https://download.osgeo.org/geotiff/libgeotiff/libgeotiff-${GEOTIFF_VERSION}.tar.gz \
        -O geotiff.tar.gz \
    && tar -xvzf geotiff.tar.gz -C geotiff --strip-components=1 \
    && cd geotiff \
    && ./configure \
        --prefix=${PREFIX} \
        --with-proj=${PREFIX} \
        --with-jpeg=${PREFIX} \
        --with-zip=yes \
    && make -j${BUILD_JOBS} \
    && make install \
    && make DESTDIR="/build_thirdparty" install \
    && cd ${BUILD} \
    && rm -rf geotiff geotiff.tar.gz

# ── GDAL ──────────────────────────────────────────────────────────────────────
RUN mkdir gdal \
    && wget -q https://github.com/OSGeo/gdal/releases/download/v${GDAL_VERSION}/gdal-${GDAL_VERSION}.tar.gz -O - \
        | tar xz -C gdal --strip-components=1 \
    && cd gdal \
    && mkdir build && cd build \
    && cmake .. \
        -DCMAKE_INSTALL_PREFIX=/usr \
        -DCMAKE_BUILD_TYPE=Release \
        -DBUILD_PYTHON_BINDINGS=ON \
        -DBUILD_TESTING=OFF \
        -DGDAL_USE_ARCHIVE=OFF \
        -DGDAL_USE_ARMADILLO=OFF \
        -DGDAL_USE_ARROW=ON \
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
        -DGDAL_USE_JPEG=ON \
        -DGDAL_USE_JPEG_INTERNAL=OFF \
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
        -DGDAL_USE_LIBQB3=OFF \
        -DGDAL_USE_LIBXML2=ON \
        -DGDAL_USE_LZ4=ON \
        -DGDAL_USE_MONGOCXX=OFF \
        -DGDAL_USE_MRSID=OFF \
        -DGDAL_USE_MSSQL_NCLI=OFF \
        -DGDAL_USE_MSSQL_ODBC=OFF \
        -DGDAL_USE_MYSQL=OFF \
        -DGDAL_USE_NETCDF=ON \
        -DGDAL_USE_ODBC=OFF \
        -DGDAL_USE_ODBCCPP=OFF \
        -DGDAL_USE_OPENCAD=OFF \
        -DGDAL_USE_OPENCAD_INTERNAL=OFF \
        -DGDAL_USE_OPENCL=OFF \
        -DGDAL_USE_OPENJPEG=ON \
        -DGDAL_USE_OPENSSL=ON \
        -DGDAL_USE_PARQUET=ON \
        -DGDAL_USE_PCRE2=ON \
        -DGDAL_USE_PDFIUM=OFF \
        -DGDAL_USE_PNG=ON \
        -DGDAL_USE_PNG_INTERNAL=OFF \
        -DGDAL_USE_POPPLER=OFF \
        -DGDAL_USE_POSTGRESQL=ON \
        -DGDAL_USE_QHULL=OFF \
        -DGDAL_USE_QHULL_INTERNAL=OFF \
        -DGDAL_USE_RASTERLITE2=OFF \
        -DGDAL_USE_RDB=OFF \
        -DGDAL_USE_SPATIALITE=OFF \
        -DGDAL_USE_SQLITE3=ON \
        -DGDAL_USE_SFCGAL=OFF \
        -DGDAL_USE_TEIGHA=OFF \
        -DGDAL_USE_TIFF=ON \
        -DGDAL_USE_TIFF_INTERNAL=OFF \
        -DGDAL_USE_TILEDB=OFF \
        -DGDAL_USE_WEBP=ON \
        -DGDAL_USE_XERCESC=OFF \
        -DGDAL_USE_ZLIB=ON \
        -DGDAL_USE_ZLIB_INTERNAL=OFF \
        -DGDAL_USE_ZSTD=ON \
    && make -j${BUILD_JOBS} \
    && make install DESTDIR="/build" \
    && cd ${BUILD} \
    && rm -rf gdal \
    && mkdir -p /build_gdal_python/usr/lib \
    && mkdir -p /build_gdal_python/usr/bin \
    && mkdir -p /build_gdal_version_changing/usr/include \
    && export py_version=$(python3 -c "import sys; print(str(sys.version_info.major) + '.' + str(sys.version_info.minor))") \
    && mv /build/usr/lib/python${py_version} /build_gdal_python/usr/lib \
    && mv /build/usr/lib                     /build_gdal_version_changing/usr \
    && mv /build/usr/include/gdal_version.h  /build_gdal_version_changing/usr/include \
    && mv /build/usr/bin/*.py                /build_gdal_python/usr/bin \
    && mv /build/usr/bin                     /build_gdal_version_changing/usr \
    && for i in /build_gdal_version_changing/usr/lib/*;  do strip -s $i 2>/dev/null || true; done \
    && for i in /build_gdal_python/usr/lib/python${py_version}/site-packages/osgeo/*.so; do strip -s $i 2>/dev/null || true; done \
    && for i in /build_gdal_version_changing/usr/bin/*; do strip -s $i 2>/dev/null || true; done \
    && for i in \
            /build/usr/share/gdal/*.svg \
            /build/usr/share/gdal/*.png \
       ; do rm -f $i; done

# ─────────────────────────────────────────────────────────────────────────────
# Stage 2 – runtime
# ─────────────────────────────────────────────────────────────────────────────
FROM $WOLFI_BASE AS runner

# Runtime packages only – no -dev headers, no build tools
RUN apk add --no-cache \
    python3 \
    py3-numpy \
    libstdc++ \
    sqlite-libs \
    tiff \
    openssl \
    zlib \
    zstd \
    lz4 \
    libjpeg-turbo \
    libpng \
    expat \
    libxml2 \
    libcurl-openssl4 \
    json-c \
    pcre2 \
    libwebp \
    ca-certificates

# Order layers starting with less frequently varying ones
COPY --from=builder /build_thirdparty/usr/ /usr/

COPY --from=builder /build_projgrids/usr/ /usr/

COPY --from=builder /build_proj/usr/share/proj/ /usr/share/proj/
COPY --from=builder /build_proj/usr/include/     /usr/include/
COPY --from=builder /build_proj/usr/bin/         /usr/bin/
COPY --from=builder /build_proj/usr/lib/         /usr/lib/

COPY --from=builder /build/usr/share/gdal/           /usr/share/gdal/
COPY --from=builder /build/usr/include/               /usr/include/
COPY --from=builder /build_gdal_python/usr/           /usr/
COPY --from=builder /build_gdal_version_changing/usr/ /usr/

# Rebuild the dynamic linker cache
RUN ldconfig

CMD ["gdalinfo", "--version"]
