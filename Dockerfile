FROM node:22 AS npmbuilder
COPY . /src
WORKDIR /src
RUN npm ci
RUN npm run build

FROM python:3.12 AS wheelbuilder
WORKDIR /src
RUN pip install --no-cache-dir uv
COPY pyproject.toml uv.lock README.md LICENSE /src/
COPY scanomatic/ /src/scanomatic/
COPY scripts/ /src/scripts/
COPY data/ /src/data/
COPY --from=npmbuilder /src/scanomatic/ui_server_data/js/somlib /src/scanomatic/ui_server_data/js/somlib
RUN uv build --wheel --out-dir /tmp/wheels /src
RUN uv export --frozen --no-dev --no-emit-project --project /src --output-file /tmp/requirements.txt

FROM python:3.12-slim
RUN apt-get update
RUN export DEBIAN_FRONTEND=noninteractive \
    && ln -fs /usr/share/zoneinfo/Etc/UTC /etc/localtime \
    && apt-get install -y tzdata \
    && dpkg-reconfigure --frontend noninteractive tzdata
RUN apt-get update \
    && apt-get -y install \
        build-essential \
        usbutils \
        net-tools \
        iputils-ping \
        libsane1 \
        sane-utils \
        libsane-common \
        nmap \
    && rm -rf /var/lib/apt/lists/*
# Add scanner id to sane config in case scanimage -L cannot find the scanner automatically
# Epson V800
RUN echo "usb 0x4b8 0x12c" >> /etc/sane.d/epson2.conf
# Epson V700
RUN echo "usb 0x4b8 0x151" >> /etc/sane.d/epson2.conf

COPY --from=wheelbuilder /tmp/requirements.txt /tmp/requirements.txt
COPY --from=wheelbuilder /tmp/wheels /tmp/wheels
RUN pip install --no-cache-dir uv \
    && uv pip install --system --requirement /tmp/requirements.txt \
    && uv pip install --system --no-deps /tmp/wheels/scanomatic_standalone-*.whl \
    && rm -rf /root/.cache /tmp/wheels /tmp/requirements.txt

COPY data/ /tmp/data/
COPY setup_config.py /opt/setup_config.py
COPY docker-entrypoint.sh /opt/docker-entrypoint.sh
RUN chmod +x /opt/docker-entrypoint.sh

ENTRYPOINT ["/opt/docker-entrypoint.sh"]
CMD ["scan-o-matic", "--no-browser"]
EXPOSE 5000
