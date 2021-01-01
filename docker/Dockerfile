# Build image
FROM python:3.8.7-slim as builder

RUN apt-get update \
&& apt-get install -y dpkg-dev build-essential libjpeg-dev libtiff-dev libsdl1.2-dev \
libnotify-dev freeglut3 freeglut3-dev libghc-gtk3-dev libwxgtk3.0-gtk3-dev \
&& apt-get clean

WORKDIR /wheels

RUN pip install -U pip \
&& pip wheel wxPython==4.1.1

# Production image
FROM python:3.8.7-slim as app

RUN apt-get update \
&& apt-get install -y --no-install-recommends git libgtk-3-0 libxxf86vm1 libsm6 libnotify4  \
libsdl1.2debian openssh-client \
&& apt-get clean \
&& rm -rf /var/lib/apt/lists/*

COPY --from=builder /wheels /wheels
COPY requirements.txt /app/barcodeRaspi/requirements.txt

WORKDIR /app

RUN pip install -U pip \
&& pip install -r barcodeRaspi/requirements.txt -f /wheels \
&& rm -rf /wheels && rm -rf /root/.cache/pip

COPY getraenkeKasse.py functions.py /app/barcodeRaspi/
COPY src /app/barcodeRaspi/src

ENTRYPOINT [ "python3", "./barcodeRaspi/getraenkeKasse.py" ]
