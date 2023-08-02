#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Bot config
BotAPIKey = '6261510862:AAEHbnjlKupEgKMSn6umI2ARTLNxwUSxnCo' # API Keythat you get from @BotFather
tg = 1697361994 # API Keythat you get from @BotFather
serverbotpath = '/home/tommygood/serverbot' # User folder with this bot.
serverbotpathdb = '/home/tommygood/serverbot/db' # User folder with bot database. 
srvping = '1.1.1.1' # Ping test server
traceroutetest = '1.1.1.1' # Traceroute test server

# Server config 
memloadalarm = 90 # RAM Utilization alarm starts at
pingcalarm = 50 # When ping will be more than X ms, you will get alarm.
cpuutilalarm = 99 # CPU Utilization alarm starts at
repeattimealarmsrv = [5,15,25,30,60,90,120,180,320, 640, 1280, 2560, 5120, 10240, 20480, 40960, 81920] # Notify every x second about high CPU, RAM load and ping
cfgAlertsNotificationsRam = 1 # RAM Monitoring + history
cfgAlertsNotificationsCPU = 1 # CPU Monitoring + history
cfgAlertsNotificationsping = 0 # RAM, Ping & CPU Monitopring
cfgmonitoringnetwork = 1 # Netowrk Monitopring
cfgmonitoringdiskio = 1 # Disk I/O Monitopring

# Docker container config
start_monitor_docker_container = 1

# Near config
nearnetwork = 'betanet' # Choose your network - betanet/testnet/mainnet/guildnet
poolname = 'xxx' # Your pool name
syncalarm = 50 # Blocks diff for alarm
blocksdiff = 1 # Blocks produced VS expected alarm
chunksdiff = 1 # Chunks produced VS expected alarm
repeattimealarmnode = [5,15,25,30,60,90,120,180,320, 640, 1280, 2560, 5120, 10240, 20480, 40960, 81920] # Notify every x second about validator node issues
cfgAlertsNotificationsNode = 0 # Node pid monitoring
cfgAlertsNotificationsSync = 0 # Sync status monitoring
cfgAlertsNotificationsBlocks = 0 # Blocks produced VS expected monitoring
cfgAlertsNotificationsChunks = 0 # Chunks produced VS expected monitoring

