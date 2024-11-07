# Start from UBI9-minimal GDAL as the base image
ARG platform=linux/amd64 
FROM --platform=${platform} gdal-oci-ubi9-large AS builder

# versions of packages
ENV \
    POSTGIS_VERSION=3.4.2 \
    PROTOBUF_VERSION=23.4 \
    PROTOBUF_C_VERSION=1.5.0 \
    MAPSERVER_VERSION=8.2.2 \
    RSVG_VERSION=2.59.0 \
    HARFBUZZ_VERSION=2.8.2 \
    FRIBIDI_VERSION=1.0.15 \
    PIXMAN_VERSION=0.43.4 \
    CAIRO_VERSION=1.18.2 \
    RUST_VERSION=1.81.0 \
    PANGO_VERSION=1.54 \
    NGHTTP2_VERSION=1.63.0 \
    HTTPD_VERSION=2.4.62 \
    FCGID_VERSION=2.3.9 \
    APR_VERSION=1.7.5 \
    APRUTIL_VERSION=1.6.3

# Paths to things
ENV \
	BUILD=/build \
    NPROC=4 \
	PREFIX=/usr \
    CARGO_HOME=/usr/local/cargo \
    RUSTUP_HOME=/usr/local/rustup \
    PATH=$PATH:/usr/local/cargo/bin \
	LD_LIBRARY_PATH=/usr/lib:/usr/lib64:/usr/lib/postgresql:/usr/lib64:/usr/lib64/mpich2/lib/:/usr/local/cargo/bin \
    ORACLE_BASE=/usr/lib64/instantclient \
    ORACLE_HOME=/usr/lib64/instantclient \
    ORACLE_LIBRARY=/usr/lib64/instantclient/lib \
    ORACLE_INCLUDE_DIR=/usr/lib64/instantclient/include \
    BOOST_ROOT=/usr/lib64

ENV MESON_BUILD=$BUILD/meson/meson.py
# Install dependencies for building PROJ and GDAL
RUN \
    microdnf update -y &&\
    microdnf repolist && \
    microdnf install --enablerepo=ubi-9-baseos-rpms -y ca-certificates \
    wget \
    gcc \
    gcc-c++ \
    make \
    cmake \
    ninja-build \
    git \
    autoconf \
    automake \
    libtool \
    gettext \
    xz \
    xz-devel \
    freetype-devel \
    libcurl-devel \
    glib2-devel \
    libxslt-devel \
    libxml2-devel \
    glibc-locale-source \
    sqlite \
    sqlite-devel \
    kernel-headers \
    libtiff-devel \
    zlib-devel \
    libjpeg-devel \
    lz4-devel \
    libpng-devel \
    expat-devel \
    patch \
    bzip2 \
    m4 \
    openssh-server \
    pcre2-devel \
    unzip \
    python3 \
    python3-devel \
    python3-pip \
    python3-toml \
    python3-tomli \
    fontconfig-devel \    
    openssl-devel \
    mod_fcgid 

# switch to a build directory
WORKDIR /build


# Download and install Rust (includes Cargo)
RUN curl https://sh.rustup.rs -sSf | sh -s -- -y --default-toolchain ${RUST_VERSION} \
    && chmod -R a+w ${CARGO_HOME} ${RUSTUP_HOME}

RUN cargo install cargo-c
    
# Meson
RUN cd ${BUILD} && \
    mkdir meson && \
    wget -qO- https://github.com/mesonbuild/meson/releases/download/1.5.1/meson-1.5.1.tar.gz \
        | tar xvz -C meson --strip-components=1
    
# Harfbuzz
RUN cd ${BUILD} && \
    mkdir harfbuzz && \
    wget https://github.com/harfbuzz/harfbuzz/releases/download/$HARFBUZZ_VERSION/harfbuzz-$HARFBUZZ_VERSION.tar.xz && \
    tar -xvf harfbuzz-${HARFBUZZ_VERSION}.tar.xz -C harfbuzz --strip-components=1 && \
    cd harfbuzz && \
    ./configure -C \
      --prefix=${PREFIX} && \
    make && \
    make install && \
    ldconfig && \
    cd ${BUILD} && \
    rm -rf harfbuzz

