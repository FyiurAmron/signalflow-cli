#!/bin/zsh
signalflow --api-endpoint https://api.us1.signalfx.com --stream-endpoint https://stream.us1.signalfx.com --timezone `readlink /etc/localtime|cut -f6- -d"/" ` $@