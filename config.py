#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Config
BotAPIKey = 'xxx' # API Keythat you get from @BotFather
tg = xxx # Your id, you can get it by sending command /id to bot @TONTgIDBot
serverbotpath = '/home/<user>/serverbot' # User folder with this bot.
serverbotpathdb = '/home/<user>/serverbot/db' # User folder with bot database. 
srvping = '1.1.1.1' # Ping test server
traceroutetest = '1.1.1.1' # Traceroute test server

# Alarms
memloadalarm = 95 # RAM Utilization alarm starts at
pingcalarm = 50 # When ping will be more than X ms, you will get alarm.
cpuutilalarm = 97 # CPU Utilization alarm starts at
repeattimealarmnode = [5,15,25,30,60,90,120,180,320, 640, 1280, 2560, 5120, 10240, 20480, 40960, 81920] # Notify every x second about validator node down
repeattimealarmsrv = [5,15,25,30,60,90,120,180,320, 640, 1280, 2560, 5120, 10240, 20480, 40960, 81920] # Notify every x second about high CPU, RAM load and ping

cfgAlertsNotificationsNode = 1 # Node Monitoring
cfgAlertsNotificationsRam = 1 # RAM Monitoring + history
cfgAlertsNotificationsCPU = 1 # CPU Monitoring + history
cfgmonitoringnetwork = 1 # Netowrk Monitopring
cfgAlertsNotificationsping = 1 # RAM, Ping & CPU Monitopring
cfgmonitoringdiskio = 1 # Disk I/O Monitopring
