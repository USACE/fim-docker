ARG PLATFORM=linux/amd64

# ==========================================
# Stage 1: Build Environment
# ==========================================
FROM --platform=${PLATFORM} docker.io/library/gdal-chainguard:oci-only AS gdal
FROM gdal AS builder

SHELL ["/bin/sh", "-eux", "-c"]

# Set Oracle and Library System Variables
ENV ORACLE_VERSION=21.15.0.0.0 \
    ORACLE_BASE=/usr/local/lib \
    LD_LIBRARY_PATH=/usr/local/lib:/usr/lib \
    ORACLE_HOME=/usr/local/lib

RUN apk update && apk add \
    bash \
    build-base \
    bison \
    flex \
    swig \
    cmake \
    ninja-build \
    git \
    curl \
    curl-dev \
    unzip \
    libarchive-tools \
    libaio-dev \
    fribidi-dev \
    librsvg-dev \
    postgresql-18-dev \
    libpng-dev \
    libjpeg-turbo-dev \
    giflib-dev \
    geos-3.14-dev \
    gd-dev \
    freetype-dev \
    cairo-dev \
    libxml2-dev \
    libxslt-dev \
    python-3.12-dev \
    py3-lxml \
    protobuf-c-dev \
    protobuf-c-compiler \
    harfbuzz-dev \
    && ln -sf /usr/bin/ninja-build /usr/bin/ninja

ARG MAPSERVER_BRANCH=branch-8-6
ARG MAPSERVER_REPO=https://github.com/mapserver/mapserver
ARG WITH_ORACLE=ON

# Clone MapServer Repository
RUN git clone ${MAPSERVER_REPO} --branch=${MAPSERVER_BRANCH} --depth=100 /src

COPY CHAINGUARD/MAPSERVER/checkout_release /tmp/checkout_release
RUN chmod +x /tmp/checkout_release \
    && /tmp/checkout_release ${MAPSERVER_BRANCH}

# Download Oracle Instant Client SDK components if Oracle is enabled
RUN if [ "${WITH_ORACLE}" = "ON" ]; then \
        mkdir -p /tmp/instantclient && cd /tmp/instantclient; \
        OracleMJR="$(echo "$ORACLE_VERSION" | tr -d '.')"; \
        curl -fSL -o instantclient-basiclite.zip "https://download.oracle.com/otn_software/linux/instantclient/${OracleMJR}/instantclient-basic-linux.x64-${ORACLE_VERSION}dbru.zip"; \
        curl -fSL -o instantclient-sdk.zip "https://download.oracle.com/otn_software/linux/instantclient/${OracleMJR}/instantclient-sdk-linux.x64-${ORACLE_VERSION}dbru.zip"; \
        curl -fSL -o instantclient-sqlplus.zip "https://download.oracle.com/otn_software/linux/instantclient/${OracleMJR}/instantclient-sqlplus-linux.x64-${ORACLE_VERSION}dbru.zip"; \
    fi

