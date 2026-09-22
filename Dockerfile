FROM python:3.12.13-slim@sha256:229a2c5bfa27522db7815ea81f9bed70af17ccb9de9fc7ad142b1877b5830d36
ENV PYTHONUNBUFFERED=1 UV_PROJECT_ENVIRONMENT=/opt/venv UV_LINK_MODE=copy
WORKDIR /app
RUN pip install --no-cache-dir uv==0.12.17
COPY pyproject.toml uv.lock ./
COPY packages ./packages
COPY scripts ./scripts
RUN uv sync --frozen
COPY . .
EXPOSE 8000
CMD ["uv", "run", "uvicorn", "readout_api.app:app", "--host", "0.0.0.0", "--port", "8000"]
