#!/bin/bash

#msg=$(tail -1 /etc/mosquitto/mosquitto.conf)
#IFS=' '
#read -ra a <<< "$msg"

#echo ${a[0]}
#string="#check"
#if [ "${a[0]}" != "$string" ]; then
#	sudo echo "listener ${1}" >> /etc/mosquitto/mosquitto.conf
#	sudo echo "#check" >> /etc/mosquitto/mosquitto.conf
#fi

#sudo mosquitto -c /etc/mosquitto/mosquitto.conf -p ${1} &
python3 /DOM/server_mqtt/app.py -i 59.27.74.76 -p 50210
