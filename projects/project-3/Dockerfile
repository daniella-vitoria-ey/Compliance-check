FROM python:3.11

WORKDIR /app

COPY . .

RUN pip install --upgrade pip
RUN pip install -r requirements.txt
RUN pip install -r requirements_frontend.txt

EXPOSE 8000
EXPOSE 8501

CMD uvicorn src.api.main:app --host 0.0.0.0 --port 8000