# Fribidi
RUN cd ${BUILD} && \
    mkdir fribidi && \
    wget https://github.com/fribidi/fribidi/releases/download/v${FRIBIDI_VERSION}/fribidi-${FRIBIDI_VERSION}.tar.xz && \
    tar -xvf fribidi-${FRIBIDI_VERSION}.tar.xz -C fribidi --strip-components=1 && \
    cd fribidi && \
    ./configure -C \
      --prefix=${PREFIX} && \
    make && \
    make install && \
    ldconfig && \
    cd ${BUILD} && \
    rm -rf fribidi

# Pixman
RUN cd ${BUILD} && \
    mkdir pixman && \
    wget -qO- https://cairographics.org/releases/pixman-${PIXMAN_VERSION}.tar.gz \
        | tar xvz -C pixman --strip-components=1 && \
    cd pixman && \   
    $MESON_BUILD setup --prefix=${PREFIX} --buildtype=release build/ && \
    ninja -C build && \
    ninja -C build install && \
    ldconfig && \
    cd ${BUILD} && \
    rm -rf pixman

# Cairo
RUN cd ${BUILD} && \
    mkdir cairo && \
    wget -qO- https://cairographics.org/releases/cairo-${CAIRO_VERSION}.tar.xz \
        | tar xvJ -C cairo --strip-components=1 && \
    cd cairo && \
    $MESON_BUILD setup --prefix=${PREFIX} --buildtype=release build/ && \
    ninja -C build && \
    ninja -C build install && \
    ldconfig && \
    cd ${BUILD} && \
    rm -rf cairo
    
# Pango
RUN cd ${BUILD} && \
    mkdir pango && \
    wget -qO- https://gitlab.gnome.org/GNOME/pango/-/archive/${PANGO_VERSION}/pango-${PANGO_VERSION}.0.tar.gz  \
        | tar xvz -C pango --strip-components=1 && \
    cd pango && \
    $MESON_BUILD setup --prefix=${PREFIX} --wrap-mode=nofallback --buildtype=release build/ && \
    ninja -C build && \
    ninja -C build install && \
    ldconfig && \
    cd ${BUILD} && \
    rm -rf pango

# RSVG
RUN cd ${BUILD} && \
    mkdir rsvg && \
    wget -qO- https://gitlab.gnome.org/GNOME/librsvg/-/archive/${RSVG_VERSION}/librsvg-${RSVG_VERSION}.tar.gz \
    | tar xvz -C rsvg --strip-components=1 && \
    cd rsvg && \
    $MESON_BUILD setup --prefix=${PREFIX} --buildtype=release build/ && \
    ninja -C build && \
    ninja -C build install && \
    ldconfig && \
    cd ${BUILD} && \
    rm -rf rsvg

# # Lighttpd
# RUN cd ${build} && \
#     mkdir lighttpd && \
#     wget -qO- https://download.lighttpd.net/lighttpd/releases-1.4.x/lighttpd-${LIGHTTPD_VERSION}.tar.xz \
#     | tar xvJ -C lighttpd --strip-components=1 && \
#     cd lighttpd && \
#     ./autogen.sh && \
#     ./configure -C \
#         --disable-dependency-tracking \
#         --with-openssl &&\
#     make -j 4 && \
#     make install && \
#     ldconfig && \
#     cd ${BUILD} && \
#     rm -rf lighttpd

# Protobuf
RUN cd ${BUILD} &&\
    git clone https://github.com/protocolbuffers/protobuf.git --branch="v${PROTOBUF_VERSION}" && \
    cd protobuf && \
    git submodule update --init --recursive && \
    mkdir build && \
    cd build && \
    cmake ../ \
     -DCMAKE_INSTALL_PREFIX=${PREFIX} \
    && make -j$(nproc) \
    && make install \
    && ldconfig \
    && cd ${BUILD} \
    && rm -rf protobuf

# Protobuf-C
RUN cd ${BUILD} && \
    mkdir protobuf-c && \
    wget -qO- https://github.com/protobuf-c/protobuf-c/releases/download/v${PROTOBUF_C_VERSION}/protobuf-c-${PROTOBUF_C_VERSION}.tar.gz \
    | tar xvz -C protobuf-c --strip-components=1 && \
    cd protobuf-c && \
    ./configure --prefix=${PREFIX} && \
    make -j$(nproc) && \
    make install && \
    ldconfig && \
    cd ${BUILD} && \
    rm -rf protobuf-c