# Extract and link Oracle Instant Client Libraries
RUN --mount=type=cache,target=/var/cache,sharing=locked \
    --mount=type=cache,target=/root/.cache \
    if [ "${WITH_ORACLE}" = "ON" ]; then \
        mkdir -p /usr/local/lib && cd /usr/local/lib; \
        for i in /tmp/instantclient/*.zip; do bsdtar --strip-components=1 -xvf "$i"; done; \
        clntsh_target="$(find /usr/local/lib -maxdepth 1 -type f -name 'libclntsh.so*' | sort -V | tail -n 1)"; \
        occi_target="$(find /usr/local/lib -maxdepth 1 -type f -name 'libocci.so*' | sort -V | tail -n 1)"; \
        nnz_target="$(find /usr/local/lib -maxdepth 1 -type f \( -name 'libnnz*.so' -o -name 'libnnz*.so.*' \) | sort -V | tail -n 1)"; \
        test -n "${clntsh_target}" && test -n "${occi_target}" && test -n "${nnz_target}"; \
        ln -sfn "${clntsh_target}" /usr/local/lib/libclntsh.so; \
        ln -sfn "${occi_target}" /usr/local/lib/libocci.so; \
        ln -sfn "${nnz_target}" /usr/local/lib/libnnz19.so; \
        ln -sf /usr/local/lib/libnnz19.so /usr/local/lib/libnnz18.so; \
        ln -sf /usr/local/lib/libnnz19.so /usr/local/lib/libnnz12.so; \
        ln -sf /usr/local/lib/libnnz19.so /usr/local/lib/libnnz11.so; \
        ln -sf /usr/local/lib/libnnz19.so /usr/local/lib/libnnz10.so; \
        ln -sfn /usr/local/lib/sdk/include /usr/local/lib/include; \
    fi

# Configure & Compile MapServer with CMake and Ninja
WORKDIR /src/build
RUN if [ "${WITH_ORACLE}" = "ON" ]; then export ORACLE_HOME=/usr/local/lib; fi; \
    cmake -G Ninja .. \
        -DCMAKE_C_FLAGS="-O2" \
        -DCMAKE_CXX_FLAGS="-O2" \
        -DCMAKE_BUILD_TYPE=Release \
        -DCMAKE_INSTALL_PREFIX=/usr/local \
        -DCMAKE_PREFIX_PATH="/usr/local/lib" \
        -DORACLE_INCLUDE_DIR=/usr/local/lib/include \
        -DWITH_FCGI=0 \
        -DWITH_CLIENT_WMS=1 \
        -DWITH_CLIENT_WFS=1 \
        -DWITH_OGCAPI=1 \
        -DWITH_KML=1 \
        -DWITH_SOS=1 \
        -DWITH_XMLMAPFILE=1 \
        -DWITH_CAIRO=1 \
        -DWITH_RSVG=1 \
        -DUSE_PROJ=1 \
        -DUSE_WFS_SVR=1 \
        -DUSE_OGCAPI_SVR=1 \
        -DWITH_ORACLESPATIAL=${WITH_ORACLE}

RUN ninja && ninja install

# ==========================================
# Stage 2: Runtime Runner Environment
# ==========================================
FROM gdal AS runner

SHELL ["/bin/sh", "-eux", "-c"]

ARG SMOKE_TEST=0
ARG BUILD_ENV=prod

# Apache environment configuration
ENV APACHE_CONFDIR=/etc/apache2 \
    APACHE_ENVVARS=/etc/apache2/envvars \
    APACHE_RUN_USER=daemon \
    APACHE_RUN_GROUP=daemon \
    APACHE_RUN_DIR=/tmp/apache2 \
    APACHE_PID_FILE=/tmp/apache2/apache2.pid \
    APACHE_LOCK_DIR=/var/lock/apache2 \
    APACHE_LOG_DIR=/var/log/apache2 \
    MS_MAP_PATTERN="^\/etc\/mapserver\/([^ \.][-_A-Za-z0-9\.]+\/{1})*([-_A-Za-z0-9\.]+\.map)$"

# Install runtime package dependencies
RUN apk update && apk add \
    bash \
    ca-certificates \
    apache2 \
    apache2-compat \
    apache2-config-compat \
    apache2-utils \
    fribidi \
    librsvg \
    libpng \
    giflib \
    libxslt \
    protobuf-c \
    libaio \
    libpcre2-posix-3 \
    glibc \
    python3 \
    py3-lxml \
    aws-cli-2 \
    curl \
    unzip \
    && mkdir --mode=0777 --parent ${APACHE_RUN_DIR} ${APACHE_LOCK_DIR} /etc/mapserver

# Development Environment Dependencies installation (if BUILD_ENV=dev)
RUN if [ "${BUILD_ENV}" = "dev" ]; then \
        apk add \
            py3-pip \
            krb5 \
            krb5-libs \
            krb5-dev \
            build-base \
            python3-dev \
        && python3 -m pip install --no-cache-dir --break-system-packages aws-adfs \
        && apk del krb5-dev build-base python3-dev; \
    fi

# Configure Apache (httpd.conf adjustments)
RUN sed -i 's/^Listen 80$/Listen 8080/' /etc/apache2/httpd.conf \
    && sed -i 's/^User .*/User daemon/' /etc/apache2/httpd.conf \
    && sed -i 's/^Group .*/Group daemon/' /etc/apache2/httpd.conf \
    && sed -i 's|^#LoadModule cgid_module modules/mod_cgid.so|LoadModule cgid_module modules/mod_cgid.so|' /etc/apache2/httpd.conf \
    && sed -i 's|^#LoadModule proxy_module modules/mod_proxy.so|LoadModule proxy_module modules/mod_proxy.so|' /etc/apache2/httpd.conf \
    && sed -i 's|^#LoadModule proxy_fcgi_module modules/mod_proxy_fcgi.so|LoadModule proxy_fcgi_module modules/mod_proxy_fcgi.so|' /etc/apache2/httpd.conf \
    && sed -i 's|^#LoadModule alias_module modules/mod_alias.so|LoadModule alias_module modules/mod_alias.so|' /etc/apache2/httpd.conf \
    && sed -i 's|^ErrorLog "logs/error_log"|ErrorLog /proc/self/fd/2|' /etc/apache2/httpd.conf \
    && sed -i 's|^CustomLog "logs/access_log" common|CustomLog /proc/self/fd/1 combined|' /etc/apache2/httpd.conf \
    && (grep -q '^IncludeOptional /etc/apache2/conf-enabled/\*\.conf' /etc/apache2/httpd.conf || echo 'IncludeOptional /etc/apache2/conf-enabled/*.conf' >> /etc/apache2/httpd.conf) \
    && mkdir -p /etc/apache2/conf-enabled

EXPOSE 8080

# Import Compiled binaries and libraries from Builder
COPY --from=builder /usr/local/bin /usr/local/bin/
COPY --from=builder /usr/local/lib /usr/local/lib/
COPY --from=builder /usr/local/share/mapserver /usr/local/share/mapserver/
COPY CHAINGUARD/MAPSERVER/runtime /

ENV LD_LIBRARY_PATH=/usr/local/lib:/usr/lib \
    ORACLE_HOME=/usr/local/lib

RUN echo '/usr/local/lib' | tee -a /etc/ld.so.conf.d/oracle_instantclient.conf \
    && ldconfig

# Application Runtime Parameters
ENV MS_DEBUGLEVEL=0 \
    MS_ERRORFILE=stderr \
    MAPSERVER_CONFIG_FILE=/etc/mapserver.conf \
    MAPSERVER_BASE_PATH="" \
    MAX_REQUESTS_PER_PROCESS=1000 \
    MIN_PROCESSES=1 \
    MAX_PROCESSES=5 \
    BUSY_TIMEOUT=300 \
    IDLE_TIMEOUT=300 \
    IO_TIMEOUT=40 \
    APACHE_LIMIT_REQUEST_LINE=8190 \
    GET_ENV=env \
    SMOKE_TEST=${SMOKE_TEST}

# Establish writable logging pathways
RUN mkdir -p /tmp/apache2 /etc/mapserver/logs \
    && touch /etc/mapserver/logs/mapserver.log \
    && chmod 777 /etc/mapserver/logs/*

CMD ["/usr/local/bin/start-server"]

WORKDIR /etc/mapserver
