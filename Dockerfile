FROM python:3.6-stretch
ENV ENV /root/.profile
ENV PYTHONUNBUFFERED 1
RUN apt-get update && apt-get install -y vim && pip install --upgrade pip
WORKDIR /app
COPY requirements.txt /app
RUN pip3 install  --no-cache-dir -r requirements.txt
RUN python -c "import nltk; nltk.download('brown')"
ADD . /app
RUN mkdir -p /app/project_secrets

ARG PORT=5001
EXPOSE $PORT
ENV FLASK_PORT $PORT

CMD ["/app/run_app.sh"]
