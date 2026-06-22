# Start from UBI9 as the base image
ARG platform=linux/amd64 
FROM --platform=${platform} registry.access.redhat.com/ubi9/ubi AS builder
ARG REBUILD=false

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
    POSTGRESQL_VERSION=17.4 \    
    PROJ_VERSION=master \
    SFCGAL_VERSION=1.5.0 \
    SPDLOG_VERSION=1.14.1 \    
    TILEDB_VERSION=2.26.2 \
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
    wget curl unzip make libtool autoconf automake pkgconfig gcc-c++ sqlite sqlite-devel \
    kernel-headers \
    libcurl-devel \
    libtiff-devel \
    zlib-devel \
    libjpeg-devel \
    lz4-devel \
    libjpeg-turbo-devel \
    libpng-devel \
    libwebp-devel \
    libaio \
    expat-devel \
    postgresql-devel \
    python3-devel \
    python3-setuptools \
    cmake

RUN mkdir -p /buildtmp /build_thirdparty/usr/lib64

# switch to a build directory
WORKDIR /buildtmp

RUN pip3 install --upgrade pip
RUN pip3 install --upgrade wheel virtualenv 

RUN pip3 install --upgrade numpy rtree geopandas rasterio rio-cogeo
# Install SWIG no idea why this doesn't show in the repo but it doesn't
RUN curl -o swig.rpm https://cdn-ubi.redhat.com/content/public/ubi/dist/ubi9/9/x86_64/codeready-builder/os/Packages/s/swig-4.1.1-1.module+el9.2.0+17621+ec36a39e.x86_64.rpm -SL \
    && dnf install -y swig.rpm

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
    strip -s /build_thirdparty/usr/lib64/* || /bin/true && \
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
    strip -s /build_thirdparty/usr/lib64/* || /bin/true && \
    cd ${BUILD} && \
    rm -rf deflate

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
    # && strip -s /build_thirdparty/usr/lib64/* || /bin/true \
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
    # && strip -s /build_proj/usr/lib64/* || /bin/true \
    # && strip -s /build_proj/usr/bin/* || /bin/true \
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
    # strip -s /build_thirdparty/usr/lib64/* || /bin/true && \
    cd ${BUILD} && \
    rm -rf geotiff

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

ENV ORACLE_BASE /usr/lib64/instantclient
ENV LD_LIBRARY_PATH /usr/lib64/instantclient
ENV ORACLE_HOME /usr/lib64/instantclient
    
# GDAL
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
        -DGDAL_USE_TIFF_INTERNAL=ON \
        -DGDAL_USE_GEOTIFF_INTERNAL=ON \
        -DBUILD_PYTHON_BINDINGS=ON \
        # -DIconv_INCLUDE_DIR=/usr/include/gnu-libiconv \
        # -DIconv_LIBRARY=/usr/lib64/libiconv.so \
        -DBUILD_TESTING=OFF \
        -DOracle_ROOT=/usr/lib64/instantclient \
        -DGDAL_USE_ORACLE=ON \
        # -DOpenDrive_DIR=/usr/lib64/ \
        # -DOGR_ENABLE_DRIVER_XODR_PLUGIN=TRUE \
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
FROM --platform=${platform} registry1.dso.mil/ironbank/redhat/ubi/ubi9-minimal:9.5 AS runner

# Paths to things
ENV \
    ORACLE_BASE=/usr/lib64/instantclient \
    LD_LIBRARY_PATH=/usr/lib64/instantclient:/usr/lib \
    ORACLE_HOME=/usr/lib64/instantclient

RUN microdnf install -y \
        libstdc++ \
        sqlite sqlite-libs \
        libtiff \
        zlib libzstd lz4-libs libarchive \
        libjpeg-turbo libpng openjpeg2 libwebp expat libpq libaio python3-numpy \
    && rm -f /usr/lib64/libturbojpeg.so* \
    && rm -f /usr/lib64/libwebpmux.so* /usr/lib64/libwebpdemux.so* /usr/lib64/libwebpdecoder.so*

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