# PostGIS
RUN cd ${BUILD} && \
    mkdir postgis && \
    wget -qO- https://download.osgeo.org/postgis/source/postgis-${POSTGIS_VERSION}.tar.gz \
        | tar xvz -C postgis --strip-components=1 && \
    cd postgis && \
    ./configure \
      --prefix=${PREFIX} && \
    make && \
    make install && \
    cd ${BUILD} && \
    rm -rf postgis


# FASTCGI
RUN cd ${build} && \
    mkdir fcgi && \
    cd fcgi && wget https://github.com/FastCGI-Archives/fcgi2/archive/refs/heads/master.zip && \
    unzip master.zip && \
    cd fcgi2-master && \
    autoreconf -i && \
    ./configure && \
    make && \
    make install && \
    ldconfig && \
    cd ${BUILD} && \
    rm -rf fcgi 

# #NGHTTP2
# RUN cd ${BUILD} && \
#     mkdir -p nghttp2 && \
#     wget -qO- https://github.com/nghttp2/nghttp2/releases/download/v${NGHTTP2_VERSION}/nghttp2-${NGHTTP2_VERSION}.tar.gz | tar -xvz -C nghttp2 --strip-components=1 && \
#     cd nghttp2 && \
#     ./configure --prefix=${PREFIX} && \
#     make && \
#     make install && \
#     cd ${BUILD} && \
#     rm -rf nghttp2

# #HTTPD
# RUN cd ${BUILD} && \
#     mkdir -p httpd/srclib/apr httpd/srclib/apr-util && \
#     wget -qO- https://dlcdn.apache.org/httpd/httpd-${HTTPD_VERSION}.tar.gz | tar -xvz -C httpd --strip-components=1 && \
#     wget -qO- https://dlcdn.apache.org/httpd/mod_fcgid/mod_fcgid-${FCGID_VERSION}.tar.gz | tar -xvz -C httpd --strip-components=1 && \
#     wget -qO- https://dlcdn.apache.org//apr/apr-${APR_VERSION}.tar.gz | tar -xvz -C httpd/srclib/apr --strip-components=1 && \
#     wget -qO- https://dlcdn.apache.org//apr/apr-util-${APRUTIL_VERSION}.tar.gz | tar -xvz -C httpd/srclib/apr-util --strip-components=1 && \
#     # cp -a /mod_fcgid/. /httpd/ && \
#     cd httpd && \
#     ./buildconf && \
#     ./configure --enable-layout=Debian \
#     --enable-fcgid --with-included-apr --enable-headers --enable-status \
#     --disable-auth_basic --disable-authn_file --disable-authn_core \
#     --disable-authz_user --disable-autoindex --disable-dir && \
#     make && \
#     make install 
# #     cd ${BUILD} && \
# #     rm -rf httpd

# Mapserver
RUN \
    mkdir mapserver && \
    wget -qO- http://download.osgeo.org/mapserver/mapserver-${MAPSERVER_VERSION}.tar.gz \
        | tar xvz -C mapserver --strip-components=1 && \
    cd mapserver && \
    mkdir build && \
    cd build && \
    cmake ../ \
        -DCMAKE_PREFIX_PATH="/usr/lib;/usr/lib64" \
        -DCMAKE_INSTALL_PREFIX=$PREFIX \
        -DWITH_PROJ=1 \
        -DWITH_KML=0 \
        -DWITH_SOS=0 \
        -DWITH_WMS=1 \
        -DWITH_FRIBIDI=1 \
        -DWITH_HARFBUZZ=1 \
        -DWITH_PIXMAN=1 \
        -DWITH_ICONV=1 \
        -DWITH_CAIRO=1 \
        -DWITH_SVGCAIRO=0 \
        -DWITH_RSVG=1 \
        -DWITH_MYSQL=0 \
        -DWITH_FCGI=1 \
        -DWITH_GEOS=1 \
        -DWITH_POSTGIS=1 \
        -DWITH_GDAL=1 \
        -DWITH_OGR=1 \
        -DWITH_CURL=1 \
        -DWITH_CLIENT_WMS=1 \
        -DWITH_CLIENT_WFS=1 \
        -DWITH_WFS=1 \
        -DWITH_WCS=1 \
        -DWITH_LIBXML2=1 \
        -DWITH_THREAD_SAFETY=0 \
        -DWITH_GIF=1 \
        -DWITH_PYTHON=0 \
        -DWITH_PHP=0 \
        -DWITH_PERL=0 \
        -DWITH_RUBY=0 \
        -DWITH_JAVA=0 \
        -DWITH_CSHARP=0 \
        -DWITH_ORACLESPATIAL=1 \
        -DWITH_ORACLE_PLUGIN=0 \
        -DWITH_MSSQL2008=0 \
        -DWITH_SDE_PLUGIN=0 \
        -DWITH_SDE=0 \
        -DWITH_EXEMPI=0 \
        -DWITH_XMLMAPFILE=1 \
        -DWITH_V8=0 \
        -DBUILD_STATIC=0 \
        -DLINK_STATIC_LIBMAPSERVER=0 \
        -DWITH_APACHE_MODULE=0 \
        -DWITH_POINT_Z_M=1 \
        -DWITH_GENERIC_NINT=0 \
        -DWITH_PROTOBUFC=1 \
        -DCMAKE_INSTALL_PREFIX=$PREFIX && \
        make && \
        make install && \
        ldconfig
    


