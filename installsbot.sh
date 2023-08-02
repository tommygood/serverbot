#!/bin/bash

sudo apt update
sudo apt -y install traceroute
sudo apt -y install python3-pip
sudo apt -y install wget
pip3 install --upgrade psutil
pip3 install "pyTelegramBotAPI==4.2.0" --user
pip3 install --upgrade python-dotenv
pip3 install --upgrade matplotlib
pip3 install --upgrade numpy
pip3 install --upgrade pandas

sudo usermod -aG docker $USER && newgrp docker
echo "Prepare configs"
sed -i "s/<user>/"$USER"/g" serverbot.service sbot.sh config.py
echo "alias botstop='sudo systemctl stop serverbot'" >> /home/$USER/.bash_aliases
echo "alias botstart='sudo systemctl start serverbot'" >> /home/$USER/.bash_aliases
echo "alias botstatus='sudo systemctl status serverbot'" >> /home/$USER/.bash_aliases
echo "alias botstop='sudo systemctl stop serverbot'" >> /home/$USER/.zshrc
echo "alias botstart='sudo systemctl start serverbot'" >> /home/$USER/.zshrc
echo "alias botstatus='sudo systemctl status serverbot'" >> /home/$USER/.zshrc


echo "Copy files"
sudo cp -pv ./sbot.sh /etc/init.d/serverbot
chmod -v +x /etc/init.d/serverbot
sudo cp -pv ./serverbot.service /etc/systemd/system
chmod -v +x ./bot.py
echo "Done"
echo "Download speedtest-cli"
wget -O ./speedtest-cli https://raw.githubusercontent.com/sivel/speedtest-cli/master/speedtest.py
chmod +x ./speedtest-cli
sudo systemctl daemon-reload
echo "Start service and check status"
echo "service serverbot start"
sudo systemctl stop serverbot.service
sleep 1
sudo systemctl start serverbot.service
sleep 2
sudo systemctl enable serverbot.service
echo "service serverbot status"
systemctl status serverbot.service
