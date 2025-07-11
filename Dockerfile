FROM mcr.microsoft.com/vscode/devcontainers/python:3.13-bookworm

COPY requirements.txt .
RUN python3 -m pip install --requirement requirements.txt && \
    rm requirements.txt

RUN mkdir -p /config && \
    hass --config /config --script ensure_config && \
    wget -O - https://get.hacs.xyz | bash -
