FROM python:3.10-slim-bullseye

ENV HOST=0.0.0.0

ENV LISTEN_PORT 8080

EXPOSE 8080

RUN apt-get update && apt-get install -y git

COPY ./requirements.txt /app/requirements.txt
COPY ./emails_config.yaml /app/emails_config.yaml

RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt

WORKDIR app/

COPY ./demo_app /app/demo_app
COPY ./.streamlit /app/.streamlit

CMD ["streamlit", "run", "demo_app/main.py", "--server.port", "8080"]
