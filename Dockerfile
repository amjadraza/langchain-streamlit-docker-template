# The builder image, used to build the virtual environment
FROM python:3.12-slim-bookworm as builder
COPY --from=ghcr.io/astral-sh/uv:0.4.24 /uv /uvx /bin/

RUN apt-get update && apt-get install -y git

ENV HOST=0.0.0.0
ENV LISTEN_PORT 8080
EXPOSE 8080

WORKDIR /app

COPY pyproject.toml ./

# Install dependencies using uv
RUN uv venv .venv
RUN /bin/bash -c "source .venv/bin/activate && uv pip compile pyproject.toml > requirements.txt && uv pip install -r requirements.txt"

# The runtime image, used to just run the code provided its virtual environment
FROM python:3.12-slim-bookworm as runtime

ENV VIRTUAL_ENV=/app/.venv \
    PATH="/app/.venv/bin:$PATH"

COPY --from=builder ${VIRTUAL_ENV} ${VIRTUAL_ENV}
COPY --from=builder /app/requirements.txt ./requirements.txt

COPY ./demo_app ./demo_app
COPY ./.streamlit ./.streamlit

CMD ["streamlit", "run", "demo_app/main.py", "--server.port", "8080"]