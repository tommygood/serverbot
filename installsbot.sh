#!/bin/bash

apt update
#apt -y install python3.7
#apt -y install python3.7-dev
apt -y install traceroute
apt -y install python3-pip
apt -y install wget
#update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.6 1
#update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.7 2
#update-alternatives --set python3 /usr/bin/python3.6
#ln -s /usr/lib/python3/dist-packages/apt_pkg.cpython-36m-x86_64-linux-gnu.so /usr/lib/python3/dist-packages/apt_pkg.so
#pip3 install --upgrade pip
#pip3 install --upgrade setuptools 
#pip3 install --upgrade requests
#pip3 install --upgrade urllib3
#pip3 install --upgrade subprocess.run
#pip3 install --upgrade wheel
pip3 install --upgrade psutil
pip3 install --upgrade pyTelegramBotAPI
pip3 install --upgrade python-dotenv
pip3 install --upgrade matplotlib
pip3 install --upgrade numpy
pip3 install --upgrade pandas

echo "Copy files"
cp -pv ./sbot.sh /etc/init.d/tontgbot
chmod -v +x /etc/init.d/tontgbot
cp -pv ./tontgbot.service /etc/systemd/system
chmod -v +x ./bot.py
echo "Done"
echo "Download speedtest-cli"
wget -O ./speedtest-cli https://raw.githubusercontent.com/sivel/speedtest-cli/master/speedtest.py
chmod +x ./speedtest-cli
systemctl daemon-reload
echo "Start service and check status"
echo "service tontgbot start"
systemctl stop tontgbot.service
sleep 1
systemctl start tontgbot.service
sleep 3
echo "service tontgbot status"
systemctl status tontgbot.service
