FROM mcr.microsoft.com/vscode/devcontainers/python:0-3.10-bullseye

COPY requirements.txt .
RUN python3 -m pip install --requirement requirements.txt && \
    rm requirements.txt

RUN mkdir -p /config && \
    hass --config /config --script ensure_config && \
    wget -O - https://get.hacs.xyz | bash -
