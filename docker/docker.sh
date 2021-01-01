#!/usr/bin/bash

export KASSE=...

sudo docker run --network host --env="DISPLAY" --volume="$KASSE:/app/kasse" --volume="$HOME/.Xauthority:/root/.Xauthority:rw"  getraenkekasse
