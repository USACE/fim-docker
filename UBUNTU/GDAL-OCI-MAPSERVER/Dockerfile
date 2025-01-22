ARG platform=linux/amd64 
FROM --platform=${platform} ghcr.io/osgeo/gdal:ubuntu-small-3.8.5 AS gdal
# https://github.com/camptocamp/docker-mapserver/tree/master
FROM gdal AS builder
LABEL maintainer Camptocamp "info@camptocamp.com"
SHELL ["/bin/bash", "-o", "pipefail", "-cux"]

ENV ORACLE_VERSION=21.15.0.0.0 \
    ORACLE_BASE=/usr/local/lib \
    LD_LIBRARY_PATH=/usr/local/lib:/usr/lib \
    ORACLE_HOME=/usr/local/lib

RUN --mount=type=cache,target=/var/cache,sharing=locked \
    --mount=type=cache,target=/root/.cache \
    apt-get update \
    && apt-get upgrade --assume-yes \
    && DEBIAN_FRONTEND=noninteractive apt-get install --assume-yes --no-install-recommends bison \
        flex python3-lxml libfribidi-dev swig \
        cmake librsvg2-dev colordiff libpq-dev libpng-dev libjpeg-dev libgif-dev libgeos-dev libgd-dev \
        libfreetype6-dev libfcgi-dev libcurl4-gnutls-dev libcairo2-dev libxml2-dev \
        libxslt1-dev python3-dev php-dev libexempi-dev lcov lftp ninja-build git curl \
        clang libprotobuf-c-dev protobuf-c-compiler libharfbuzz-dev libcairo2-dev librsvg2-dev libaio-dev \
    && ln -s /usr/local/lib/libproj.so.25 /usr/local/lib/libproj.so

ARG MAPSERVER_BRANCH=branch-8-2
ARG MAPSERVER_REPO=https://github.com/mapserver/mapserver

RUN git clone ${MAPSERVER_REPO} --branch=${MAPSERVER_BRANCH} --depth=100 /src

COPY checkout_release /tmp
RUN cd /src \
    && /tmp/checkout_release ${MAPSERVER_BRANCH}

# Install Oracle Instant Client
ARG OracleMJR
RUN cd /tmp && \
    mkdir instantclient && \
    cd instantclient && \
    OracleMJR=$(echo "$ORACLE_VERSION" | tr -d '.') && \
    curl -o instantclient-basiclite.zip https://download.oracle.com/otn_software/linux/instantclient/$OracleMJR/instantclient-basic-linux.x64-${ORACLE_VERSION}dbru.zip -SL && \
    # unzip instantclient-basiclite.zip && \
    curl -o instantclient-sdk.zip https://download.oracle.com/otn_software/linux/instantclient/$OracleMJR/instantclient-sdk-linux.x64-${ORACLE_VERSION}dbru.zip -SL && \
    # unzip -o instantclient-sdk.zip && \
    curl -o instantclient-sqlplus.zip https://download.oracle.com/otn_software/linux/instantclient/$OracleMJR/instantclient-sqlplus-linux.x64-${ORACLE_VERSION}dbru.zip -SL 
    # unzip -o instantclient-sqlplus.zip && \
    # mkdir -p /usr/local/lib && \
    # mv instantclient*/ /usr/local/lib/instantclient && \
    # rm instantclient-basiclite.zip && \
    # rm instantclient-sdk.zip && \
    # rm instantclient-sqlplus.zip && \   
    # echo '/usr/local/lib/instantclient' | tee -a /etc/ld.so.conf.d/oracle_instantclient.conf && \
    # ldconfig    

ARG WITH_ORACLE=ON

