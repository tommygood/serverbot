#!/bin/bash

apt update
apt -y install python3.7
apt -y install python3.7-dev
apt -y install traceroute
apt -y install python3-pip
apt -y install wget
update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.6 1
update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.7 2
update-alternatives --set python3 /usr/bin/python3.7
python3 -m pip install --upgrade pip
python3 -m pip install --upgrade setuptools 
python3 -m pip install --upgrade requests
python3 -m pip install --upgrade urllib3
python3 -m pip install --upgrade subprocess.run
python3 -m pip install --upgrade wheel
python3 -m pip install --upgrade psutil
python3 -m pip install --upgrade pyTelegramBotAPI
python3 -m pip install --upgrade python-dotenv
python3 -m pip install --upgrade matplotlib
python3 -m pip install --upgrade numpy
python3 -m pip install --upgrade pandas

echo "Copy files"
cp -pv /opt/tontgbot/sbot.sh /etc/init.d/tontgbot
chmod -v +x /etc/init.d/tontgbot
cp -pv /opt/tontgbot/tontgbot.service /etc/systemd/system
chmod -v +x /opt/tontgbot/bot.py
echo "Done"
echo "Download speedtest-cli"
wget -O /opt/tontgbot/speedtest-cli https://raw.githubusercontent.com/sivel/speedtest-cli/master/speedtest.py
chmod +x /opt/tontgbot/speedtest-cli
systemctl daemon-reload
echo "Start service and check status"
echo "service tontgbot start"
systemctl stop tontgbot.service
sleep 1
systemctl start tontgbot.service
sleep 3
echo "service tontgbot status"
systemctl status tontgbot.service
