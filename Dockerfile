FROM python:3.10-slim

ADD src /app/src
ADD frontend /app/frontend

WORKDIR /app/src

RUN rm variables.ini
RUN find . -name __pycache__ | xargs rm -rf
RUN pip install -r requirements.txt

CMD ["gunicorn", "-k", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000", "main:app"]