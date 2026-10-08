ARG PYTHON_BASE_IMAGE=python:3.11-slim-bookworm
FROM ${PYTHON_BASE_IMAGE}

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    FIVES_DB_PATH=/data/5s_crypto_v1.db

WORKDIR /app

COPY integrations/5s_crypto_binance_usdm_v1/app.py \
     integrations/5s_crypto_binance_usdm_v1/charting.py \
     integrations/5s_crypto_binance_usdm_v1/config.py \
     integrations/5s_crypto_binance_usdm_v1/m2_testnet_check.py \
     integrations/5s_crypto_binance_usdm_v1/requirements.txt \
     integrations/5s_crypto_binance_usdm_v1/runtime_testnet_session.py \
     integrations/5s_crypto_binance_usdm_v1/storage.py /app/
COPY integrations/5s_crypto_binance_usdm_v1/engine /app/engine
COPY integrations/5s_crypto_binance_usdm_v1/exchange /app/exchange
COPY integrations/5s_crypto_binance_usdm_v1/strategy /app/strategy
COPY integrations/5s_crypto_binance_usdm_v1/templates /app/templates
COPY integrations/5s_crypto_binance_usdm_v1/vendor /app/vendor
COPY deployment/5s-independent-server-module/entrypoint.py /app/deployment_entrypoint.py

RUN python -c 'import base64; from pathlib import Path; p=Path("/app/strategy"); p.joinpath("SSSS.ftindex").write_bytes(base64.b64decode(p.joinpath("SSSS.ftindex.b64").read_text(encoding="ascii")))'
RUN python -m pip install --no-cache-dir --upgrade pip \
    && python -m pip install --no-cache-dir -r requirements.txt

RUN groupadd --system --gid 10001 five_s \
    && useradd --system --uid 10001 --gid 10001 --no-create-home five_s \
    && mkdir -p /data \
    && chown -R 10001:10001 /app /data

USER 10001:10001
EXPOSE 8080
ENTRYPOINT ["python", "/app/deployment_entrypoint.py"]
