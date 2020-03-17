FROM python:3.5
WORKDIR /code
ENV FLASK_APP app.py
ENV FLASK_RUN_HOST 0.0.0.0
ENV PYTHONUNBUFFERED 1
COPY requirements.txt requirements.txt
COPY static/react/ static/react/
RUN pip install -r requirements.txt
COPY . .
CMD ["flask", "run"]
