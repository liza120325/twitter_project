FROM python:3.12-alpine

WORKDIR /app

COPY ./app/requirements.txt /app/

RUN python -m pip install -r /app/requirements.txt

COPY ./app/database.py /app/
COPY ./app/models.py /app/
COPY ./static /app/
COPY ./app/app.py /app/

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]