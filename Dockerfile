FROM python:3.12.1

WORKDIR /usr/app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY ./assets ./assets
COPY ./src ./src

ENV PYTHONPATH=/usr/app/src

CMD [ "python", "src/main.py" ]
