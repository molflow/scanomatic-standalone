FROM python:3.9-bullseye

ENV DEBIAN_FRONTEND=noninteractive
ARG GECKODRIVER_VERSION=v0.31.0
ARG CHROME_VERSION=107.0.5304.110-1
ARG CHROMEDRIVER_VERSION=107.0.5304.62
ARG NODE_MAJOR=16

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        bzip2 \
        ca-certificates \
        curl \
        firefox-esr \
        git \
        gnupg2 \
        iputils-ping \
        libdbus-glib-1-2 \
        libsane \
        libsane-common \
        libxtst6 \
        net-tools \
        nmap \
        sane-utils \
        software-properties-common \
        tzdata \
        unzip \
        usbutils \
        wget \
        xauth \
        xvfb \
    && rm -rf /var/lib/apt/lists/*

RUN curl -fsSL https://deb.nodesource.com/setup_${NODE_MAJOR}.x | bash - \
    && apt-get update \
    && apt-get install -y --no-install-recommends nodejs \
    && node --version | grep -E "^v${NODE_MAJOR}\\." \
    && rm -rf /var/lib/apt/lists/*

RUN python3.9 -m pip install --no-cache-dir --upgrade pip \
    && python3.9 -m pip install --no-cache-dir tox==3.27.1

# Use distro Firefox ESR to ensure runtime library compatibility with Debian Bullseye.
RUN ln -sf /usr/bin/firefox-esr /usr/local/bin/firefox

RUN wget -q -O /tmp/geckodriver.tar.gz \
        "https://github.com/mozilla/geckodriver/releases/download/${GECKODRIVER_VERSION}/geckodriver-${GECKODRIVER_VERSION}-linux64.tar.gz" \
    && tar -xzf /tmp/geckodriver.tar.gz -C /usr/local/bin \
    && chmod +x /usr/local/bin/geckodriver \
    && rm -f /tmp/geckodriver.tar.gz

RUN wget -q -O /tmp/google-chrome.deb \
        "https://mirror.cs.uchicago.edu/google-chrome/pool/main/g/google-chrome-stable/google-chrome-stable_${CHROME_VERSION}_amd64.deb" \
    && apt-get update \
    && apt-get install -y --no-install-recommends /tmp/google-chrome.deb \
    && rm -f /etc/apt/sources.list.d/google-chrome.list \
    && rm -f /tmp/google-chrome.deb \
    && rm -rf /var/lib/apt/lists/*

RUN wget -q -O /tmp/chromedriver.zip \
        "https://chromedriver.storage.googleapis.com/${CHROMEDRIVER_VERSION}/chromedriver_linux64.zip" \
    && unzip -q /tmp/chromedriver.zip -d /tmp \
    && mv /tmp/chromedriver /usr/local/bin/chromedriver \
    && chmod +x /usr/local/bin/chromedriver \
    && rm -f /tmp/chromedriver.zip

# Add scanner IDs in case automatic discovery fails.
RUN echo "usb 0x4b8 0x12c" >> /etc/sane.d/epson2.conf \
    && echo "usb 0x4b8 0x151" >> /etc/sane.d/epson2.conf

WORKDIR /workspaces/scanomatic-standalone
