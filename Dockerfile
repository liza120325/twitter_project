FROM python:3.12-alpine

WORKDIR /fastapi_app/my_app

COPY ./my_app/requirements.txt /fastapi_app/my_app

RUN python -m pip install -r /fastapi_app/my_app/requirements.txt

COPY ./my_app/database.py /fastapi_app/my_app/
COPY ./my_app/schemas.py /fastapi_app/my_app/
COPY ./my_app/app.py /fastapi_app/my_app/
COPY ./my_app/crud.py /fastapi_app/my_app/
COPY ./test/ /fastapi_app/my_app/

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]