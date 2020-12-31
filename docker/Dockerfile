# Build image
FROM python:3.8.7-slim as builder

RUN apt-get update \ 
&& apt-get install -y dpkg-dev build-essential libjpeg-dev libtiff-dev libsdl1.2-dev \
libnotify-dev freeglut3 freeglut3-dev libghc-gtk3-dev libwxgtk3.0-gtk3-dev \
&& apt-get clean

COPY requirements.txt /app/requirements.txt

WORKDIR app

RUN pip install -r requirements.txt

COPY . /app

# Production image
FROM python:3.8.7-slim as app

RUN apt-get update && apt-get install -y --no-install-recommends git libgtk-3-0 libxxf86vm1 libsm6 libnotify4 libsdl1.2debian && apt-get clean && rm -rf /var/lib/apt/lists/*

COPY --from=builder /root/.cache /root/.cache
COPY --from=builder /app/requirements.txt /app/requirements.txt

WORKDIR app

RUN pip install -r requirements.txt 

COPY --from=builder /app/getraenkeKasse.py /app/getraenkeKasse.py
COPY --from=builder /app/functions.py /app/functions.py
COPY --from=builder /app/src /app/src

ENTRYPOINT [ "python3", "./getraenkeKasse.py" ]