RUN --mount=type=cache,target=/var/cache,sharing=locked \
    --mount=type=cache,target=/root/.cache \
    (if test "${WITH_ORACLE}" = "ON"; then \
       apt-get update && \
       apt-get install --assume-yes --no-install-recommends \
       libarchive-tools libaio-dev && \
       mkdir -p /usr/local/lib && \
       cd /usr/local/lib && \
       (for i in /tmp/instantclient/*.zip; do bsdtar --strip-components=1 -xvf "$i"; done) && \
       ln -s libnnz19.so /usr/local/lib/libnnz18.so; \
     fi )

WORKDIR /src/build
RUN if test "${WITH_ORACLE}" = "ON"; then \
      export ORACLE_HOME=/usr/local/lib; \
    fi; \
    cmake .. \
    -GNinja \
    -DCMAKE_C_FLAGS="-O2 -DPROJ_RENAME_SYMBOLS" \
    -DCMAKE_CXX_FLAGS="-O2 -DPROJ_RENAME_SYMBOLS" \
    -DCMAKE_BUILD_TYPE=Release \
    -DCMAKE_INSTALL_PREFIX=/usr/local \
    -DCMAKE_PREFIX_PATH="/usr/local/lib" \
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

RUN ninja install 

FROM gdal AS runner
LABEL maintainer Camptocamp "info@camptocamp.com"
SHELL ["/bin/bash", "-o", "pipefail", "-cux"]

# Let's copy a few of the settings from /etc/init.d/apache2
ENV APACHE_CONFDIR=/etc/apache2 \
    APACHE_ENVVARS=/etc/apache2/envvars \
    # And then a few more from $APACHE_CONFDIR/envvars itself
    APACHE_RUN_USER=www-data \
    APACHE_RUN_GROUP=www-data \
    APACHE_RUN_DIR=/tmp/apache2 \
    APACHE_PID_FILE=/tmp/apache2/apache2.pid \
    APACHE_LOCK_DIR=/var/lock/apache2 \
    APACHE_LOG_DIR=/var/log/apache2 \
    MS_MAP_PATTERN=^\\/etc\\/mapserver\\/([^\\.][-_A-Za-z0-9\\.]+\\/{1})*([-_A-Za-z0-9\\.]+\\.map)$   

RUN --mount=type=cache,target=/var/cache,sharing=locked \
    --mount=type=cache,target=/root/.cache \
    apt-get update \
    && apt-get upgrade --assume-yes \
    && apt-get install --assume-yes --no-install-recommends ca-certificates apache2 libapache2-mod-fcgid \
        libfribidi0 librsvg2-2 libpng16-16 libgif7 libfcgi0ldbl \
        libxslt1.1 libprotobuf-c1 libaio1 libpcre2-posix3 glibc-tools libaio-dev

RUN curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip" && \
    unzip awscliv2.zip && \
     ./aws/install

RUN a2enmod fcgid headers status \
    && a2dismod -f auth_basic authn_file authn_core authz_user autoindex dir \
    && rm /etc/apache2/mods-enabled/alias.conf \
    && mkdir --mode=go+w --parent ${APACHE_RUN_DIR} ${APACHE_LOCK_DIR} \
    && mkdir --parent /etc/mapserver \
    && chmod o+w /var/lib/apache2/fcgid /var/lib/apache2/fcgid/sock \
    && find "$APACHE_CONFDIR" -type f -exec sed -ri ' \
    s!^(\s*CustomLog)\s+\S+!\1 /proc/self/fd/1!g; \
    s!^(\s*ErrorLog)\s+\S+!\1 /proc/self/fd/2!g; \
    ' '{}' ';' \
    && sed -ri 's!LogFormat "(.*)" combined!LogFormat "%{us}T %{X-Request-Id}i \1" combined!g' /etc/apache2/apache2.conf \
    && echo 'ErrorLogFormat "%{X-Request-Id}i [%l] [pid %P] %M"' >> /etc/apache2/apache2.conf \
    && sed -i -e 's/<VirtualHost \*:80>/<VirtualHost *:8080>/' /etc/apache2/sites-available/000-default.conf \
    && sed -i -e 's/Listen 80$/Listen 8080/' /etc/apache2/ports.conf \
    && rm -rf /etc/apache2/conf-enabled/other-vhosts-access-log.conf

EXPOSE 8080

COPY --from=builder /usr/local/bin /usr/local/bin/
COPY --from=builder /usr/local/lib /usr/local/lib/
COPY --from=builder /usr/local/share/mapserver /usr/local/share/mapserver/
COPY --from=builder /src/share/ogcapi/templates/html-bootstrap4 /usr/local/share/mapserver/ogcapi/templates/html-bootstrap4/

COPY runtime /
# COPY mapfiles /etc/mapserver

ENV LD_LIBRARY_PATH=/usr/local/lib:/usr/lib \
    ORACLE_HOME=/usr/local/lib


RUN echo '/usr/local/lib' | tee -a /etc/ld.so.conf.d/oracle_instantclient.conf && \
    ldconfig

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

RUN mkdir -p /tmp/apache2 && \
    mkdir -p /etc/mapserver/logs/mapserver.log 
RUN touch /etc/mapserver/logs/mapserver.log && \
    chmod 777 /etc/mapserver/logs/*


CMD ["/usr/local/bin/start-server"]

WORKDIR /etc/mapserver