# TONTgBot Readme
This is telegram bot for Validator server. 

This bot can onlysend messages to your telegram id

Tested on ubuntu 18.04 & python 3.6.8 (To check your python version, put to the terminal # python3 --version )

## What this bot can do?

####  Monitoring

 1. Validator node + Automatic restart if node down
 2. CPU load 
 3. RAM load
 4. Network
 5. Time diff
 6. Wallet balance
 7. Stake monitoring + Auto stake (New!)
 8. Error log monitoring
 9. Slow log monitoring
 10. Stake send check (New!)

#### Historical data
 1. CPU Utilization
 2. RAM Load
 3. Time Diff
 4. Slow log events
 5. Disk I/O
 6. Network perfomance 
 7. Ping test 

#### Alert

 1. Validator node down
 2. High CPU Utilization
 3. High RAM load
 4. Network degradation
 5. Stake < Wallet balance
 6. Stake not send check (New!)

#### Features

##### Validator

 1. Restart validotor node
 2. Check current stake + Auto stake (New!)
 3. Update stake
 4. Check wallet balance
 5. Check current time diff + Historical data
 6. Know your adnl key
 7. Get your error log
 8. Get your slow log + Historical data
 9. Validators count
 10. Election status

##### Server
 1. Check CPU load + Historical data
 2. Check RAM load + Historical data
 3. Check disk usage
 4. Check disk i/o + Historical data
 5. Check validator ports
 6. Check server ping + Historical data
 7. Alalyze server traceroute
 8. Get top processes
 9. Check uptime
 10. Check network load + Historical data
 11. Check server network speed to different countries (Some countries may not work because speedtest servers may have problems. On Hetzner, many countries didn't work. In the future, I will add much more servers for tests)

## 07/01/2020 Update
If you get History load error, remove bot files from /tmp
sudo rm -rf /tmp/*.log
sudo rm -rf /tmp/*.png

If you get Can't fetch your balance, check for tonlabs-cli.conf.json in ton/build/utils/

## Installation in 5 simple steps (2-3 minutes, and your bot is ready)

 1. Create your personal telegram bot and get Api Token. [Instruction](https://docs.microsoft.com/en-us/azure/bot-service/bot-service-channel-connect-telegram?view=azure-bot-service-4.0)
 2. Send to your new bot command /start and go to the next step
 3. Run command below
```sh
$ cd $HOME && git clone -v https://github.com/anvme/TONTgBot.git tontgbot && cd ./tontgbot && chmod +x ./installsbot.sh
```
 4. Open ./config.py in any editor and change values in TONTgBot from *Edit starts here* till *Edit ends here*. If you dont know your id(tg value), Just send message to @TONTgIDBot in telegram. Then open ./sbot.sh and put user folder at lines 14-15. Open ./tontgbot.service and put user&group at lines 7-8
 5. Run 
 ```sh
$ /bin/bash ./installsbot.sh
```

## Available languages *Yes, with google translate
Change languages=['en'] in bot.py to language, what you need
  ```sh
lang_translations = gettext.translation('base', localedir='/opt/tontgbot/locales', languages=['en'])
```

Language - code
* English - en
* Español - es
* Français - fr
* Dansk - da
* Nederlands - nl
* हिंदी - hi
* Italiano - it
* Polski - pl
* Português - pt
* Suomi - fi
* Svenska - sv
* Türkçe - tr
* Ελληνικά - el
* Русский - ru
* Українська - uk
* 日本語 - ja

And restart your bot
  ```sh
$ systemctl restart tontgbot.service 
```

## Restart validator node
If you will restart validator node from bot, tontgbot service will be it's parrent, and if you stop tontgbot, you will need to run node again from terminal. I will think about deattaching run node pid from tontgbot service after restart

## What to do if something not working?
Find in bot.py telebot.logger.setLevel(logging.ERROR) and change ERROR to DEBUG, restart tontgbot service and execute
  ```sh
$ journalctl -e -u tontgbot > /opt/tontgbot/servicelog.log
```
Then sent this log to my telegram @anvme


## Donate

Free TON 0:7ccbe4a3bfac4afd44b20d8042925af13a9fc5aeaec1d600dadd70798f64d9ad
