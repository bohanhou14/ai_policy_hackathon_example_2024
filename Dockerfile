# 1 
FROM python:3.7

COPY requirements.txt /

RUN pip3 install -r /requirements.txt

# 2
RUN pip install Flask gunicorn

COPY app.py .

CMD ["gunicorn"  , "-b", "0.0.0.0:8888", "app:app"]