FROM mcr.microsoft.com/devcontainers/python:1-3.13-bookworm

ENV DEBIAN_FRONTEND=noninteractive

RUN rm -f /etc/apt/sources.list.d/yarn.list \
    && rm -f /etc/apt/sources.list.d/yarn.sources \
    && apt-get update \
    && apt-get install -y --no-install-recommends \
        curl \
        ca-certificates \
        gnupg \
        xvfb \
        chromium \
        chromium-driver \
        chromium-sandbox \
        firefox-esr \
        libsane1 \
        sane-utils \
        libsane-common \
        usbutils \
        net-tools \
        iputils-ping \
        nmap \
        docker.io \
        docker-compose \
    && rm -rf /var/lib/apt/lists/*

RUN curl -fsSL https://deb.nodesource.com/setup_22.x | bash - \
    && apt-get update \
    && apt-get install -y --no-install-recommends nodejs \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir uv tox-uv

# Mirror scanner hints from runtime Docker image.
RUN echo "usb 0x4b8 0x12c" >> /etc/sane.d/epson2.conf \
    && echo "usb 0x4b8 0x151" >> /etc/sane.d/epson2.conf