# RUN rm -rf /build

# # # Final image
# # ARG platform=linux/amd64 
# # FROM  --platform=${platform} gdal-oci-ubi9 AS service

# Let's copy a few of the settings from /etc/init.d/apache2
ENV APACHE_CONFDIR=/etc/httpd \
    APACHE_ENVVARS=/etc/httpd/envvars \
    # And then a few more from $APACHE_CONFDIR/envvars itself
    APACHE_RUN_USER=www-data \
    APACHE_RUN_GROUP=www-data \
    APACHE_RUN_DIR=/tmp/httpd \
    APACHE_PID_FILE=/tmp/httpd/httpd.pid \
    APACHE_LOCK_DIR=/var/lock/httpd \
    APACHE_LOG_DIR=/var/log/httpd \
    MS_MAP_PATTERN=^\\/etc\\/mapserver\\/([^\\.][-_A-Za-z0-9\\.]+\\/{1})*([-_A-Za-z0-9\\.]+\\.map)$

RUN mkdir --mode=go+w --parent ${APACHE_RUN_DIR} ${APACHE_LOCK_DIR} \
    && mkdir --parent /etc/mapserver \
    && mkdir -p /var/lib/httpd/fcgid/sock \
    && mkdir -m go+w -p /run/httpd /var/lock/httpd \
    && mkdir -p /etc/mapserver \
    && chmod o+w /var/lib/httpd/fcgid /var/lib/httpd/fcgid/sock || true \
    && find /etc/httpd -type f -exec sed -ri ' \
    s!^(\s*CustomLog)\s+\S+!\1 /proc/self/fd/1!g; \
    s!^(\s*ErrorLog)\s+\S+!\1 /proc/self/fd/2!g; \
    ' '{}' ';' \
    && sed -ri 's!LogFormat "(.*)" combined!LogFormat "%{us}T %{X-Request-Id}i \1" combined!g' /etc/httpd/conf/httpd.conf \
    && echo 'ErrorLogFormat "%{X-Request-Id}i [%l] [pid %P] %M"' >> /etc/httpd/conf/httpd.conf \
    && sed -i -e 's/Listen 80$/Listen 8080/' /etc/httpd/conf/httpd.conf \
    && rm -rf /etc/httpd/conf.d/other-vhosts-access-log.conf

COPY runtime /

RUN ldconfig

ENV MS_DEBUGLEVEL=0 \
    MS_ERRORFILE=stderr \
    MAPSERVER_CONFIG_FILE=/etc/mapserver.conf \
    MAPSERVER_BASE_PATH= \
    MAX_REQUESTS_PER_PROCESS=1000 \
    MIN_PROCESSES=1 \
    MAX_PROCESSES=5 \
    BUSY_TIMEOUT=300 \
    IDLE_TIMEOUT=300 \
    IO_TIMEOUT=40 \
    APACHE_LIMIT_REQUEST_LINE=8190 \
    GET_ENV=env

EXPOSE 8080

CMD ["/usr/local/bin/start-server"]

WORKDIR /etc/mapserver