#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os, sys
import config
import time
import datetime
from datetime import datetime as dt
import subprocess
import tty
import pty
import psutil
import numpy as np
import pandas as pd
import logging
import threading
import re
import telebot
from telebot import types
from telebot import util
from dotenv import load_dotenv
import matplotlib
import matplotlib.dates as mdates
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import gettext
import requests
import json
from subprocess import call, PIPE, run

# API Token
bot = telebot.TeleBot(config.BotAPIKey)
# /API Token

# Log
logger = telebot.logger
telebot.logger.setLevel(logging.ERROR) # Outputs Error messages to console.
# /Log

#hostn = os.uname()[1]
#hostn = (hostn[0:hostn.find('.')])

#set NEAR rpc url
if config.nearnetwork == 'guildnet':
    rpcurl=("https://rpc.openshards.io")
else:
    rpcurl=("https://rpc." + config.nearnetwork + ".near.org")
# /set NEAR rpc url

#set NEAR pid
if config.nearnetwork == 'mainnet':
    nearpid="neard"
else:
    nearpid="near"
#/set NEAR pid

#set NEAR logs
if config.nearnetwork == 'mainnet':
    nearlogsreq="journalctl -u neard.service -n 5"
else:
    nearlogsreq="tail -n 5 ~/.nearup/logs/" + config.nearnetwork + ".log"
#/set NEAR logs

# Menu vars
lt_cpu = ("CPU")
lt_cpu = "\U0001F39B " + lt_cpu
lt_ram = ("RAM")
lt_ram = "\U0001F39A " + lt_ram
lt_disks = ("Disk usage")
lt_disks = "\U0001F4BE " + lt_disks
lt_linuxtools = ("Linux tools")
lt_linuxtools = "\U0001F9F0 " + lt_linuxtools
#----
lt_ping = ("Ping test")
lt_ping =  "\U0001F3D3 " + lt_ping
lt_traceroute = ("Traceroute test")
lt_traceroute =  "\U0001F9ED " + lt_traceroute
lt_topproc = ("Top processes")
lt_topproc =  "\U0001F51D " + lt_topproc
#lt_ssvalid = ("Port check")
#lt_ssvalid =  "\U0001F442\U0001F3FC " + lt_ssvalid
lt_spdtst = ("Network speed test")
lt_spdtst =  "\U0001F4E1 " + lt_spdtst
lt_currntwrkload = ("Current network load")
lt_currntwrkload =  "\U0001F51B " + lt_currntwrkload
lt_currntdiskload = ("Current disk i/o")
lt_currntdiskload = "\U0001F4BD " + lt_currntdiskload
lt_starttime = ("Uptime")
lt_starttime = "\U0001F7E2 " + lt_starttime
lt_mainmenu = ("Main menu")
lt_mainmenu =  "\U0001F3E1 " + lt_mainmenu
lt_docker_container = ("Docker Container")
lt_docker_container = "\U00002b50" + lt_docker_container
lt_nearpool = ("My pool info")
lt_nearpool = "\u2139 " + lt_nearpool
lt_nearlogs = ("Near logs")
lt_nearlogs = "\U0001F4CB" + lt_nearlogs
lt_nearcurrent = ("Current")
lt_nearcurrent = "\u23fa " + lt_nearcurrent
lt_nearproposals = ("Proposals")
lt_nearproposals = "\u23e9 " + lt_nearproposals
lt_nearnext = ("Next")
lt_nearnext = "\u23e9 " + lt_nearnext

## /Menu vars

# Default markup
markup = types.ReplyKeyboardMarkup()
cpu = types.KeyboardButton(lt_cpu)
ram = types.KeyboardButton(lt_ram)
disks = types.KeyboardButton(lt_disks)
currntdiskload = types.KeyboardButton(lt_currntdiskload)
neartools = types.KeyboardButton(lt_docker_container)
linuxtools = types.KeyboardButton(lt_linuxtools)
markup.row(cpu,ram,disks)
markup.row(currntdiskload,neartools,linuxtools)

# Near markup
markupnear = types.ReplyKeyboardMarkup()
nearpool = types.KeyboardButton(lt_nearpool)
nearlogs = types.KeyboardButton(lt_nearlogs)
mainmenu = types.KeyboardButton(lt_mainmenu)
nearcurrent = types.KeyboardButton(lt_nearcurrent)
nearproposals = types.KeyboardButton(lt_nearproposals)
nearnext = types.KeyboardButton(lt_nearnext)
markupnear.row(nearcurrent,nearproposals,nearnext)
markupnear.row(nearpool,nearlogs,mainmenu)

# Linux markup
markuplinux = types.ReplyKeyboardMarkup()
ping = types.KeyboardButton(lt_ping)
traceroute = types.KeyboardButton(lt_traceroute)
topproc = types.KeyboardButton(lt_topproc)
starttime = types.KeyboardButton(lt_starttime)
spdtst = types.KeyboardButton(lt_spdtst)
currntwrkload = types.KeyboardButton(lt_currntwrkload)
currntdiskload = types.KeyboardButton(lt_currntdiskload)
mainmenu = types.KeyboardButton(lt_mainmenu)
markuplinux.row(ping,traceroute)
markuplinux.row(topproc,starttime,spdtst)
markuplinux.row(currntwrkload,currntdiskload,mainmenu)

# Get id for tg value
@bot.message_handler(commands=["id"])
def get_id(i):
    id = i.from_user.id
    msg = "Id: " + str(id)
    bot.reply_to(i, msg)
# /Get id for tg value

# Start
@bot.message_handler(commands=["start", "help"])
def send_welcome(message):
  if message.from_user.id == config.tg:
    bot.send_message(config.tg, ("Hi, I'm here to make your life a little bit easier ;) "),reply_markup=markup)
  else:
    pass
# /Start

# InlineKeyboards
# Docker Container
container_load_hist = types.InlineKeyboardMarkup()

container_load_hist.row(
types.InlineKeyboardButton(text=("3h"), callback_data="container_load_hist_3h"),
types.InlineKeyboardButton(text=("6h"), callback_data="container_load_hist_6h"),
types.InlineKeyboardButton(text=("12h"), callback_data="container_load_hist_12h"),
types.InlineKeyboardButton(text=("24h"), callback_data="container_load_hist_24h"),
types.InlineKeyboardButton(text=("3d"), callback_data="container_load_hist_3d"),
types.InlineKeyboardButton(text=("10d"), callback_data="container_load_hist_10d"),
types.InlineKeyboardButton(text=("30d"), callback_data="container_load_hist_30d"))
# Docker Container
#CPU
cpuloadhist = types.InlineKeyboardMarkup()
cpuloadhist.row(
types.InlineKeyboardButton(text=("30m"), callback_data="cpuhist_30m"),
types.InlineKeyboardButton(text=("1h"), callback_data="cpuhist_1h"),
types.InlineKeyboardButton(text=("3h"), callback_data="cpuhist_3h"),
types.InlineKeyboardButton(text=("6h"), callback_data="cpuhist_6h"),
types.InlineKeyboardButton(text=("12h"), callback_data="cpuhist_12h"),
types.InlineKeyboardButton(text=("1d"), callback_data="cpuhist_1d"),
types.InlineKeyboardButton(text=("+"), callback_data="cpuhistmore"))

cpuhistmore = types.InlineKeyboardMarkup()
cpuhistmore.row(
types.InlineKeyboardButton(text="\U00002190", callback_data="cpuloadhist"),
types.InlineKeyboardButton(text=("3d"), callback_data="cpuhist_3d"),
types.InlineKeyboardButton(text=("5d"), callback_data="cpuhist_5d"),
types.InlineKeyboardButton(text=("7d"), callback_data="cpuhist_7d"),
types.InlineKeyboardButton(text=("14d"), callback_data="cpuhist_14d"),
types.InlineKeyboardButton(text=("21d"), callback_data="cpuhist_21d"),
types.InlineKeyboardButton(text=("30d"), callback_data="cpuhist_30d"))
#CPU

#RAM
ramloadhist = types.InlineKeyboardMarkup()
ramloadhist.row(
types.InlineKeyboardButton(text=("30m"), callback_data="ramhist_30m"),
types.InlineKeyboardButton(text=("1h"), callback_data="ramhist_1h"),
types.InlineKeyboardButton(text=("3h"), callback_data="ramhist_3h"),
types.InlineKeyboardButton(text=("6h"), callback_data="ramhist_6h"),
types.InlineKeyboardButton(text=("12h"), callback_data="ramhist_12h"),
types.InlineKeyboardButton(text=("1d"), callback_data="ramhist_1d"),
types.InlineKeyboardButton(text=("+"), callback_data="ramhistmore"))

ramhistmore = types.InlineKeyboardMarkup()
ramhistmore.row(
types.InlineKeyboardButton(text=("\U00002190"), callback_data="ramloadhist"),
types.InlineKeyboardButton(text=("3d"), callback_data="ramhist_3d"),
types.InlineKeyboardButton(text=("5d"), callback_data="ramhist_5d"),
types.InlineKeyboardButton(text=("7d"), callback_data="ramhist_7d"),
types.InlineKeyboardButton(text=("14d"), callback_data="ramhist_14d"),
types.InlineKeyboardButton(text=("21d"), callback_data="ramhist_21d"),
types.InlineKeyboardButton(text=("30d"), callback_data="ramhist_30d"))
#RAM

#PING
pingcheckhist = types.InlineKeyboardMarkup()
pingcheckhist.row(
types.InlineKeyboardButton(text=("30m"), callback_data="pinghist_30m"),
types.InlineKeyboardButton(text=("1h"), callback_data="pinghist_1h"),
types.InlineKeyboardButton(text=("3h"), callback_data="pinghist_3h"),
types.InlineKeyboardButton(text=("6h"), callback_data="pinghist_6h"),
types.InlineKeyboardButton(text=("12h"), callback_data="pinghist_12h"),
types.InlineKeyboardButton(text=("1d"), callback_data="pinghist_1d"),
types.InlineKeyboardButton(text=("+"), callback_data="pinghistmore"))

pinghistmore = types.InlineKeyboardMarkup()
pinghistmore.row(
types.InlineKeyboardButton(text=("\U00002190"), callback_data="pingcheckhist"),
types.InlineKeyboardButton(text=("3d"), callback_data="pinghist_3d"),
types.InlineKeyboardButton(text=("5d"), callback_data="pinghist_5d"),
types.InlineKeyboardButton(text=("7d"), callback_data="pinghist_7d"),
types.InlineKeyboardButton(text=("14d"), callback_data="pinghist_14d"),
types.InlineKeyboardButton(text=("21d"), callback_data="pinghist_21d"),
types.InlineKeyboardButton(text=("30d"), callback_data="pinghist_30d"))
#PING

# Network
networkcheckhist = types.InlineKeyboardMarkup()
networkcheckhist.row(
types.InlineKeyboardButton(text=("30m"), callback_data="networkhist_30m"),
types.InlineKeyboardButton(text=("1h"), callback_data="networkhist_1h"),
types.InlineKeyboardButton(text=("3h"), callback_data="networkhist_3h"),
types.InlineKeyboardButton(text=("6h"), callback_data="networkhist_6h"),
types.InlineKeyboardButton(text=("12h"), callback_data="networkhist_12h"),
types.InlineKeyboardButton(text=("1d"), callback_data="networkhist_1d"),
types.InlineKeyboardButton(text=("+"), callback_data="networkhistmore"))

networkhistmore = types.InlineKeyboardMarkup()
networkhistmore.row(
types.InlineKeyboardButton(text=("\U00002190"), callback_data="networkcheckhist"),
types.InlineKeyboardButton(text=("3d"), callback_data="networkhist_3d"),
types.InlineKeyboardButton(text=("5d"), callback_data="networkhist_5d"),
types.InlineKeyboardButton(text=("7d"), callback_data="networkhist_7d"),
types.InlineKeyboardButton(text=("14d"), callback_data="networkhist_14d"),
types.InlineKeyboardButton(text=("21d"), callback_data="networkhist_21d"),
types.InlineKeyboardButton(text=("30d"), callback_data="networkhist_30d"))
# Network

# Disk io
diskiocheckhist = types.InlineKeyboardMarkup()
diskiocheckhist.row(
types.InlineKeyboardButton(text=("30m"), callback_data="diskiohist_30m"),
types.InlineKeyboardButton(text=("1h"), callback_data="diskiohist_1h"),
types.InlineKeyboardButton(text=("3h"), callback_data="diskiohist_3h"),
types.InlineKeyboardButton(text=("6h"), callback_data="diskiohist_6h"),
types.InlineKeyboardButton(text=("12h"), callback_data="diskiohist_12h"),
types.InlineKeyboardButton(text=("1d"), callback_data="diskiohist_1d"),
types.InlineKeyboardButton(text=("+"), callback_data="diskiohistmore"))

diskiohistmore = types.InlineKeyboardMarkup()
diskiohistmore.row(
types.InlineKeyboardButton(text=("\U00002190"), callback_data="diskiocheckhist"),
types.InlineKeyboardButton(text=("3d"), callback_data="diskiohist_3d"),
types.InlineKeyboardButton(text=("5d"), callback_data="diskiohist_5d"),
types.InlineKeyboardButton(text=("7d"), callback_data="diskiohist_7d"),
types.InlineKeyboardButton(text=("14d"), callback_data="diskiohist_14d"),
types.InlineKeyboardButton(text=("21d"), callback_data="diskiohist_21d"),
types.InlineKeyboardButton(text=("30d"), callback_data="diskiohist_30d"))
# Disk io

# History load welcome
def historyget(f,t,lbl,ptitle,poutf,rm):
  try:
    bot.send_chat_action(config.tg, "upload_photo")
    df = pd.read_csv(os.path.join(config.serverbotpath, f), sep=";", encoding="utf-8", header=None)
    df.iloc[:,0] = pd.to_datetime(df.iloc[:,0], unit='s')
    period = df.iloc[:,0] > df.iloc[:,0].max() - pd.Timedelta(minutes=t)
    x = df.iloc[:,0].loc[period]
    y = df.iloc[:,1].loc[period]
    plt.figure(figsize=[12, 9], dpi=100)
    plt.xlabel('Time')
    plt.ylabel(lbl)
    plt.title(ptitle)
    plt.yticks(np.arange(0, 100, step=5))
    plt.grid(True)
    plt.ylim(top=100)
    plt.plot(x, y)
    plt.gcf().autofmt_xdate()
    plt.tight_layout()
    plt.savefig(poutf)
    plt.close()
    load = open(poutf, 'rb')
    bot.send_photo(config.tg, load, reply_markup=rm)
  except:
    bot.send_message(config.tg, text = ("History load error"))
# History load welcome

# History load welcome Time Diff
def historygettd(f,t,lbl,ptitle,poutf,rm):
  try:
    bot.send_chat_action(config.tg, "upload_photo")
    df = pd.read_csv(os.path.join(config.serverbotpath, f), sep=";", encoding="utf-8", header=None)
    df.iloc[:,0] = pd.to_datetime(df.iloc[:,0], unit='s')
    period = (df.iloc[:,0] > df.iloc[:,0].max() - pd.Timedelta(minutes=t)) & (df.iloc[:,1] < 0)
    x = df.iloc[:,0].loc[period]
    y = df.iloc[:,1].loc[period]
    plt.figure(figsize=[12, 9], dpi=100)
    plt.xlabel('Time')
    plt.ylabel(lbl)
    plt.title(ptitle)
    plt.grid(True)
    plt.plot(x, y)
    plt.gcf().autofmt_xdate()
    plt.tight_layout()
    plt.savefig(poutf)
    plt.close()
    load = open(poutf, 'rb')
    bot.send_photo(config.tg, load, reply_markup=rm)
  except:
    bot.send_message(config.tg, text = ("History load error"))
# History load welcome Time Diff 

# History load welcome Ping
def historygetping(f,t,lbl,ptitle,poutf,rm):
  try:
    bot.send_chat_action(config.tg, "upload_photo")
    df = pd.read_csv(os.path.join(config.serverbotpath, f), sep=";", encoding="utf-8", header=None)
    df.iloc[:,0] = pd.to_datetime(df.iloc[:,0], unit='s')
    period = df.iloc[:,0] > df.iloc[:,0].max() - pd.Timedelta(minutes=t)
    x = df.iloc[:,0].loc[period]
    y = df.iloc[:,1].loc[period]
    plt.figure(figsize=[12, 9], dpi=100)
    plt.xlabel('Time')
    plt.ylabel(lbl)
    plt.title(ptitle)
    plt.grid(True)
    plt.plot(x, y)
    plt.gcf().autofmt_xdate()
    plt.tight_layout()
    plt.savefig(poutf)
    plt.close()
    load = open(poutf, 'rb')
    bot.send_photo(config.tg, load, reply_markup=rm)
  except:
    bot.send_message(config.tg, text = ("Ping History load error"))
# History load welcome Ping

# History load welcome Network Bandwidth
def historygetnb(f,t,lbl,dptitle,uptitle,poutf,rm):
  try:
    bot.send_chat_action(config.tg, "upload_photo")
    df = pd.read_csv(os.path.join(config.serverbotpath, f), sep=";", encoding="utf-8", header=None)
    df.iloc[:,0] = pd.to_datetime(df.iloc[:,0], unit='s')
    df.iloc[:,1] = df.iloc[:,1]/1024/1024*8
    df.iloc[:,2] = df.iloc[:,2]/1024/1024*8
    period = df.iloc[:,0] > df.iloc[:,0].max() - pd.Timedelta(hours=t)
    x = df.iloc[:,0].loc[period]
    y1 = df.iloc[:,1].loc[period]
    y2 = df.iloc[:,2].loc[period]
    plt.figure(figsize=[12, 9], dpi=100)
    plt.subplot(2, 1, 1)
    plt.xlabel('Time')
    plt.ylabel(lbl)
    plt.title(dptitle)
    plt.grid(True)
    plt.plot(x, y1)
    plt.subplot(2, 1, 2)
    plt.xlabel('Time')
    plt.ylabel(lbl)
    plt.title(uptitle)
    plt.grid(True)
    plt.plot(x, y2)
    plt.gcf().autofmt_xdate()
    plt.tight_layout()
    plt.savefig(poutf)
    plt.close()
    load = open(poutf, 'rb')
    bot.send_photo(config.tg, load, reply_markup=rm)
  except:
    bot.send_message(config.tg, text = ("Ping History load error"))
# History load welcome Network Bandwidth

# History load welcome Disk I/O
def historygetdio(f,t,lbl,rptitle,wptitle,poutf,rm):
  try:
    bot.send_chat_action(config.tg, "upload_photo")
    df = pd.read_csv(os.path.join(config.serverbotpath, f), sep=";", encoding="utf-8", header=None)
    df.iloc[:,0] = pd.to_datetime(df.iloc[:,0], unit='s')
    df.iloc[:,1] = df.iloc[:,1]/1024/1024
    df.iloc[:,2] = df.iloc[:,2]/1024/1024
    period = df.iloc[:,0] > df.iloc[:,0].max() - pd.Timedelta(hours=t)
    x = df.iloc[:,0].loc[period]
    y1 = df.iloc[:,1].loc[period]
    y2 = df.iloc[:,2].loc[period]
    plt.figure(figsize=[12, 9], dpi=100)
    plt.subplot(2, 1, 1)
    plt.xlabel('Time')
    plt.ylabel(lbl)
    plt.title(rptitle)
    plt.grid(True)
    plt.plot(x, y1)
    plt.subplot(2, 1, 2)
    plt.xlabel('Time')
    plt.ylabel(lbl)
    plt.title(wptitle)
    plt.grid(True)
    plt.plot(x, y2)
    plt.gcf().autofmt_xdate()
    plt.tight_layout()
    plt.savefig(poutf)
    plt.close()
    load = open(poutf, 'rb')
    bot.send_photo(config.tg, load, reply_markup=rm)
  except:
    bot.send_message(config.tg, text = ("Disk I/O Utilization history load error"))
# History load welcome Disk I/O

# History load welcome
def historygetslowlog(f,t,lbl,ptitle,poutf,rm):
  try:
    bot.send_chat_action(config.tg, "upload_photo")
    df = pd.read_csv(os.path.join(config.serverbotpath, f), sep=";", encoding="utf-8", header=None)
    df.iloc[:,0] = pd.to_datetime(df.iloc[:,0], unit='s')
    period = df.iloc[:,0] > df.iloc[:,0].max() - pd.Timedelta(minutes=t)
    x = df.iloc[:,0].loc[period]
    y = df.iloc[:,2].loc[period]
    plt.figure(figsize=[12, 9], dpi=100)
    plt.xlabel('Time')
    plt.ylabel(lbl)
    plt.title(ptitle)
    plt.grid(True)
    plt.plot(x, y)
    plt.gcf().autofmt_xdate()
    plt.tight_layout()
    plt.savefig(poutf)
    plt.close()
    load = open(poutf, 'rb')
    bot.send_photo(config.tg, load, reply_markup=rm)
  except:
    bot.send_message(config.tg, text = ("History load error"))
#/History load welcome

# CPU
@bot.message_handler(func=lambda message: message.text == lt_cpu)
def command_cpu(message):
  if message.from_user.id == config.tg:
    try:
      sysload = str(psutil.getloadavg())
      cpuutil = str(psutil.cpu_percent(percpu=True))
      cpu = ("*System load (1,5,15 min):* _") + sysload + ("_\n*CPU utilization %:* _") + cpuutil + "_"
      bot.send_message(config.tg, text=cpu, parse_mode="Markdown")
      historyget("db/cpuload.dat",30,("Utilization"),("CPU Utilization"),"/tmp/cpuload.png",cpuloadhist)
    except:
      bot.send_message(config.tg, text=("Can't get CPU info"))
  else:
    pass
# /CPU

# RAM
@bot.message_handler(func=lambda message: message.text == lt_ram)
def command_ram(message):
  if message.from_user.id == config.tg:
    try:
      ram = ("*RAM, Gb.*\n_Total: ") + str(subprocess.check_output(["free -mh | grep Mem | awk '{print $2}'"], shell = True,encoding='utf-8')) + ("Available: ") + str(subprocess.check_output(["free -mh | grep Mem | awk '{print $7}'"], shell = True,encoding='utf-8')) + ("Used: ") + str(subprocess.check_output(["free -mh | grep Mem | awk '{print $3}'"], shell = True,encoding='utf-8')) + "_"
      swap = ("*SWAP, Gb.*\n_Total: ") + str(subprocess.check_output(["free -mh | grep Swap | awk '{print $2}'"], shell = True,encoding='utf-8')) + ("Available: ") + str(subprocess.check_output(["free -mh | grep Swap | awk '{print $7}'"], shell = True,encoding='utf-8')) + ("Used: ") + str(subprocess.check_output(["free -mh | grep Swap | awk '{print $3}'"], shell = True,encoding='utf-8')) + "_"
      bot.send_message(config.tg, text=ram + swap, parse_mode="Markdown")
      historyget("db/ramload.dat",30,("Utilization"),("RAM Utilization"),"/tmp/ramload.png",ramloadhist)
    except:
      bot.send_message(config.tg, text=("Can't get RAM info"), parse_mode="Markdown")
  else:
    pass
# /RAM

# Disk
@bot.message_handler(func=lambda message: message.text == lt_disks)
def command_disk(message):
  if message.from_user.id == config.tg:
    try:
      disk = str(subprocess.check_output(["df -h -t ext4"], shell = True,encoding='utf-8'))
      bot.send_message(config.tg, text=disk, parse_mode="Markdown", reply_markup=markup)
    except:
      bot.send_message(config.tg, text=("Can't get disk info"), parse_mode="Markdown", reply_markup=markup)
  else:
    pass
# /Disk

# Server Info tools
#######################################################

@bot.callback_query_handler(func = lambda call: True)
def inlinekeyboards(call):
  if call.from_user.id == config.tg:
  # CPU graph
    if call.data == "cpuloadhist":
      bot.edit_message_reply_markup(config.tg, message_id=call.message.message_id, reply_markup=cpuloadhist)
    if call.data == "cpuhistmore":
      bot.edit_message_reply_markup(config.tg, message_id=call.message.message_id, reply_markup=cpuhistmore)
    if call.data == "cpuhist_30m":
      try:
        df = pd.read_csv(os.path.join(config.serverbotpathdb, "cpuload.dat"), sep=";", encoding="utf-8", header=None)
        df.iloc[:,0] = pd.to_datetime(df.iloc[:,0], unit='s')
        period = df.iloc[:,0] > df.iloc[:,0].max() - pd.Timedelta(minutes=30)
        x = df.iloc[:,0].loc[period]
        y = df.iloc[:,1].loc[period]
        plt.figure(figsize=[12, 9], dpi=100)
        plt.xlabel('Time')
        plt.ylabel('Utilization')
        plt.title('CPU Utilization')
        plt.yticks(np.arange(0, 100, step=5))
        plt.grid(True)
        plt.ylim(top=100)
        plt.plot(x, y)
        plt.gcf().autofmt_xdate()
        plt.tight_layout()
        plt.savefig('/tmp/cpuload.png')
        plt.close()
        cpuload_1h = open('/tmp/cpuload.png', 'rb')
        bot.edit_message_media(media=types.InputMedia(type='photo', media=cpuload_1h),chat_id=call.message.chat.id,message_id=call.message.message_id, reply_markup=cpuloadhist)
      except:
        bot.send_message(config.tg, text = ("CPU Utilization history load error"))
    if call.data == "cpuhist_1h":
      try:
        df = pd.read_csv(os.path.join(config.serverbotpathdb, "cpuload.dat"), sep=";", encoding="utf-8", header=None)
        df.iloc[:,0] = pd.to_datetime(df.iloc[:,0], unit='s')
        period = df.iloc[:,0] > df.iloc[:,0].max() - pd.Timedelta(hours=1)
        x = df.iloc[:,0].loc[period]
        y = df.iloc[:,1].loc[period]
        plt.figure(figsize=[15, 9], dpi=100)
        plt.xlabel('Time')
        plt.ylabel('Utilization')
        plt.title('CPU Utilization')
        plt.yticks(np.arange(0, 100, step=5))
        plt.grid(True)
        plt.ylim(top=100)
        plt.plot(x, y)
        plt.gcf().autofmt_xdate()
        plt.tight_layout()
        plt.savefig('/tmp/cpuload.png')
        plt.close()
        cpuload_1h = open('/tmp/cpuload.png', 'rb')
        bot.edit_message_media(media=types.InputMedia(type='photo', media=cpuload_1h),chat_id=call.message.chat.id,message_id=call.message.message_id, reply_markup=cpuloadhist)
      except:
        bot.send_message(config.tg, text = ("CPU Utilization history load error"))
    if call.data == "cpuhist_3h":
      try:
        df = pd.read_csv(os.path.join(config.serverbotpathdb, "cpuload.dat"), sep=";", encoding="utf-8", header=None)
        df.iloc[:,0] = pd.to_datetime(df.iloc[:,0], unit='s')
        period = df.iloc[:,0] > df.iloc[:,0].max() - pd.Timedelta(hours=3)
        x = df.iloc[:,0].loc[period]
        y = df.iloc[:,1].loc[period]
        plt.figure(figsize=[20, 9], dpi=100)
        plt.xlabel('Time')
        plt.ylabel('Utilization')
        plt.title('CPU Utilization')
        plt.yticks(np.arange(0, 100, step=5))
        plt.grid(True)
        plt.ylim(top=100)
        plt.plot(x, y)
        plt.gcf().autofmt_xdate()
        plt.tight_layout()
        plt.savefig('/tmp/cpuload.png')
        plt.close()
        cpuload_3h = open('/tmp/cpuload.png', 'rb')
        bot.edit_message_media(media=types.InputMedia(type='photo', media=cpuload_3h),chat_id=call.message.chat.id,message_id=call.message.message_id, reply_markup=cpuloadhist)
      except:
        bot.send_message(config.tg, text = ("CPU Utilization history load error"))
    if call.data == "cpuhist_6h":
      try:
        df = pd.read_csv(os.path.join(config.serverbotpathdb, "cpuload.dat"), sep=";", encoding="utf-8", header=None)
        df.iloc[:,0] = pd.to_datetime(df.iloc[:,0], unit='s')
        period = df.iloc[:,0] > df.iloc[:,0].max() - pd.Timedelta(hours=6)
        x = df.iloc[:,0].loc[period]
        y = df.iloc[:,1].loc[period]
        plt.figure(figsize=[20, 9], dpi=100)
        plt.xlabel('Time')
        plt.ylabel('Utilization')
        plt.title('CPU Utilization')
        plt.yticks(np.arange(0, 100, step=5))
        plt.grid(True)
        plt.ylim(top=100)
        plt.plot(x, y)
        plt.gcf().autofmt_xdate()
        plt.tight_layout()
        plt.savefig('/tmp/cpuload.png')
        plt.close()
        cpuload_6h = open('/tmp/cpuload.png', 'rb')
        bot.edit_message_media(media=types.InputMedia(type='photo', media=cpuload_6h),chat_id=call.message.chat.id,message_id=call.message.message_id, reply_markup=cpuloadhist)
      except:
        bot.send_message(config.tg, text = ("CPU Utilization history load error"))
    if call.data == "cpuhist_12h":
      try:
        df = pd.read_csv(os.path.join(config.serverbotpathdb, "cpuload.dat"), sep=";", encoding="utf-8", header=None)
        df.iloc[:,0] = pd.to_datetime(df.iloc[:,0], unit='s')
        period = df.iloc[:,0] > df.iloc[:,0].max() - pd.Timedelta(hours=12)
        x = df.iloc[:,0].loc[period]
        y = df.iloc[:,1].loc[period]
        plt.figure(figsize=[20, 9], dpi=100)
        plt.xlabel('Time')
        plt.ylabel('Utilization')
        plt.title('CPU Utilization')
        plt.yticks(np.arange(0, 100, step=5))
        plt.grid(True)
        plt.ylim(top=100)
        plt.plot(x, y)
        plt.gcf().autofmt_xdate()
        plt.tight_layout()
        plt.savefig('/tmp/cpuload.png')
        plt.close()
        cpuload_12h = open('/tmp/cpuload.png', 'rb')
        bot.edit_message_media(media=types.InputMedia(type='photo', media=cpuload_12h),chat_id=call.message.chat.id,message_id=call.message.message_id, reply_markup=cpuloadhist)
      except:
        bot.send_message(config.tg, text = ("CPU Utilization history load error"))
    if call.data == "cpuhist_1d":
      try:
        df = pd.read_csv(os.path.join(config.serverbotpathdb, "cpuload.dat"), sep=";", encoding="utf-8", header=None)
        df.iloc[:,0] = pd.to_datetime(df.iloc[:,0], unit='s')
        period = df.iloc[:,0] > df.iloc[:,0].max() - pd.Timedelta(hours=24)
        x = df.iloc[:,0].loc[period]
        y = df.iloc[:,1].loc[period]
        plt.figure(figsize=[20, 9], dpi=100)
        plt.xlabel('Time')
        plt.ylabel('Utilization')
        plt.title('CPU Utilization')
        plt.yticks(np.arange(0, 100, step=5))
        plt.grid(True)
        plt.ylim(top=100)
        plt.plot(x, y)
        plt.gcf().autofmt_xdate()
        plt.tight_layout()
        plt.savefig('/tmp/cpuload.png')
        plt.close()
        cpuload_1d = open('/tmp/cpuload.png', 'rb')
        bot.edit_message_media(media=types.InputMedia(type='photo', media=cpuload_1d),chat_id=call.message.chat.id,message_id=call.message.message_id, reply_markup=cpuloadhist)
      except:
        bot.send_message(config.tg, text = ("CPU Utilization history load error"))
    if call.data == "cpuhist_3d":
      try:
        df = pd.read_csv(os.path.join(config.serverbotpathdb, "cpuload.dat"), sep=";", encoding="utf-8", header=None)
        df.iloc[:,0] = pd.to_datetime(df.iloc[:,0], unit='s')
        period = df.iloc[:,0] > df.iloc[:,0].max() - pd.Timedelta(hours=72)
        x = df.iloc[:,0].loc[period]
        y = df.iloc[:,1].loc[period]
        plt.figure(figsize=[20, 9], dpi=100)
        plt.xlabel('Time')
        plt.ylabel('Utilization')
        plt.title('CPU Utilization')
        plt.yticks(np.arange(0, 100, step=5))
        plt.grid(True)
        plt.ylim(top=100)
        plt.plot(x, y)
        plt.gcf().autofmt_xdate()
        plt.tight_layout()
        plt.savefig('/tmp/cpuload.png')
        plt.close()
        cpuload_3d = open('/tmp/cpuload.png', 'rb')
        bot.edit_message_media(media=types.InputMedia(type='photo', media=cpuload_3d),chat_id=call.message.chat.id,message_id=call.message.message_id, reply_markup=cpuhistmore)
      except:
        bot.send_message(config.tg, text = ("CPU Utilization history load error"))
    if call.data == "cpuhist_5d":
      try:
        df = pd.read_csv(os.path.join(config.serverbotpathdb, "cpuload.dat"), sep=";", encoding="utf-8", header=None)
        df.iloc[:,0] = pd.to_datetime(df.iloc[:,0], unit='s')
        period = df.iloc[:,0] > df.iloc[:,0].max() - pd.Timedelta(hours=120)
        x = df.iloc[:,0].loc[period]
        y = df.iloc[:,1].loc[period]
        plt.figure(figsize=[30, 9], dpi=100)
        plt.xlabel('Time')
        plt.ylabel('Utilization')
        plt.title('CPU Utilization')
        plt.yticks(np.arange(0, 100, step=5))
        plt.grid(True)
        plt.ylim(top=100)
        plt.plot(x, y)
        plt.gcf().autofmt_xdate()
        plt.tight_layout()
        plt.savefig('/tmp/cpuload.png')
        plt.close()
        cpuload_5d = open('/tmp/cpuload.png', 'rb')
        bot.edit_message_media(media=types.InputMedia(type='photo', media=cpuload_5d),chat_id=call.message.chat.id,message_id=call.message.message_id, reply_markup=cpuhistmore)
      except:
        bot.send_message(config.tg, text = ("CPU Utilization history load error"))
    if call.data == "cpuhist_7d":
      try:
        df = pd.read_csv(os.path.join(config.serverbotpathdb, "cpuload.dat"), sep=";", encoding="utf-8", header=None)
        df.iloc[:,0] = pd.to_datetime(df.iloc[:,0], unit='s')
        period = df.iloc[:,0] > df.iloc[:,0].max() - pd.Timedelta(hours=168)
        x = df.iloc[:,0].loc[period]
        y = df.iloc[:,1].loc[period]
        plt.figure(figsize=[30, 9], dpi=100)
        plt.xlabel('Time')
        plt.ylabel('Utilization')
        plt.title('CPU Utilization')
        plt.yticks(np.arange(0, 100, step=5))
        plt.grid(True)
        plt.ylim(top=100)
        plt.plot(x, y)
        plt.gcf().autofmt_xdate()
        plt.tight_layout()
        plt.savefig('/tmp/cpuload.png')
        plt.close()
        cpuload_7d = open('/tmp/cpuload.png', 'rb')
        bot.edit_message_media(media=types.InputMedia(type='photo', media=cpuload_7d),chat_id=call.message.chat.id,message_id=call.message.message_id, reply_markup=cpuhistmore)
      except:
        bot.send_message(config.tg, text = ("CPU Utilization history load error"))
    if call.data == "cpuhist_14d":
      try:
        df = pd.read_csv(os.path.join(config.serverbotpathdb, "cpuload.dat"), sep=";", encoding="utf-8", header=None)
        df.iloc[:,0] = pd.to_datetime(df.iloc[:,0], unit='s')
        period = df.iloc[:,0] > df.iloc[:,0].max() - pd.Timedelta(hours=336)
        x = df.iloc[:,0].loc[period]
        y = df.iloc[:,1].loc[period]
        plt.figure(figsize=[30, 9], dpi=100)
        plt.xlabel('Time')
        plt.ylabel('Utilization')
        plt.title('CPU Utilization')
        plt.yticks(np.arange(0, 100, step=5))
        plt.grid(True)
        plt.ylim(top=100)
        plt.plot(x, y)
        plt.gcf().autofmt_xdate()
        plt.tight_layout()
        plt.savefig('/tmp/cpuload.png')
        plt.close()
        cpuload_14d = open('/tmp/cpuload.png', 'rb')
        bot.edit_message_media(media=types.InputMedia(type='photo', media=cpuload_14d),chat_id=call.message.chat.id,message_id=call.message.message_id, reply_markup=cpuhistmore)
      except:
        bot.send_message(config.tg, text = ("CPU Utilization history load error"))
    if call.data == "cpuhist_21d":
      try:
        df = pd.read_csv(os.path.join(config.serverbotpathdb, "cpuload.dat"), sep=";", encoding="utf-8", header=None)
        df.iloc[:,0] = pd.to_datetime(df.iloc[:,0], unit='s')
        period = df.iloc[:,0] > df.iloc[:,0].max() - pd.Timedelta(hours=504)
        x = df.iloc[:,0].loc[period]
        y = df.iloc[:,1].loc[period]
        plt.figure(figsize=[30, 9], dpi=100)
        plt.xlabel('Time')
        plt.ylabel('Utilization')
        plt.title('CPU Utilization')
        plt.yticks(np.arange(0, 100, step=5))
        plt.grid(True)
        plt.ylim(top=100)
        plt.plot(x, y)
        plt.gcf().autofmt_xdate()
        plt.tight_layout()
        plt.savefig('/tmp/cpuload.png')
        plt.close()
        cpuload_21d = open('/tmp/cpuload.png', 'rb')
        bot.edit_message_media(media=types.InputMedia(type='photo', media=cpuload_21d),chat_id=call.message.chat.id,message_id=call.message.message_id, reply_markup=cpuhistmore)
      except:
        bot.send_message(config.tg, text = ("CPU Utilization history load error"))
    if call.data == "cpuhist_30d":
      try:
        df = pd.read_csv(os.path.join(config.serverbotpathdb, "cpuload.dat"), sep=";", encoding="utf-8", header=None)
        df.iloc[:,0] = pd.to_datetime(df.iloc[:,0], unit='s')
        period = df.iloc[:,0] > df.iloc[:,0].max() - pd.Timedelta(hours=720)
        x = df.iloc[:,0].loc[period]
        y = df.iloc[:,1].loc[period]
        plt.figure(figsize=[30, 9], dpi=100)
        plt.xlabel('Time')
        plt.ylabel('Utilization')
        plt.title('CPU Utilization')
        plt.yticks(np.arange(0, 100, step=5))
        plt.grid(True)
        plt.ylim(top=100)
        plt.plot(x, y)
        plt.gcf().autofmt_xdate()
        plt.tight_layout()
        plt.savefig('/tmp/cpuload.png')
        plt.close()
        cpuload_30d = open('/tmp/cpuload.png', 'rb')
        bot.edit_message_media(media=types.InputMedia(type='photo', media=cpuload_30d),chat_id=call.message.chat.id,message_id=call.message.message_id, reply_markup=cpuhistmore)
        bot.send
      except:
        bot.send_message(config.tg, text = ("CPU Utilization history load error"))
  # CPU graph

  # RAM graph
    if call.data == "ramloadhist":
      bot.edit_message_reply_markup(config.tg, message_id=call.message.message_id, reply_markup=ramloadhist)
    if call.data == "ramhistmore":
      bot.edit_message_reply_markup(config.tg, message_id=call.message.message_id, reply_markup=ramhistmore)
    if call.data == "ramhist_30m":
      try:
        df = pd.read_csv(os.path.join(config.serverbotpathdb, "ramload.dat"), sep=";", encoding="utf-8", header=None)
        df.iloc[:,0] = pd.to_datetime(df.iloc[:,0], unit='s')
        period = df.iloc[:,0] > df.iloc[:,0].max() - pd.Timedelta(minutes=30)
        x = df.iloc[:,0].loc[period]
        y = df.iloc[:,1].loc[period]
        plt.figure(figsize=[12, 9], dpi=100)
        plt.xlabel('Time')
        plt.ylabel('Load')
        plt.title('RAM Load')
        plt.yticks(np.arange(0, 100, step=5))
        plt.grid(True)
        plt.ylim(top=100)
        plt.plot(x, y)
        plt.gcf().autofmt_xdate()
        plt.tight_layout()
        plt.savefig('/tmp/ramload.png')
        plt.close()
        ramload_30m = open('/tmp/ramload.png', 'rb')
        bot.edit_message_media(media=types.InputMedia(type='photo', media=ramload_30m),chat_id=call.message.chat.id,message_id=call.message.message_id, reply_markup=ramloadhist)
      except:
        bot.send_message(config.tg, text = ("RAM Load history load error"))
    if call.data == "ramhist_1h":
      try:
        df = pd.read_csv(os.path.join(config.serverbotpathdb, "ramload.dat"), sep=";", encoding="utf-8", header=None)
        df.iloc[:,0] = pd.to_datetime(df.iloc[:,0], unit='s')
        period = df.iloc[:,0] > df.iloc[:,0].max() - pd.Timedelta(hours=1)
        x = df.iloc[:,0].loc[period]
        y = df.iloc[:,1].loc[period]
        plt.figure(figsize=[15, 9], dpi=100)
        plt.xlabel('Time')
        plt.ylabel('Load')
        plt.title('RAM Load')
        plt.yticks(np.arange(0, 100, step=5))
        plt.grid(True)
        plt.ylim(top=100)
        plt.plot(x, y)
        plt.gcf().autofmt_xdate()
        plt.tight_layout()
        plt.savefig('/tmp/ramload.png')
        plt.close()
        ramload_1h = open('/tmp/ramload.png', 'rb')
        bot.edit_message_media(media=types.InputMedia(type='photo', media=ramload_1h),chat_id=call.message.chat.id,message_id=call.message.message_id, reply_markup=ramloadhist)
      except:
        bot.send_message(config.tg, text = ("RAM Load history load error"))
    if call.data == "ramhist_3h":
      try:
        df = pd.read_csv(os.path.join(config.serverbotpathdb, "ramload.dat"), sep=";", encoding="utf-8", header=None)
        df.iloc[:,0] = pd.to_datetime(df.iloc[:,0], unit='s')
        period = df.iloc[:,0] > df.iloc[:,0].max() - pd.Timedelta(hours=3)
        x = df.iloc[:,0].loc[period]
        y = df.iloc[:,1].loc[period]
        plt.figure(figsize=[20, 9], dpi=100)
        plt.xlabel('Time')
        plt.ylabel('Load')
        plt.title('RAM Load')
        plt.yticks(np.arange(0, 100, step=5))
        plt.grid(True)
        plt.ylim(top=100)
        plt.plot(x, y)
        plt.gcf().autofmt_xdate()
        plt.tight_layout()
        plt.savefig('/tmp/ramload.png')
        plt.close()
        ramload_3h = open('/tmp/ramload.png', 'rb')
        bot.edit_message_media(media=types.InputMedia(type='photo', media=ramload_3h),chat_id=call.message.chat.id,message_id=call.message.message_id, reply_markup=ramloadhist)
      except:
        bot.send_message(config.tg, text = ("RAM Load history load error"))
    if call.data == "ramhist_6h":
      try:
        df = pd.read_csv(os.path.join(config.serverbotpathdb, "ramload.dat"), sep=";", encoding="utf-8", header=None)
        df.iloc[:,0] = pd.to_datetime(df.iloc[:,0], unit='s')
        period = df.iloc[:,0] > df.iloc[:,0].max() - pd.Timedelta(hours=6)
        x = df.iloc[:,0].loc[period]
        y = df.iloc[:,1].loc[period]
        plt.figure(figsize=[20, 9], dpi=100)
        plt.xlabel('Time')
        plt.ylabel('Load')
        plt.title('RAM Load')
        plt.yticks(np.arange(0, 100, step=5))
        plt.grid(True)
        plt.ylim(top=100)
        plt.plot(x, y)
        plt.gcf().autofmt_xdate()
        plt.tight_layout()
        plt.savefig('/tmp/ramload.png')
        plt.close()
        ramload_6h = open('/tmp/ramload.png', 'rb')
        bot.edit_message_media(media=types.InputMedia(type='photo', media=ramload_6h),chat_id=call.message.chat.id,message_id=call.message.message_id, reply_markup=ramloadhist)
      except:
        bot.send_message(config.tg, text = ("RAM Load history load error"))
    if call.data == "ramhist_12h":
      try:
        df = pd.read_csv(os.path.join(config.serverbotpathdb, "ramload.dat"), sep=";", encoding="utf-8", header=None)
        df.iloc[:,0] = pd.to_datetime(df.iloc[:,0], unit='s')
        period = df.iloc[:,0] > df.iloc[:,0].max() - pd.Timedelta(hours=12)
        x = df.iloc[:,0].loc[period]
        y = df.iloc[:,1].loc[period]
        plt.figure(figsize=[20, 9], dpi=100)
        plt.xlabel('Time')
        plt.ylabel('Load')
        plt.title('RAM Load')
        plt.yticks(np.arange(0, 100, step=5))
        plt.grid(True)
        plt.ylim(top=100)
        plt.plot(x, y)
        plt.gcf().autofmt_xdate()
        plt.tight_layout()
        plt.savefig('/tmp/ramload.png')
        plt.close()
        ramload_12h = open('/tmp/ramload.png', 'rb')
        bot.edit_message_media(media=types.InputMedia(type='photo', media=ramload_12h),chat_id=call.message.chat.id,message_id=call.message.message_id, reply_markup=ramloadhist)
      except:
        bot.send_message(config.tg, text = ("RAM Load history load error"))
    if call.data == "ramhist_1d":
      try:
        df = pd.read_csv(os.path.join(config.serverbotpathdb, "ramload.dat"), sep=";", encoding="utf-8", header=None)
        df.iloc[:,0] = pd.to_datetime(df.iloc[:,0], unit='s')
        period = df.iloc[:,0] > df.iloc[:,0].max() - pd.Timedelta(hours=24)
        x = df.iloc[:,0].loc[period]
        y = df.iloc[:,1].loc[period]
        plt.figure(figsize=[20, 9], dpi=100)
        plt.xlabel('Time')
        plt.ylabel('Load')
        plt.title('RAM Load')
        plt.yticks(np.arange(0, 100, step=5))
        plt.grid(True)
        plt.ylim(top=100)
        plt.plot(x, y)
        plt.gcf().autofmt_xdate()
        plt.tight_layout()
        plt.savefig('/tmp/ramload.png')
        plt.close()
        ramload_1d = open('/tmp/ramload.png', 'rb')
        bot.edit_message_media(media=types.InputMedia(type='photo', media=ramload_1d),chat_id=call.message.chat.id,message_id=call.message.message_id, reply_markup=ramloadhist)
      except:
        bot.send_message(config.tg, text = ("RAM Load history load error"))
    if call.data == "ramhist_3d":
      try:
        df = pd.read_csv(os.path.join(config.serverbotpathdb, "ramload.dat"), sep=";", encoding="utf-8", header=None)
        df.iloc[:,0] = pd.to_datetime(df.iloc[:,0], unit='s')
        period = df.iloc[:,0] > df.iloc[:,0].max() - pd.Timedelta(hours=72)
        x = df.iloc[:,0].loc[period]
        y = df.iloc[:,1].loc[period]
        plt.figure(figsize=[20, 9], dpi=100)
        plt.xlabel('Time')
        plt.ylabel('Load')
        plt.title('RAM Load')
        plt.yticks(np.arange(0, 100, step=5))
        plt.grid(True)
        plt.ylim(top=100)
        plt.plot(x, y)
        plt.gcf().autofmt_xdate()
        plt.tight_layout()
        plt.savefig('/tmp/ramload.png')
        plt.close()
        ramload_3d = open('/tmp/ramload.png', 'rb')
        bot.edit_message_media(media=types.InputMedia(type='photo', media=ramload_3d),chat_id=call.message.chat.id,message_id=call.message.message_id, reply_markup=ramhistmore)
      except:
        bot.send_message(config.tg, text = ("RAM Load history load error"))
    if call.data == "ramhist_5d":
      try:
        df = pd.read_csv(os.path.join(config.serverbotpathdb, "ramload.dat"), sep=";", encoding="utf-8", header=None)
        df.iloc[:,0] = pd.to_datetime(df.iloc[:,0], unit='s')
        period = df.iloc[:,0] > df.iloc[:,0].max() - pd.Timedelta(hours=120)
        x = df.iloc[:,0].loc[period]
        y = df.iloc[:,1].loc[period]
        plt.figure(figsize=[30, 9], dpi=100)
        plt.xlabel('Time')
        plt.ylabel('Load')
        plt.title('RAM Load')
        plt.yticks(np.arange(0, 100, step=5))
        plt.grid(True)
        plt.ylim(top=100)
        plt.plot(x, y)
        plt.gcf().autofmt_xdate()
        plt.tight_layout()
        plt.savefig('/tmp/ramload.png')
        plt.close()
        ramload_5d = open('/tmp/ramload.png', 'rb')
        bot.edit_message_media(media=types.InputMedia(type='photo', media=ramload_5d),chat_id=call.message.chat.id,message_id=call.message.message_id, reply_markup=ramhistmore)
      except:
        bot.send_message(config.tg, text = ("RAM Load history load error"))
    if call.data == "ramhist_7d":
      try:
        df = pd.read_csv(os.path.join(config.serverbotpathdb, "ramload.dat"), sep=";", encoding="utf-8", header=None)
        df.iloc[:,0] = pd.to_datetime(df.iloc[:,0], unit='s')
        period = df.iloc[:,0] > df.iloc[:,0].max() - pd.Timedelta(hours=168)
        x = df.iloc[:,0].loc[period]
        y = df.iloc[:,1].loc[period]
        plt.figure(figsize=[30, 9], dpi=100)
        plt.xlabel('Time')
        plt.ylabel('Load')
        plt.title('RAM Load')
        plt.yticks(np.arange(0, 100, step=5))
        plt.grid(True)
        plt.ylim(top=100)
        plt.plot(x, y)
        plt.gcf().autofmt_xdate()
        plt.tight_layout()
        plt.savefig('/tmp/ramload.png')
        plt.close()
        ramload_7d = open('/tmp/ramload.png', 'rb')
        bot.edit_message_media(media=types.InputMedia(type='photo', media=ramload_7d),chat_id=call.message.chat.id,message_id=call.message.message_id, reply_markup=ramhistmore)
      except:
        bot.send_message(config.tg, text = ("RAM Load history load error"))
    if call.data == "ramhist_14d":
      try:
        df = pd.read_csv(os.path.join(config.serverbotpathdb, "ramload.dat"), sep=";", encoding="utf-8", header=None)
        df.iloc[:,0] = pd.to_datetime(df.iloc[:,0], unit='s')
        period = df.iloc[:,0] > df.iloc[:,0].max() - pd.Timedelta(hours=336)
        x = df.iloc[:,0].loc[period]
        y = df.iloc[:,1].loc[period]
        plt.figure(figsize=[30, 9], dpi=100)
        plt.xlabel('Time')
        plt.ylabel('Load')
        plt.title('RAM Load')
        plt.yticks(np.arange(0, 100, step=5))
        plt.grid(True)
        plt.ylim(top=100)
        plt.plot(x, y)
        plt.gcf().autofmt_xdate()
        plt.tight_layout()
        plt.savefig('/tmp/ramload.png')
        plt.close()
        ramload_14d = open('/tmp/ramload.png', 'rb')
        bot.edit_message_media(media=types.InputMedia(type='photo', media=ramload_14d),chat_id=call.message.chat.id,message_id=call.message.message_id, reply_markup=ramhistmore)
      except:
        bot.send_message(config.tg, text = ("RAM Load history load error"))
    if call.data == "ramhist_21d":
      try:
        df = pd.read_csv(os.path.join(config.serverbotpathdb, "ramload.dat"), sep=";", encoding="utf-8", header=None)
        df.iloc[:,0] = pd.to_datetime(df.iloc[:,0], unit='s')
        period = df.iloc[:,0] > df.iloc[:,0].max() - pd.Timedelta(hours=504)
        x = df.iloc[:,0].loc[period]
        y = df.iloc[:,1].loc[period]
        plt.figure(figsize=[30, 9], dpi=100)
        plt.xlabel('Time')
        plt.ylabel('Load')
        plt.title('RAM Load')
        plt.yticks(np.arange(0, 100, step=5))
        plt.grid(True)
        plt.ylim(top=100)
        plt.plot(x, y)
        plt.gcf().autofmt_xdate()
        plt.tight_layout()
        plt.savefig('/tmp/ramload.png')
        plt.close()
        ramload_21d = open('/tmp/ramload.png', 'rb')
        bot.edit_message_media(media=types.InputMedia(type='photo', media=ramload_21d),chat_id=call.message.chat.id,message_id=call.message.message_id, reply_markup=ramhistmore)
      except:
        bot.send_message(config.tg, text = ("RAM Load history load error"))
    if call.data == "ramhist_30d":
      try:
        df = pd.read_csv(os.path.join(config.serverbotpathdb, "ramload.dat"), sep=";", encoding="utf-8", header=None)
        df.iloc[:,0] = pd.to_datetime(df.iloc[:,0], unit='s')
        period = df.iloc[:,0] > df.iloc[:,0].max() - pd.Timedelta(hours=720)
        x = df.iloc[:,0].loc[period]
        y = df.iloc[:,1].loc[period]
        plt.figure(figsize=[30, 9], dpi=100)
        plt.xlabel('Time')
        plt.ylabel('Load')
        plt.title('RAM Load')
        plt.yticks(np.arange(0, 100, step=5))
        plt.grid(True)
        plt.ylim(top=100)
        plt.plot(x, y)
        plt.gcf().autofmt_xdate()
        plt.tight_layout()
        plt.savefig('/tmp/ramload.png')
        plt.close()
        ramload_30d = open('/tmp/ramload.png', 'rb')
        bot.edit_message_media(media=types.InputMedia(type='photo', media=ramload_30d),chat_id=call.message.chat.id,message_id=call.message.message_id, reply_markup=ramhistmore)
        bot.send
      except:
        bot.send_message(config.tg, text = ("RAM Load history load error"))
  # RAM graph

# PING graph
    if call.data == "pingcheckhist":
      bot.edit_message_reply_markup(config.tg, message_id=call.message.message_id, reply_markup=pingcheckhist)
    if call.data == "pinghistmore":
      bot.edit_message_reply_markup(config.tg, message_id=call.message.message_id, reply_markup=pinghistmore)
    if call.data == "pinghist_30m":
      try:
        df = pd.read_csv(os.path.join(config.serverbotpathdb, "pingcheck.dat"), sep=";", encoding="utf-8", header=None)
        df.iloc[:,0] = pd.to_datetime(df.iloc[:,0], unit='s')
        period = df.iloc[:,0] > df.iloc[:,0].max() - pd.Timedelta(minutes=30)
        x = df.iloc[:,0].loc[period]
        y = df.iloc[:,1].loc[period]
        plt.figure(figsize=[12, 9], dpi=100)
        plt.xlabel('Time')
        plt.ylabel('ms')
        plt.title('Ping Check')
        plt.grid(True)
        plt.plot(x, y)
        plt.gcf().autofmt_xdate()
        plt.tight_layout()
        plt.savefig('/tmp/pingcheck.png')
        plt.close()
        pingcheck_30m = open('/tmp/pingcheck.png', 'rb')
        bot.edit_message_media(media=types.InputMedia(type='photo', media=pingcheck_30m),chat_id=call.message.chat.id,message_id=call.message.message_id, reply_markup=pingcheckhist)
      except:
        bot.send_message(config.tg, text = ("Ping check history load error"))
    if call.data == "pinghist_1h":
      try:
        df = pd.read_csv(os.path.join(config.serverbotpathdb, "pingcheck.dat"), sep=";", encoding="utf-8", header=None)
        df.iloc[:,0] = pd.to_datetime(df.iloc[:,0], unit='s')
        period = df.iloc[:,0] > df.iloc[:,0].max() - pd.Timedelta(hours=1)
        x = df.iloc[:,0].loc[period]
        y = df.iloc[:,1].loc[period]
        plt.figure(figsize=[15, 9], dpi=100)
        plt.xlabel('Time')
        plt.ylabel('ms')
        plt.title('Ping Check')
        plt.grid(True)
        plt.plot(x, y)
        plt.gcf().autofmt_xdate()
        plt.tight_layout()
        plt.savefig('/tmp/pingcheck.png')
        plt.close()
        pingcheck_1h = open('/tmp/pingcheck.png', 'rb')
        bot.edit_message_media(media=types.InputMedia(type='photo', media=pingcheck_1h),chat_id=call.message.chat.id,message_id=call.message.message_id, reply_markup=pingcheckhist)
      except:
        bot.send_message(config.tg, text = ("Ping check history load error"))
    if call.data == "pinghist_3h":
      try:
        df = pd.read_csv(os.path.join(config.serverbotpathdb, "pingcheck.dat"), sep=";", encoding="utf-8", header=None)
        df.iloc[:,0] = pd.to_datetime(df.iloc[:,0], unit='s')
        period = df.iloc[:,0] > df.iloc[:,0].max() - pd.Timedelta(hours=3)
        x = df.iloc[:,0].loc[period]
        y = df.iloc[:,1].loc[period]
        plt.figure(figsize=[20, 9], dpi=100)
        plt.xlabel('Time')
        plt.ylabel('ms')
        plt.title('Ping Check')
        plt.grid(True)
        plt.plot(x, y)
        plt.gcf().autofmt_xdate()
        plt.tight_layout()
        plt.savefig('/tmp/pingcheck.png')
        plt.close()
        pingcheck_3h = open('/tmp/pingcheck.png', 'rb')
        bot.edit_message_media(media=types.InputMedia(type='photo', media=pingcheck_3h),chat_id=call.message.chat.id,message_id=call.message.message_id, reply_markup=pingcheckhist)
      except:
        bot.send_message(config.tg, text = ("Ping check history load error"))
    if call.data == "pinghist_6h":
      try:
        df = pd.read_csv(os.path.join(config.serverbotpathdb, "pingcheck.dat"), sep=";", encoding="utf-8", header=None)
        df.iloc[:,0] = pd.to_datetime(df.iloc[:,0], unit='s')
        period = df.iloc[:,0] > df.iloc[:,0].max() - pd.Timedelta(hours=6)
        x = df.iloc[:,0].loc[period]
        y = df.iloc[:,1].loc[period]
        plt.figure(figsize=[20, 9], dpi=100)
        plt.xlabel('Time')
        plt.ylabel('ms')
        plt.title('Ping Check')
        plt.grid(True)
        plt.plot(x, y)
        plt.gcf().autofmt_xdate()
        plt.tight_layout()
        plt.savefig('/tmp/pingcheck.png')
        plt.close()
        pingcheck_6h = open('/tmp/pingcheck.png', 'rb')
        bot.edit_message_media(media=types.InputMedia(type='photo', media=pingcheck_6h),chat_id=call.message.chat.id,message_id=call.message.message_id, reply_markup=pingcheckhist)
      except:
        bot.send_message(config.tg, text = ("Ping check history load error"))
    if call.data == "pinghist_12h":
      try:
        df = pd.read_csv(os.path.join(config.serverbotpathdb, "pingcheck.dat"), sep=";", encoding="utf-8", header=None)
        df.iloc[:,0] = pd.to_datetime(df.iloc[:,0], unit='s')
        period = df.iloc[:,0] > df.iloc[:,0].max() - pd.Timedelta(hours=12)
        x = df.iloc[:,0].loc[period]
        y = df.iloc[:,1].loc[period]
        plt.figure(figsize=[20, 9], dpi=100)
        plt.xlabel('Time')
        plt.ylabel('ms')
        plt.title('Ping Check')
        plt.grid(True)
        plt.plot(x, y)
        plt.gcf().autofmt_xdate()
        plt.tight_layout()
        plt.savefig('/tmp/pingcheck.png')
        plt.close()
        pingcheck_12h = open('/tmp/pingcheck.png', 'rb')
        bot.edit_message_media(media=types.InputMedia(type='photo', media=pingcheck_12h),chat_id=call.message.chat.id,message_id=call.message.message_id, reply_markup=pingcheckhist)
      except:
        bot.send_message(config.tg, text = ("Ping check history load error"))
    if call.data == "pinghist_1d":
      try:
        df = pd.read_csv(os.path.join(config.serverbotpathdb, "pingcheck.dat"), sep=";", encoding="utf-8", header=None)
        df.iloc[:,0] = pd.to_datetime(df.iloc[:,0], unit='s')
        period = df.iloc[:,0] > df.iloc[:,0].max() - pd.Timedelta(hours=24)
        x = df.iloc[:,0].loc[period]
        y = df.iloc[:,1].loc[period]
        plt.figure(figsize=[20, 9], dpi=100)
        plt.xlabel('Time')
        plt.ylabel('ms')
        plt.title('Ping Check')
        plt.grid(True)
        plt.plot(x, y)
        plt.gcf().autofmt_xdate()
        plt.tight_layout()
        plt.savefig('/tmp/pingcheck.png')
        plt.close()
        pingcheck_1d = open('/tmp/pingcheck.png', 'rb')
        bot.edit_message_media(media=types.InputMedia(type='photo', media=pingcheck_1d),chat_id=call.message.chat.id,message_id=call.message.message_id, reply_markup=pingcheckhist)
      except:
        bot.send_message(config.tg, text = ("Ping check history load error"))
    if call.data == "pinghist_3d":
      try:
        df = pd.read_csv(os.path.join(config.serverbotpathdb, "pingcheck.dat"), sep=";", encoding="utf-8", header=None)
        df.iloc[:,0] = pd.to_datetime(df.iloc[:,0], unit='s')
        period = df.iloc[:,0] > df.iloc[:,0].max() - pd.Timedelta(hours=72)
        x = df.iloc[:,0].loc[period]
        y = df.iloc[:,1].loc[period]
        plt.figure(figsize=[20, 9], dpi=100)
        plt.xlabel('Time')
        plt.ylabel('ms')
        plt.title('Ping Check')
        plt.grid(True)
        plt.plot(x, y)
        plt.gcf().autofmt_xdate()
        plt.tight_layout()
        plt.savefig('/tmp/pingcheck.png')
        plt.close()
        pingcheck_3d = open('/tmp/pingcheck.png', 'rb')
        bot.edit_message_media(media=types.InputMedia(type='photo', media=pingcheck_3d),chat_id=call.message.chat.id,message_id=call.message.message_id, reply_markup=pinghistmore)
      except:
        bot.send_message(config.tg, text = ("Ping check history load error"))
    if call.data == "pinghist_5d":
      try:
        df = pd.read_csv(os.path.join(config.serverbotpathdb, "pingcheck.dat"), sep=";", encoding="utf-8", header=None)
        df.iloc[:,0] = pd.to_datetime(df.iloc[:,0], unit='s')
        period = df.iloc[:,0] > df.iloc[:,0].max() - pd.Timedelta(hours=120)
        x = df.iloc[:,0].loc[period]
        y = df.iloc[:,1].loc[period]
        plt.figure(figsize=[30, 9], dpi=100)
        plt.xlabel('Time')
        plt.ylabel('ms')
        plt.title('Ping Check')
        plt.grid(True)
        plt.plot(x, y)
        plt.gcf().autofmt_xdate()
        plt.tight_layout()
        plt.savefig('/tmp/pingcheck.png')
        plt.close()
        pingcheck_5d = open('/tmp/pingcheck.png', 'rb')
        bot.edit_message_media(media=types.InputMedia(type='photo', media=pingcheck_5d),chat_id=call.message.chat.id,message_id=call.message.message_id, reply_markup=pinghistmore)
      except:
        bot.send_message(config.tg, text = ("Ping check history load error"))
    if call.data == "pinghist_7d":
      try:
        df = pd.read_csv(os.path.join(config.serverbotpathdb, "pingcheck.dat"), sep=";", encoding="utf-8", header=None)
        df.iloc[:,0] = pd.to_datetime(df.iloc[:,0], unit='s')
        period = df.iloc[:,0] > df.iloc[:,0].max() - pd.Timedelta(hours=168)
        x = df.iloc[:,0].loc[period]
        y = df.iloc[:,1].loc[period]
        plt.figure(figsize=[30, 9], dpi=100)
        plt.xlabel('Time')
        plt.ylabel('ms')
        plt.title('Ping Check')
        plt.grid(True)
        plt.plot(x, y)
        plt.gcf().autofmt_xdate()
        plt.tight_layout()
        plt.savefig('/tmp/pingcheck.png')
        plt.close()
        pingcheck_7d = open('/tmp/pingcheck.png', 'rb')
        bot.edit_message_media(media=types.InputMedia(type='photo', media=pingcheck_7d),chat_id=call.message.chat.id,message_id=call.message.message_id, reply_markup=pinghistmore)
      except:
        bot.send_message(config.tg, text = ("Ping check history load error"))
    if call.data == "pinghist_14d":
      try:
        df = pd.read_csv(os.path.join(config.serverbotpathdb, "pingcheck.dat"), sep=";", encoding="utf-8", header=None)
        df.iloc[:,0] = pd.to_datetime(df.iloc[:,0], unit='s')
        period = df.iloc[:,0] > df.iloc[:,0].max() - pd.Timedelta(hours=336)
        x = df.iloc[:,0].loc[period]
        y = df.iloc[:,1].loc[period]
        plt.figure(figsize=[30, 9], dpi=100)
        plt.xlabel('Time')
        plt.ylabel('ms')
        plt.title('Ping Check')
        plt.grid(True)
        plt.plot(x, y)
        plt.gcf().autofmt_xdate()
        plt.tight_layout()
        plt.savefig('/tmp/pingcheck.png')
        plt.close()
        pingcheck_14d = open('/tmp/pingcheck.png', 'rb')
        bot.edit_message_media(media=types.InputMedia(type='photo', media=pingcheck_14d),chat_id=call.message.chat.id,message_id=call.message.message_id, reply_markup=pinghistmore)
      except:
        bot.send_message(config.tg, text = ("Ping check history load error"))
    if call.data == "pinghist_21d":
      try:
        df = pd.read_csv(os.path.join(config.serverbotpathdb, "pingcheck.dat"), sep=";", encoding="utf-8", header=None)
        df.iloc[:,0] = pd.to_datetime(df.iloc[:,0], unit='s')
        period = df.iloc[:,0] > df.iloc[:,0].max() - pd.Timedelta(hours=504)
        x = df.iloc[:,0].loc[period]
        y = df.iloc[:,1].loc[period]
        plt.figure(figsize=[30, 9], dpi=100)
        plt.xlabel('Time')
        plt.ylabel('ms')
        plt.title('Ping Check')
        plt.grid(True)
        plt.plot(x, y)
        plt.gcf().autofmt_xdate()
        plt.tight_layout()
        plt.savefig('/tmp/pingcheck.png')
        plt.close()
        pingcheck_21d = open('/tmp/pingcheck.png', 'rb')
        bot.edit_message_media(media=types.InputMedia(type='photo', media=pingcheck_21d),chat_id=call.message.chat.id,message_id=call.message.message_id, reply_markup=pinghistmore)
      except:
        bot.send_message(config.tg, text = ("Ping check history load error"))
    if call.data == "pinghist_30d":
      try:
        df = pd.read_csv(os.path.join(config.serverbotpathdb, "pingcheck.dat"), sep=";", encoding="utf-8", header=None)
        df.iloc[:,0] = pd.to_datetime(df.iloc[:,0], unit='s')
        period = df.iloc[:,0] > df.iloc[:,0].max() - pd.Timedelta(hours=720)
        x = df.iloc[:,0].loc[period]
        y = df.iloc[:,1].loc[period]
        plt.figure(figsize=[30, 9], dpi=100)
        plt.xlabel('Time')
        plt.ylabel('ms')
        plt.title('Ping Check')
        plt.grid(True)
        plt.plot(x, y)
        plt.gcf().autofmt_xdate()
        plt.tight_layout()
        plt.savefig('/tmp/pingcheck.png')
        plt.close()
        pingcheck_30d = open('/tmp/pingcheck.png', 'rb')
        bot.edit_message_media(media=types.InputMedia(type='photo', media=pingcheck_30d),chat_id=call.message.chat.id,message_id=call.message.message_id, reply_markup=pinghistmore)
        bot.send
      except:
        bot.send_message(config.tg, text = ("Ping check history load error"))
  # PING graph

  # Network graph
    if call.data == "networkcheckhist":
      bot.edit_message_reply_markup(config.tg, message_id=call.message.message_id, reply_markup=networkcheckhist)
    if call.data == "networkhistmore":
      bot.edit_message_reply_markup(config.tg, message_id=call.message.message_id, reply_markup=networkhistmore)
    if call.data == "networkhist_30m":
      try:
        df = pd.read_csv(os.path.join(config.serverbotpathdb, "networkload.dat"), sep=";", encoding="utf-8", header=None)
        df.iloc[:,0] = pd.to_datetime(df.iloc[:,0], unit='s')
        df.iloc[:,1] = df.iloc[:,1]/1024/1024*8
        df.iloc[:,2] = df.iloc[:,2]/1024/1024*8
        period = df.iloc[:,0] > df.iloc[:,0].max() - pd.Timedelta(minutes=30)
        x = df.iloc[:,0].loc[period]
        y1 = df.iloc[:,1].loc[period]
        y2 = df.iloc[:,2].loc[period]
        plt.figure(figsize=[12, 9], dpi=100)
        plt.subplot(2, 1, 1)
        plt.xlabel('Time')
        plt.ylabel('MB/s')
        plt.title('Upload speed')
        plt.grid(True)
        plt.plot(x, y1)
        plt.subplot(2, 1, 2)
        plt.xlabel('Time')
        plt.ylabel('MB/s')
        plt.title('Download speed')
        plt.grid(True)
        plt.plot(x, y2)
        plt.gcf().autofmt_xdate()
        plt.tight_layout()
        plt.savefig('/tmp/networkload.png')
        plt.close()
        networkload_1h = open('/tmp/networkload.png', 'rb')
        bot.edit_message_media(media=types.InputMedia(type='photo', media=networkload_1h),chat_id=call.message.chat.id,message_id=call.message.message_id, reply_markup=networkcheckhist)
      except:
        bot.send_message(config.tg, text = ("Network Utilization history load error"))
    if call.data == "networkhist_1h":
      try:
        df = pd.read_csv(os.path.join(config.serverbotpathdb, "networkload.dat"), sep=";", encoding="utf-8", header=None)
        df.iloc[:,0] = pd.to_datetime(df.iloc[:,0], unit='s')
        df.iloc[:,1] = df.iloc[:,1]/1024/1024*8
        df.iloc[:,2] = df.iloc[:,2]/1024/1024*8
        period = df.iloc[:,0] > df.iloc[:,0].max() - pd.Timedelta(hours=1)
        x = df.iloc[:,0].loc[period]
        y1 = df.iloc[:,1].loc[period]
        y2 = df.iloc[:,2].loc[period]
        plt.figure(figsize=[15, 9], dpi=100)
        plt.subplot(2, 1, 1)
        plt.xlabel('Time')
        plt.ylabel('MB/s')
        plt.title('Upload speed')
        plt.grid(True)
        plt.plot(x, y1)
        plt.subplot(2, 1, 2)
        plt.xlabel('Time')
        plt.ylabel('MB/s')
        plt.title('Download speed')
        plt.grid(True)
        plt.plot(x, y2)
        plt.gcf().autofmt_xdate()
        plt.tight_layout()
        plt.savefig('/tmp/networkload.png')
        plt.close()
        networkload_1h = open('/tmp/networkload.png', 'rb')
        bot.edit_message_media(media=types.InputMedia(type='photo', media=networkload_1h),chat_id=call.message.chat.id,message_id=call.message.message_id, reply_markup=networkcheckhist)
      except:
        bot.send_message(config.tg, text = ("Network Utilization history load error"))
    if call.data == "networkhist_3h":
      try:
        df = pd.read_csv(os.path.join(config.serverbotpathdb, "networkload.dat"), sep=";", encoding="utf-8", header=None)
        df.iloc[:,0] = pd.to_datetime(df.iloc[:,0], unit='s')
        df.iloc[:,1] = df.iloc[:,1]/1024/1024*8
        df.iloc[:,2] = df.iloc[:,2]/1024/1024*8
        period = df.iloc[:,0] > df.iloc[:,0].max() - pd.Timedelta(hours=3)
        x = df.iloc[:,0].loc[period]
        y1 = df.iloc[:,1].loc[period]
        y2 = df.iloc[:,2].loc[period]
        plt.figure(figsize=[20, 9], dpi=100)
        plt.subplot(2, 1, 1)
        plt.xlabel('Time')
        plt.ylabel('MB/s')
        plt.title('Upload speed')
        plt.grid(True)
        plt.plot(x, y1)
        plt.subplot(2, 1, 2)
        plt.xlabel('Time')
        plt.ylabel('MB/s')
        plt.title('Download speed')
        plt.grid(True)
        plt.plot(x, y2)
        plt.gcf().autofmt_xdate()
        plt.tight_layout()
        plt.savefig('/tmp/networkload.png')
        plt.close()
        networkload_3h = open('/tmp/networkload.png', 'rb')
        bot.edit_message_media(media=types.InputMedia(type='photo', media=networkload_3h),chat_id=call.message.chat.id,message_id=call.message.message_id, reply_markup=networkcheckhist)
      except:
        bot.send_message(config.tg, text = ("Network Utilization history load error"))
    if call.data == "networkhist_6h":
      try:
        df = pd.read_csv(os.path.join(config.serverbotpathdb, "networkload.dat"), sep=";", encoding="utf-8", header=None)
        df.iloc[:,0] = pd.to_datetime(df.iloc[:,0], unit='s')
        df.iloc[:,1] = df.iloc[:,1]/1024/1024*8
        df.iloc[:,2] = df.iloc[:,2]/1024/1024*8
        period = df.iloc[:,0] > df.iloc[:,0].max() - pd.Timedelta(hours=6)
        x = df.iloc[:,0].loc[period]
        y1 = df.iloc[:,1].loc[period]
        y2 = df.iloc[:,2].loc[period]
        plt.figure(figsize=[20, 9], dpi=100)
        plt.subplot(2, 1, 1)
        plt.xlabel('Time')
        plt.ylabel('MB/s')
        plt.title('Upload speed')
        plt.grid(True)
        plt.plot(x, y1)
        plt.subplot(2, 1, 2)
        plt.xlabel('Time')
        plt.ylabel('MB/s')
        plt.title('Download speed')
        plt.grid(True)
        plt.plot(x, y2)
        plt.gcf().autofmt_xdate()
        plt.tight_layout()
        plt.savefig('/tmp/networkload.png')
        plt.close()
        networkload_6h = open('/tmp/networkload.png', 'rb')
        bot.edit_message_media(media=types.InputMedia(type='photo', media=networkload_6h),chat_id=call.message.chat.id,message_id=call.message.message_id, reply_markup=networkcheckhist)
      except:
        bot.send_message(config.tg, text = ("Network Utilization history load error"))
    if call.data == "networkhist_12h":
      try:
        df = pd.read_csv(os.path.join(config.serverbotpathdb, "networkload.dat"), sep=";", encoding="utf-8", header=None)
        df.iloc[:,0] = pd.to_datetime(df.iloc[:,0], unit='s')
        df.iloc[:,1] = df.iloc[:,1]/1024/1024*8
        df.iloc[:,2] = df.iloc[:,2]/1024/1024*8
        period = df.iloc[:,0] > df.iloc[:,0].max() - pd.Timedelta(hours=12)
        x = df.iloc[:,0].loc[period]
        y1 = df.iloc[:,1].loc[period]
        y2 = df.iloc[:,2].loc[period]
        plt.figure(figsize=[20, 9], dpi=100)
        plt.subplot(2, 1, 1)
        plt.xlabel('Time')
        plt.ylabel('MB/s')
        plt.title('Upload speed')
        plt.grid(True)
        plt.plot(x, y1)
        plt.subplot(2, 1, 2)
        plt.xlabel('Time')
        plt.ylabel('MB/s')
        plt.title('Download speed')
        plt.grid(True)
        plt.plot(x, y2)
        plt.gcf().autofmt_xdate()
        plt.tight_layout()
        plt.savefig('/tmp/networkload.png')
        plt.close()
        networkload_12h = open('/tmp/networkload.png', 'rb')
        bot.edit_message_media(media=types.InputMedia(type='photo', media=networkload_12h),chat_id=call.message.chat.id,message_id=call.message.message_id, reply_markup=networkcheckhist)
      except:
        bot.send_message(config.tg, text = ("Network Utilization history load error"))
    if call.data == "networkhist_1d":
      try:
        df = pd.read_csv(os.path.join(config.serverbotpathdb, "networkload.dat"), sep=";", encoding="utf-8", header=None)
        df.iloc[:,0] = pd.to_datetime(df.iloc[:,0], unit='s')
        df.iloc[:,1] = df.iloc[:,1]/1024/1024*8
        df.iloc[:,2] = df.iloc[:,2]/1024/1024*8
        period = df.iloc[:,0] > df.iloc[:,0].max() - pd.Timedelta(hours=24)
        x = df.iloc[:,0].loc[period]
        y1 = df.iloc[:,1].loc[period]
        y2 = df.iloc[:,2].loc[period]
        plt.figure(figsize=[20, 9], dpi=100)
        plt.subplot(2, 1, 1)
        plt.xlabel('Time')
        plt.ylabel('MB/s')
        plt.title('Upload speed')
        plt.grid(True)
        plt.plot(x, y1)
        plt.subplot(2, 1, 2)
        plt.xlabel('Time')
        plt.ylabel('MB/s')
        plt.title('Download speed')
        plt.grid(True)
        plt.plot(x, y2)
        plt.gcf().autofmt_xdate()
        plt.tight_layout()
        plt.savefig('/tmp/networkload.png')
        plt.close()
        networkload_24h = open('/tmp/networkload.png', 'rb')
        bot.edit_message_media(media=types.InputMedia(type='photo', media=networkload_24h),chat_id=call.message.chat.id,message_id=call.message.message_id, reply_markup=networkcheckhist)
      except:
        bot.send_message(config.tg, text = ("Network Utilization history load error"))
    if call.data == "networkhist_3d":
      try:
        df = pd.read_csv(os.path.join(config.serverbotpathdb, "networkload.dat"), sep=";", encoding="utf-8", header=None)
        df.iloc[:,0] = pd.to_datetime(df.iloc[:,0], unit='s')
        df.iloc[:,1] = df.iloc[:,1]/1024/1024*8
        df.iloc[:,2] = df.iloc[:,2]/1024/1024*8
        period = df.iloc[:,0] > df.iloc[:,0].max() - pd.Timedelta(hours=72)
        x = df.iloc[:,0].loc[period]
        y1 = df.iloc[:,1].loc[period]
        y2 = df.iloc[:,2].loc[period]
        plt.figure(figsize=[20, 9], dpi=100)
        plt.subplot(2, 1, 1)
        plt.xlabel('Time')
        plt.ylabel('MB/s')
        plt.title('Upload speed')
        plt.grid(True)
        plt.plot(x, y1)
        plt.subplot(2, 1, 2)
        plt.xlabel('Time')
        plt.ylabel('MB/s')
        plt.title('Download speed')
        plt.grid(True)
        plt.plot(x, y2)
        plt.gcf().autofmt_xdate()
        plt.tight_layout()
        plt.savefig('/tmp/networkload.png')
        plt.close()
        networkload_72h = open('/tmp/networkload.png', 'rb')
        bot.edit_message_media(media=types.InputMedia(type='photo', media=networkload_72h),chat_id=call.message.chat.id,message_id=call.message.message_id, reply_markup=networkhistmore)
      except:
        bot.send_message(config.tg, text = ("Network Utilization history load error"))
    if call.data == "networkhist_5d":
      try:
        df = pd.read_csv(os.path.join(config.serverbotpathdb, "networkload.dat"), sep=";", encoding="utf-8", header=None)
        df.iloc[:,0] = pd.to_datetime(df.iloc[:,0], unit='s')
        df.iloc[:,1] = df.iloc[:,1]/1024/1024*8
        df.iloc[:,2] = df.iloc[:,2]/1024/1024*8
        period = df.iloc[:,0] > df.iloc[:,0].max() - pd.Timedelta(hours=120)
        x = df.iloc[:,0].loc[period]
        y1 = df.iloc[:,1].loc[period]
        y2 = df.iloc[:,2].loc[period]
        plt.figure(figsize=[30, 9], dpi=100)
        plt.subplot(2, 1, 1)
        plt.xlabel('Time')
        plt.ylabel('MB/s')
        plt.title('Upload speed')
        plt.grid(True)
        plt.plot(x, y1)
        plt.subplot(2, 1, 2)
        plt.xlabel('Time')
        plt.ylabel('MB/s')
        plt.title('Download speed')
        plt.grid(True)
        plt.plot(x, y2)
        plt.gcf().autofmt_xdate()
        plt.tight_layout()
        plt.savefig('/tmp/networkload.png')
        plt.close()
        networkload_120h = open('/tmp/networkload.png', 'rb')
        bot.edit_message_media(media=types.InputMedia(type='photo', media=networkload_120h),chat_id=call.message.chat.id,message_id=call.message.message_id, reply_markup=networkhistmore)
      except:
        bot.send_message(config.tg, text = ("Network Utilization history load error"))
    if call.data == "networkhist_7d":
      try:
        df = pd.read_csv(os.path.join(config.serverbotpathdb, "networkload.dat"), sep=";", encoding="utf-8", header=None)
        df.iloc[:,0] = pd.to_datetime(df.iloc[:,0], unit='s')
        df.iloc[:,1] = df.iloc[:,1]/1024/1024*8
        df.iloc[:,2] = df.iloc[:,2]/1024/1024*8
        period = df.iloc[:,0] > df.iloc[:,0].max() - pd.Timedelta(hours=168)
        x = df.iloc[:,0].loc[period]
        y1 = df.iloc[:,1].loc[period]
        y2 = df.iloc[:,2].loc[period]
        plt.figure(figsize=[30, 9], dpi=100)
        plt.subplot(2, 1, 1)
        plt.xlabel('Time')
        plt.ylabel('MB/s')
        plt.title('Upload speed')
        plt.grid(True)
        plt.plot(x, y1)
        plt.subplot(2, 1, 2)
        plt.xlabel('Time')
        plt.ylabel('MB/s')
        plt.title('Download speed')
        plt.grid(True)
        plt.plot(x, y2)
        plt.gcf().autofmt_xdate()
        plt.tight_layout()
        plt.savefig('/tmp/networkload.png')
        plt.close()
        networkload_168h = open('/tmp/networkload.png', 'rb')
        bot.edit_message_media(media=types.InputMedia(type='photo', media=networkload_168h),chat_id=call.message.chat.id,message_id=call.message.message_id, reply_markup=networkhistmore)
      except:
        bot.send_message(config.tg, text = ("Network Utilization history load error"))
    if call.data == "networkhist_14d":
      try:
        df = pd.read_csv(os.path.join(config.serverbotpathdb, "networkload.dat"), sep=";", encoding="utf-8", header=None)
        df.iloc[:,0] = pd.to_datetime(df.iloc[:,0], unit='s')
        df.iloc[:,1] = df.iloc[:,1]/1024/1024*8
        df.iloc[:,2] = df.iloc[:,2]/1024/1024*8
        period = df.iloc[:,0] > df.iloc[:,0].max() - pd.Timedelta(hours=336)
        x = df.iloc[:,0].loc[period]
        y1 = df.iloc[:,1].loc[period]
        y2 = df.iloc[:,2].loc[period]
        plt.figure(figsize=[30, 9], dpi=100)
        plt.subplot(2, 1, 1)
        plt.xlabel('Time')
        plt.ylabel('MB/s')
        plt.title('Upload speed')
        plt.grid(True)
        plt.plot(x, y1)
        plt.subplot(2, 1, 2)
        plt.xlabel('Time')
        plt.ylabel('MB/s')
        plt.title('Download speed')
        plt.grid(True)
        plt.plot(x, y2)
        plt.gcf().autofmt_xdate()
        plt.tight_layout()
        plt.savefig('/tmp/networkload.png')
        plt.close()
        networkload_336h = open('/tmp/networkload.png', 'rb')
        bot.edit_message_media(media=types.InputMedia(type='photo', media=networkload_336h),chat_id=call.message.chat.id,message_id=call.message.message_id, reply_markup=networkhistmore)
      except:
        bot.send_message(config.tg, text = ("Network Utilization history load error"))
    if call.data == "networkhist_21d":
      try:
        df = pd.read_csv(os.path.join(config.serverbotpathdb, "networkload.dat"), sep=";", encoding="utf-8", header=None)
        df.iloc[:,0] = pd.to_datetime(df.iloc[:,0], unit='s')
        df.iloc[:,1] = df.iloc[:,1]/1024/1024*8
        df.iloc[:,2] = df.iloc[:,2]/1024/1024*8
        period = df.iloc[:,0] > df.iloc[:,0].max() - pd.Timedelta(hours=504)
        x = df.iloc[:,0].loc[period]
        y1 = df.iloc[:,1].loc[period]
        y2 = df.iloc[:,2].loc[period]
        plt.figure(figsize=[30, 9], dpi=100)
        plt.subplot(2, 1, 1)
        plt.xlabel('Time')
        plt.ylabel('MB/s')
        plt.title('Upload speed')
        plt.grid(True)
        plt.plot(x, y1)
        plt.subplot(2, 1, 2)
        plt.xlabel('Time')
        plt.ylabel('MB/s')
        plt.title('Download speed')
        plt.grid(True)
        plt.plot(x, y2)
        plt.gcf().autofmt_xdate()
        plt.tight_layout()
        plt.savefig('/tmp/networkload.png')
        plt.close()
        networkload_504h = open('/tmp/networkload.png', 'rb')
        bot.edit_message_media(media=types.InputMedia(type='photo', media=networkload_504h),chat_id=call.message.chat.id,message_id=call.message.message_id, reply_markup=networkhistmore)
      except:
        bot.send_message(config.tg, text = ("Network Utilization history load error"))
    if call.data == "networkhist_30d":
      try:
        df = pd.read_csv(os.path.join(config.serverbotpathdb, "networkload.dat"), sep=";", encoding="utf-8", header=None)
        df.iloc[:,0] = pd.to_datetime(df.iloc[:,0], unit='s')
        df.iloc[:,1] = df.iloc[:,1]/1024/1024*8
        df.iloc[:,2] = df.iloc[:,2]/1024/1024*8
        period = df.iloc[:,0] > df.iloc[:,0].max() - pd.Timedelta(hours=720)
        x = df.iloc[:,0].loc[period]
        y1 = df.iloc[:,1].loc[period]
        y2 = df.iloc[:,2].loc[period]
        plt.figure(figsize=[30, 9], dpi=100)
        plt.subplot(2, 1, 1)
        plt.xlabel('Time')
        plt.ylabel('MB/s')
        plt.title('Upload speed')
        plt.grid(True)
        plt.plot(x, y1)
        plt.subplot(2, 1, 2)
        plt.xlabel('Time')
        plt.ylabel('MB/s')
        plt.title('Download speed')
        plt.grid(True)
        plt.plot(x, y2)
        plt.gcf().autofmt_xdate()
        plt.tight_layout()
        plt.savefig('/tmp/networkload.png')
        plt.close()
        networkload_720h = open('/tmp/networkload.png', 'rb')
        bot.edit_message_media(media=types.InputMedia(type='photo', media=networkload_720h),chat_id=call.message.chat.id,message_id=call.message.message_id, reply_markup=networkhistmore)
      except:
        bot.send_message(config.tg, text = ("Network Utilization history load error"))
  # Network graph

  # diskio graph
    if call.data == "diskiocheckhist":
      bot.edit_message_reply_markup(config.tg, message_id=call.message.message_id, reply_markup=diskiocheckhist)
    if call.data == "diskiohistmore":
      bot.edit_message_reply_markup(config.tg, message_id=call.message.message_id, reply_markup=diskiohistmore)
    if call.data == "diskiohist_30m":
      try:
        df = pd.read_csv(os.path.join(config.serverbotpathdb, "diskioload.dat"), sep=";", encoding="utf-8", header=None)
        df.iloc[:,0] = pd.to_datetime(df.iloc[:,0], unit='s')
        df.iloc[:,1] = df.iloc[:,1]/1024/1024
        df.iloc[:,2] = df.iloc[:,2]/1024/1024
        period = df.iloc[:,0] > df.iloc[:,0].max() - pd.Timedelta(minutes=30)
        x = df.iloc[:,0].loc[period]
        y1 = df.iloc[:,1].loc[period]
        y2 = df.iloc[:,2].loc[period]
        plt.figure(figsize=[12, 9], dpi=100)
        plt.subplot(2, 1, 1)
        plt.xlabel('Time')
        plt.ylabel('MB/s')
        plt.title('Read')
        plt.grid(True)
        plt.plot(x, y1)
        plt.subplot(2, 1, 2)
        plt.xlabel('Time')
        plt.ylabel('MB/s')
        plt.title('Write')
        plt.grid(True)
        plt.plot(x, y2)
        plt.gcf().autofmt_xdate()
        plt.tight_layout()
        plt.savefig('/tmp/diskioload.png')
        plt.close()
        diskioload_1h = open('/tmp/diskioload.png', 'rb')
        bot.edit_message_media(media=types.InputMedia(type='photo', media=diskioload_1h),chat_id=call.message.chat.id,message_id=call.message.message_id, reply_markup=diskiocheckhist)
      except:
        bot.send_message(config.tg, text = ("Disk I/O Utilization history load error"))
    if call.data == "diskiohist_1h":
      try:
        df = pd.read_csv(os.path.join(config.serverbotpathdb, "diskioload.dat"), sep=";", encoding="utf-8", header=None)
        df.iloc[:,0] = pd.to_datetime(df.iloc[:,0], unit='s')
        df.iloc[:,1] = df.iloc[:,1]/1024/1024*8
        df.iloc[:,2] = df.iloc[:,2]/1024/1024*8
        period = df.iloc[:,0] > df.iloc[:,0].max() - pd.Timedelta(hours=1)
        x = df.iloc[:,0].loc[period]
        y1 = df.iloc[:,1].loc[period]
        y2 = df.iloc[:,2].loc[period]
        plt.figure(figsize=[15, 9], dpi=100)
        plt.subplot(2, 1, 1)
        plt.xlabel('Time')
        plt.ylabel('MB/s')
        plt.title('Read')
        plt.grid(True)
        plt.plot(x, y1)
        plt.subplot(2, 1, 2)
        plt.xlabel('Time')
        plt.ylabel('MB/s')
        plt.title('Write')
        plt.grid(True)
        plt.plot(x, y2)
        plt.gcf().autofmt_xdate()
        plt.tight_layout()
        plt.savefig('/tmp/diskioload.png')
        plt.close()
        diskioload_1h = open('/tmp/diskioload.png', 'rb')
        bot.edit_message_media(media=types.InputMedia(type='photo', media=diskioload_1h),chat_id=call.message.chat.id,message_id=call.message.message_id, reply_markup=diskiocheckhist)
      except:
        bot.send_message(config.tg, text = ("Disk I/O Utilization history load error"))
    if call.data == "diskiohist_3h":
      try:
        df = pd.read_csv(os.path.join(config.serverbotpathdb, "diskioload.dat"), sep=";", encoding="utf-8", header=None)
        df.iloc[:,0] = pd.to_datetime(df.iloc[:,0], unit='s')
        df.iloc[:,1] = df.iloc[:,1]/1024/1024*8
        df.iloc[:,2] = df.iloc[:,2]/1024/1024*8
        period = df.iloc[:,0] > df.iloc[:,0].max() - pd.Timedelta(hours=3)
        x = df.iloc[:,0].loc[period]
        y1 = df.iloc[:,1].loc[period]
        y2 = df.iloc[:,2].loc[period]
        plt.figure(figsize=[20, 9], dpi=100)
        plt.subplot(2, 1, 1)
        plt.xlabel('Time')
        plt.ylabel('MB/s')
        plt.title('Read')
        plt.grid(True)
        plt.plot(x, y1)
        plt.subplot(2, 1, 2)
        plt.xlabel('Time')
        plt.ylabel('MB/s')
        plt.title('Write')
        plt.grid(True)
        plt.plot(x, y2)
        plt.gcf().autofmt_xdate()
        plt.tight_layout()
        plt.savefig('/tmp/diskioload.png')
        plt.close()
        diskioload_3h = open('/tmp/diskioload.png', 'rb')
        bot.edit_message_media(media=types.InputMedia(type='photo', media=diskioload_3h),chat_id=call.message.chat.id,message_id=call.message.message_id, reply_markup=diskiocheckhist)
      except:
        bot.send_message(config.tg, text = ("Disk I/O Utilization history load error"))
    if call.data == "diskiohist_6h":
      try:
        df = pd.read_csv(os.path.join(config.serverbotpathdb, "diskioload.dat"), sep=";", encoding="utf-8", header=None)
        df.iloc[:,0] = pd.to_datetime(df.iloc[:,0], unit='s')
        df.iloc[:,1] = df.iloc[:,1]/1024/1024*8
        df.iloc[:,2] = df.iloc[:,2]/1024/1024*8
        period = df.iloc[:,0] > df.iloc[:,0].max() - pd.Timedelta(hours=6)
        x = df.iloc[:,0].loc[period]
        y1 = df.iloc[:,1].loc[period]
        y2 = df.iloc[:,2].loc[period]
        plt.figure(figsize=[20, 9], dpi=100)
        plt.subplot(2, 1, 1)
        plt.xlabel('Time')
        plt.ylabel('MB/s')
        plt.title('Read')
        plt.grid(True)
        plt.plot(x, y1)
        plt.subplot(2, 1, 2)
        plt.xlabel('Time')
        plt.ylabel('MB/s')
        plt.title('Write')
        plt.grid(True)
        plt.plot(x, y2)
        plt.gcf().autofmt_xdate()
        plt.tight_layout()
        plt.savefig('/tmp/diskioload.png')
        plt.close()
        diskioload_6h = open('/tmp/diskioload.png', 'rb')
        bot.edit_message_media(media=types.InputMedia(type='photo', media=diskioload_6h),chat_id=call.message.chat.id,message_id=call.message.message_id, reply_markup=diskiocheckhist)
      except:
        bot.send_message(config.tg, text = ("Disk I/O Utilization history load error"))
    if call.data == "diskiohist_12h":
      try:
        df = pd.read_csv(os.path.join(config.serverbotpathdb, "diskioload.dat"), sep=";", encoding="utf-8", header=None)
        df.iloc[:,0] = pd.to_datetime(df.iloc[:,0], unit='s')
        df.iloc[:,1] = df.iloc[:,1]/1024/1024*8
        df.iloc[:,2] = df.iloc[:,2]/1024/1024*8
        period = df.iloc[:,0] > df.iloc[:,0].max() - pd.Timedelta(hours=12)
        x = df.iloc[:,0].loc[period]
        y1 = df.iloc[:,1].loc[period]
        y2 = df.iloc[:,2].loc[period]
        plt.figure(figsize=[20, 9], dpi=100)
        plt.subplot(2, 1, 1)
        plt.xlabel('Time')
        plt.ylabel('MB/s')
        plt.title('Read')
        plt.grid(True)
        plt.plot(x, y1)
        plt.subplot(2, 1, 2)
        plt.xlabel('Time')
        plt.ylabel('MB/s')
        plt.title('Write')
        plt.grid(True)
        plt.plot(x, y2)
        plt.gcf().autofmt_xdate()
        plt.tight_layout()
        plt.savefig('/tmp/diskioload.png')
        plt.close()
        diskioload_12h = open('/tmp/diskioload.png', 'rb')
        bot.edit_message_media(media=types.InputMedia(type='photo', media=diskioload_12h),chat_id=call.message.chat.id,message_id=call.message.message_id, reply_markup=diskiocheckhist)
      except:
        bot.send_message(config.tg, text = ("Disk I/O Utilization history load error"))
    if call.data == "diskiohist_1d":
      try:
        df = pd.read_csv(os.path.join(config.serverbotpathdb, "diskioload.dat"), sep=";", encoding="utf-8", header=None)
        df.iloc[:,0] = pd.to_datetime(df.iloc[:,0], unit='s')
        df.iloc[:,1] = df.iloc[:,1]/1024/1024*8
        df.iloc[:,2] = df.iloc[:,2]/1024/1024*8
        period = df.iloc[:,0] > df.iloc[:,0].max() - pd.Timedelta(hours=24)
        x = df.iloc[:,0].loc[period]
        y1 = df.iloc[:,1].loc[period]
        y2 = df.iloc[:,2].loc[period]
        plt.figure(figsize=[20, 9], dpi=100)
        plt.subplot(2, 1, 1)
        plt.xlabel('Time')
        plt.ylabel('MB/s')
        plt.title('Read')
        plt.grid(True)
        plt.plot(x, y1)
        plt.subplot(2, 1, 2)
        plt.xlabel('Time')
        plt.ylabel('MB/s')
        plt.title('Write')
        plt.grid(True)
        plt.plot(x, y2)
        plt.gcf().autofmt_xdate()
        plt.tight_layout()
        plt.savefig('/tmp/diskioload.png')
        plt.close()
        diskioload_24h = open('/tmp/diskioload.png', 'rb')
        bot.edit_message_media(media=types.InputMedia(type='photo', media=diskioload_24h),chat_id=call.message.chat.id,message_id=call.message.message_id, reply_markup=diskiocheckhist)
      except:
        bot.send_message(config.tg, text = ("Disk I/O Utilization history load error"))
    if call.data == "diskiohist_3d":
      try:
        df = pd.read_csv(os.path.join(config.serverbotpathdb, "diskioload.dat"), sep=";", encoding="utf-8", header=None)
        df.iloc[:,0] = pd.to_datetime(df.iloc[:,0], unit='s')
        df.iloc[:,1] = df.iloc[:,1]/1024/1024*8
        df.iloc[:,2] = df.iloc[:,2]/1024/1024*8
        period = df.iloc[:,0] > df.iloc[:,0].max() - pd.Timedelta(hours=72)
        x = df.iloc[:,0].loc[period]
        y1 = df.iloc[:,1].loc[period]
        y2 = df.iloc[:,2].loc[period]
        plt.figure(figsize=[20, 9], dpi=100)
        plt.subplot(2, 1, 1)
        plt.xlabel('Time')
        plt.ylabel('MB/s')
        plt.title('Read')
        plt.grid(True)
        plt.plot(x, y1)
        plt.subplot(2, 1, 2)
        plt.xlabel('Time')
        plt.ylabel('MB/s')
        plt.title('Write')
        plt.grid(True)
        plt.plot(x, y2)
        plt.gcf().autofmt_xdate()
        plt.tight_layout()
        plt.savefig('/tmp/diskioload.png')
        plt.close()
        diskioload_72h = open('/tmp/diskioload.png', 'rb')
        bot.edit_message_media(media=types.InputMedia(type='photo', media=diskioload_72h),chat_id=call.message.chat.id,message_id=call.message.message_id, reply_markup=diskiohistmore)
      except:
        bot.send_message(config.tg, text = ("Disk I/O Utilization history load error"))
    if call.data == "diskiohist_5d":
      try:
        df = pd.read_csv(os.path.join(config.serverbotpathdb, "diskioload.dat"), sep=";", encoding="utf-8", header=None)
        df.iloc[:,0] = pd.to_datetime(df.iloc[:,0], unit='s')
        df.iloc[:,1] = df.iloc[:,1]/1024/1024*8
        df.iloc[:,2] = df.iloc[:,2]/1024/1024*8
        period = df.iloc[:,0] > df.iloc[:,0].max() - pd.Timedelta(hours=120)
        x = df.iloc[:,0].loc[period]
        y1 = df.iloc[:,1].loc[period]
        y2 = df.iloc[:,2].loc[period]
        plt.figure(figsize=[30, 9], dpi=100)
        plt.subplot(2, 1, 1)
        plt.xlabel('Time')
        plt.ylabel('MB/s')
        plt.title('Read')
        plt.grid(True)
        plt.plot(x, y1)
        plt.subplot(2, 1, 2)
        plt.xlabel('Time')
        plt.ylabel('MB/s')
        plt.title('Write')
        plt.grid(True)
        plt.plot(x, y2)
        plt.gcf().autofmt_xdate()
        plt.tight_layout()
        plt.savefig('/tmp/diskioload.png')
        plt.close()
        diskioload_120h = open('/tmp/diskioload.png', 'rb')
        bot.edit_message_media(media=types.InputMedia(type='photo', media=diskioload_120h),chat_id=call.message.chat.id,message_id=call.message.message_id, reply_markup=diskiohistmore)
      except:
        bot.send_message(config.tg, text = ("Disk I/O Utilization history load error"))
    if call.data == "diskiohist_7d":
      try:
        df = pd.read_csv(os.path.join(config.serverbotpathdb, "diskioload.dat"), sep=";", encoding="utf-8", header=None)
        df.iloc[:,0] = pd.to_datetime(df.iloc[:,0], unit='s')
        df.iloc[:,1] = df.iloc[:,1]/1024/1024*8
        df.iloc[:,2] = df.iloc[:,2]/1024/1024*8
        period = df.iloc[:,0] > df.iloc[:,0].max() - pd.Timedelta(hours=168)
        x = df.iloc[:,0].loc[period]
        y1 = df.iloc[:,1].loc[period]
        y2 = df.iloc[:,2].loc[period]
        plt.figure(figsize=[30, 9], dpi=100)
        plt.subplot(2, 1, 1)
        plt.xlabel('Time')
        plt.ylabel('MB/s')
        plt.title('Read')
        plt.grid(True)
        plt.plot(x, y1)
        plt.subplot(2, 1, 2)
        plt.xlabel('Time')
        plt.ylabel('MB/s')
        plt.title('Write')
        plt.grid(True)
        plt.plot(x, y2)
        plt.gcf().autofmt_xdate()
        plt.tight_layout()
        plt.savefig('/tmp/diskioload.png')
        plt.close()
        diskioload_168h = open('/tmp/diskioload.png', 'rb')
        bot.edit_message_media(media=types.InputMedia(type='photo', media=diskioload_168h),chat_id=call.message.chat.id,message_id=call.message.message_id, reply_markup=diskiohistmore)
      except:
        bot.send_message(config.tg, text = ("Disk I/O Utilization history load error"))
    if call.data == "diskiohist_14d":
      try:
        df = pd.read_csv(os.path.join(config.serverbotpathdb, "diskioload.dat"), sep=";", encoding="utf-8", header=None)
        df.iloc[:,0] = pd.to_datetime(df.iloc[:,0], unit='s')
        df.iloc[:,1] = df.iloc[:,1]/1024/1024*8
        df.iloc[:,2] = df.iloc[:,2]/1024/1024*8
        period = df.iloc[:,0] > df.iloc[:,0].max() - pd.Timedelta(hours=336)
        x = df.iloc[:,0].loc[period]
        y1 = df.iloc[:,1].loc[period]
        y2 = df.iloc[:,2].loc[period]
        plt.figure(figsize=[30, 9], dpi=100)
        plt.subplot(2, 1, 1)
        plt.xlabel('Time')
        plt.ylabel('MB/s')
        plt.title('Read')
        plt.grid(True)
        plt.plot(x, y1)
        plt.subplot(2, 1, 2)
        plt.xlabel('Time')
        plt.ylabel('MB/s')
        plt.title('Write')
        plt.grid(True)
        plt.plot(x, y2)
        plt.gcf().autofmt_xdate()
        plt.tight_layout()
        plt.savefig('/tmp/diskioload.png')
        plt.close()
        diskioload_336h = open('/tmp/diskioload.png', 'rb')
        bot.edit_message_media(media=types.InputMedia(type='photo', media=diskioload_336h),chat_id=call.message.chat.id,message_id=call.message.message_id, reply_markup=diskiohistmore)
      except:
        bot.send_message(config.tg, text = ("Disk I/O Utilization history load error"))
    if call.data == "diskiohist_21d":
      try:
        df = pd.read_csv(os.path.join(config.serverbotpathdb, "diskioload.dat"), sep=";", encoding="utf-8", header=None)
        df.iloc[:,0] = pd.to_datetime(df.iloc[:,0], unit='s')
        df.iloc[:,1] = df.iloc[:,1]/1024/1024*8
        df.iloc[:,2] = df.iloc[:,2]/1024/1024*8
        period = df.iloc[:,0] > df.iloc[:,0].max() - pd.Timedelta(hours=504)
        x = df.iloc[:,0].loc[period]
        y1 = df.iloc[:,1].loc[period]
        y2 = df.iloc[:,2].loc[period]
        plt.figure(figsize=[30, 9], dpi=100)
        plt.subplot(2, 1, 1)
        plt.xlabel('Time')
        plt.ylabel('MB/s')
        plt.title('Read')
        plt.grid(True)
        plt.plot(x, y1)
        plt.subplot(2, 1, 2)
        plt.xlabel('Time')
        plt.ylabel('MB/s')
        plt.title('Write')
        plt.grid(True)
        plt.plot(x, y2)
        plt.gcf().autofmt_xdate()
        plt.tight_layout()
        plt.savefig('/tmp/diskioload.png')
        plt.close()
        diskioload_504h = open('/tmp/diskioload.png', 'rb')
        bot.edit_message_media(media=types.InputMedia(type='photo', media=diskioload_504h),chat_id=call.message.chat.id,message_id=call.message.message_id, reply_markup=diskiohistmore)
      except:
        bot.send_message(config.tg, text = ("Disk I/O Utilization history load error"))
    if call.data == "diskiohist_30d":
      try:
        df = pd.read_csv(os.path.join(config.serverbotpathdb, "diskioload.dat"), sep=";", encoding="utf-8", header=None)
        df.iloc[:,0] = pd.to_datetime(df.iloc[:,0], unit='s')
        df.iloc[:,1] = df.iloc[:,1]/1024/1024*8
        df.iloc[:,2] = df.iloc[:,2]/1024/1024*8
        period = df.iloc[:,0] > df.iloc[:,0].max() - pd.Timedelta(hours=720)
        x = df.iloc[:,0].loc[period]
        y1 = df.iloc[:,1].loc[period]
        y2 = df.iloc[:,2].loc[period]
        plt.figure(figsize=[30, 9], dpi=100)
        plt.subplot(2, 1, 1)
        plt.xlabel('Time')
        plt.ylabel('MB/s')
        plt.title('Read')
        plt.grid(True)
        plt.plot(x, y1)
        plt.subplot(2, 1, 2)
        plt.xlabel('Time')
        plt.ylabel('MB/s')
        plt.title('Write')
        plt.grid(True)
        plt.plot(x, y2)
        plt.gcf().autofmt_xdate()
        plt.tight_layout()
        plt.savefig('/tmp/diskioload.png')
        plt.close()
        diskioload_720h = open('/tmp/diskioload.png', 'rb')
        bot.edit_message_media(media=types.InputMedia(type='photo', media=diskioload_720h),chat_id=call.message.chat.id,message_id=call.message.message_id, reply_markup=diskiohistmore)
      except:
        bot.send_message(config.tg, text = ("Disk I/O Utilization history load error"))
    if call.data == "container_load_hist_3h":
        dockerGetInfo(180)
        container_run = open('/tmp/containerRunCounts.png', 'rb')
        try :
            bot.edit_message_media(media=types.InputMedia(type='photo', media=container_run),chat_id=call.message.chat.id,message_id=call.message.message_id, reply_markup=container_load_hist)
        except Exception as e:
            bot.send_message(config.tg, text=(e))
    if call.data == "container_load_hist_6h":
        dockerGetInfo(360)
        container_run = open('/tmp/containerRunCounts.png', 'rb')
        try :
            bot.edit_message_media(media=types.InputMedia(type='photo', media=container_run),chat_id=call.message.chat.id,message_id=call.message.message_id, reply_markup=container_load_hist)
        except Exception as e:
            bot.send_message(config.tg, text=(e))
    if call.data == "container_load_hist_12h":
        dockerGetInfo(720)
        container_run = open('/tmp/containerRunCounts.png', 'rb')
        try :
            bot.edit_message_media(media=types.InputMedia(type='photo', media=container_run),chat_id=call.message.chat.id,message_id=call.message.message_id, reply_markup=container_load_hist)
        except Exception as e:
            bot.send_message(config.tg, text=(e))
    if call.data == "container_load_hist_24h":
        dockerGetInfo(1440)
        container_run = open('/tmp/containerRunCounts.png', 'rb')
        try :
            bot.edit_message_media(media=types.InputMedia(type='photo', media=container_run),chat_id=call.message.chat.id,message_id=call.message.message_id, reply_markup=container_load_hist)
        except Exception as e:
            bot.send_message(config.tg, text=(e))
    if call.data == "container_load_hist_3d":
        dockerGetInfo(4320)
        container_run = open('/tmp/containerRunCounts.png', 'rb')
        try :
            bot.edit_message_media(media=types.InputMedia(type='photo', media=container_run),chat_id=call.message.chat.id,message_id=call.message.message_id, reply_markup=container_load_hist)
        except Exception as e:
            bot.send_message(config.tg, text=(e))
    if call.data == "container_load_hist__10d":
        dockerGetInfo(43200)
        container_run = open('/tmp/containerRunCounts.png', 'rb')
        try :
            bot.edit_message_media(media=types.InputMedia(type='photo', media=container_run),chat_id=call.message.chat.id,message_id=call.message.message_id, reply_markup=container_load_hist)
        except Exception as e:
            bot.send_message(config.tg, text=(e))
    if call.data == "container_load_hist_30d":
        dockerGetInfo(129600)
        container_run = open('/tmp/containerRunCounts.png', 'rb')
        try :
            bot.edit_message_media(media=types.InputMedia(type='photo', media=container_run),chat_id=call.message.chat.id,message_id=call.message.message_id, reply_markup=container_load_hist)
        except Exception as e:
            bot.send_message(config.tg, text=(e))
  # diskio graph

#######################################################
# Docker container
# Docker container start
@bot.message_handler(func=lambda message: message.text == lt_docker_container)
def command_linuxtools(message):
    try :
        if message.from_user.id == config.tg:
            result = run(["docker", "ps"], stdout=PIPE, stderr=PIPE, universal_newlines=True)
            error_msg = ""
            if not str(result.stderr) == "" :
                error_msg += "\nError : \n" + str(result.stderr)
            result = str(result.stdout)
            dockerGetInfo(60)
            container_run = open('/tmp/containerRunCounts.png', 'rb')
            bot.send_photo(config.tg, container_run, reply_markup=container_load_hist)
    except Exception as e:
        bot.send_message(config.tg, text=(e))

# get docker info in the specified datetime
def dockerGetInfo(range_time) :
    # now time
    now_time = time.time()
    # range time is based on minute
    range_time = now_time - (range_time * 60)
    db_file = open(os.path.join(config.serverbotpathdb, "dockerContainer.dat"), "r")
    docker_info_history = json.load(db_file)
    # count each metrics of the numbers of containers were running and not running
    each_metrics_count_run = []
    each_metrics_count_not_run = []
    each_metrics_time = []
    # each info include multiple containers
    for each_info in docker_info_history :
        # key is the time found this metrics
        for key in each_info.keys() :
            # this container info was found in the requested range time
            if float(key) >= float(range_time) :
                # number of running containers in a metric
                count_run = 0
                count_not_run = 0
                # count this metrics
                for each_container in each_info[key] :
                    each_container = each_container.split(" ")
                    # the container name
                    each_container_name = each_container[0]
                    # the container running, true or false
                    each_container_running = each_container[1]
                    # if running, count + 1
                    if each_container_running == "True" :
                        count_run += 1
                    # else means the container is not running
                    else :
                        count_not_run += 1
                # save metrics which are in the range to make the plot
                each_metrics_count_run.append(count_run)
                each_metrics_count_not_run.append(count_not_run)
                timestamp = dt.fromtimestamp(float(key))
                formatted_time = timestamp.strftime('%Y-%m-%d %H:%M')
                each_metrics_time.append(formatted_time)
    db_file.close()
    # make the plot with metrics
    dockerSaveImg(each_metrics_count_run, each_metrics_time, each_metrics_count_not_run)

# make the plot with metrics and save the image
def dockerSaveImg(each_metrics_count_run, each_metrics_time, each_metrics_count_not_run) :
    plt.title("Docker container Running(blue) and Not Running(orange) Numbers")
    plt.xlabel("time")
    plt.ylabel("counts")
    plt.grid(True)
    # count the container is running
    plt.plot(each_metrics_time, each_metrics_count_run)
    # count the container is not running
    plt.plot(each_metrics_time, each_metrics_count_not_run, "--")
    # make the datetime show only ten times
    interval_date = len(each_metrics_time) // 100
    # when the data number is less than 100
    if interval_date == 0 :
        interval_date = 1
    plt.gca().xaxis.set_major_locator(mdates.DayLocator(interval=interval_date))
    plt.gcf().autofmt_xdate()
    plt.tight_layout()
    plt.savefig('/tmp/containerRunCounts.png')
    plt.close()

#######################################################
# Linux tools

# Linux tools start
@bot.message_handler(func=lambda message: message.text == lt_linuxtools)
def command_linuxtools(message):
  if message.from_user.id == config.tg:
    bot.send_message(config.tg, text=("Slowly, slowly, some processes need time. ") + "\U000023F3", reply_markup=markuplinux)
  else:
    pass
# /Linux tools start

# Ping test
@bot.message_handler(func=lambda message: message.text == lt_ping)
def command_pingcheck(message):
  if message.from_user.id == config.tg:
    try:
      bot.send_chat_action(config.tg, "typing")
      pingcheck = "ping -c 5 " + config.srvping
      pingcheck = str(subprocess.check_output(pingcheck, shell = True,encoding='utf-8'))
      bot.send_message(config.tg, text=pingcheck, reply_markup=markuplinux)
      historygetping("db/pingcheck.dat",30,("ms"),("Ping test"),"/tmp/pingcheck.png",pingcheckhist)
    except:
      bot.send_message(config.tg, text=("Can't execute ping test"), reply_markup=markuplinux)
  else:
    pass
# /Ping test

# Traceroute test
@bot.message_handler(func=lambda message: message.text == lt_traceroute)
def command_traceroutecheck(message):
  if message.from_user.id == config.tg:
    try:
      bot.send_chat_action(config.tg, "typing")
      bot.send_chat_action(config.tg, "typing")
      traceroutecheck = "traceroute " + config.traceroutetest
      traceroutecheck = str(subprocess.check_output(traceroutecheck, shell = True,encoding='utf-8'))
      bot.send_message(config.tg, text=traceroutecheck, reply_markup=markuplinux)
    except:
      bot.send_message(config.tg, text=("Can't execute traceroute, try to change ip or server in config"), reply_markup=markuplinux)
  else:
    pass
# /Traceroute test

# Top processes
@bot.message_handler(func=lambda message: message.text == lt_topproc)
def command_timediff(message):
  if message.from_user.id == config.tg:
    try:
      topps = "ps -eo pid,ppid,user,start,%mem,pcpu,cmd --sort=-%mem | head"
      topps = str(subprocess.check_output(topps, shell = True,encoding='utf-8'))
      bot.send_message(config.tg, text=topps, reply_markup=markuplinux)
    except:
      bot.send_message(config.tg, text=("Can't get top processes"), reply_markup=markuplinux)
  else:
    pass
# /Top processes

# Server start date/time
@bot.message_handler(func=lambda message: message.text == lt_starttime)
def command_srvstart(message):
  if message.from_user.id == config.tg:
    try:
      startt = ("System start: ") + str(datetime.datetime.fromtimestamp(psutil.boot_time()).strftime("%b/%d/%Y %H:%M:%S"))
      bot.send_message(config.tg, text=startt, reply_markup=markuplinux)
    except:
      bot.send_message(config.tg, text=("Can't get system start date"), reply_markup=markuplinux)
  else:
    pass
# /Server start date/time

# Current network load
@bot.message_handler(func=lambda message: message.text == lt_currntwrkload)
def command_currntwrkload(message):
  if message.from_user.id == config.tg:
    try:
      bot.send_chat_action(config.tg, "typing")
      currentloadn = psutil.net_io_counters()
      bytes_sent = getattr(currentloadn, 'bytes_sent')
      bytes_recv = getattr(currentloadn, 'bytes_recv')
      time.sleep(1)
      currentloadn1 = psutil.net_io_counters()
      bytes_sent1 = getattr(currentloadn1, 'bytes_sent')
      bytes_recv1 = getattr(currentloadn1, 'bytes_recv')
      sentspd = (bytes_sent1-bytes_sent)/1024/1024*8
      recvspd = (bytes_recv1-bytes_recv)/1024/1024*8
      sentspd = str((round(sentspd, 2)))
      recvspd = str((round(recvspd, 2)))
      bot.send_message(config.tg, text=("*Current network load\nIncoming:* _") + recvspd + (" Mb/s_\n*Outgoing:* _") + sentspd + (" Mb/s_"), parse_mode="Markdown", reply_markup=markuplinux)
      historygetnb("db/networkload.dat",0.5,("Mb/s"),("Upload"),("Download"),"/tmp/networkload.png",networkcheckhist)
    except:
      bot.send_message(config.tg, text=("Can't get current network load"), parse_mode="Markdown", reply_markup=markuplinux)
  else:
    pass
# /Current network load

# Disk I/O
@bot.message_handler(func=lambda message: message.text == lt_currntdiskload)
def command_currdiskload(message):
  if message.from_user.id == config.tg:
    try:
      bot.send_chat_action(config.tg, "typing")
      currentloadd = psutil.disk_io_counters()
      bytes_read = getattr(currentloadd, 'read_bytes')
      bytes_writ = getattr(currentloadd, 'write_bytes')
      time.sleep(1)
      currentloadd1 = psutil.disk_io_counters()
      bytes_read1 = getattr(currentloadd1, 'read_bytes')
      bytes_writ1 = getattr(currentloadd1, 'write_bytes')
      readio = (bytes_read1-bytes_read)/1024/1024
      writio = (bytes_writ1-bytes_writ)/1024/1024
      readio = str((round(readio, 2)))
      writio = str((round(writio, 2)))
      bot.send_message(config.tg, text=("*Current disk load\nRead:* _") + readio + (" MB/s_\n*Write:* _") + writio + (" MB/s_"), parse_mode="Markdown")
      historygetdio("db/diskioload.dat",0.5,("MB/s"),("Read"),("Write"),"/tmp/diskioload.png",diskiocheckhist)
    except:
      bot.send_message(config.tg, text=("Can't get current disk load"), parse_mode="Markdown")
  else:
    pass
# /Disk I/O

# /Linux tools
#######################################################

# Network speedtest
@bot.message_handler(func=lambda message: message.text == lt_spdtst)
def command_testspeed(message):
  if message.from_user.id == config.tg:
    try:
      bot.send_chat_action(config.tg, "typing")
      testspeedcmd = "python3 " + config.serverbotpath + "/speedtest-cli --share | grep -i 'Share results' | awk '{print $3}' | wget -i - -O /tmp/speedtestcheck.png"
      testspeed =str(subprocess.call(testspeedcmd, shell = True,encoding='utf-8'))
      bot.send_chat_action(config.tg, "upload_photo")
      testspeedfile = open('/tmp/speedtestcheck.png', 'rb')
      bot.send_photo(config.tg, testspeedfile)
    except:
      bot.send_message(config.tg, text=("Speed test failed"))
  else:
    pass
# Network speedtest end

# Main menu
@bot.message_handler(func=lambda message: message.text == lt_mainmenu)
def command_srvstart(message):
  if message.from_user.id == config.tg:
    bot.send_message(config.tg, text=("Start menu"), reply_markup=markup)
  else:
    pass
# /Main menu

# Except proc kill
def kill(proc_pid):
  process = psutil.Process(proc_pid)
  for proc in process.children(recursive=True):
    proc.kill()
  process.kill()

# Validator node monitoring
def AlertsNotificationsNode():
  td = 0
  alrtprdnode = 5
  while True:
    if td == 5:
      td = 0
      # Check validator node running
      try:
        valnodecheck = str(subprocess.check_output(["pidof ", nearpid], encoding='utf-8'))
        alrtprdnode =5
      except subprocess.CalledProcessError as i:
        if i.output != None:
          if alrtprdnode in config.repeattimealarmnode:
            try:
              bot.send_message(config.tg, text="\U0001F6A8 " + ("Near node is not running."))
              time.sleep(2)
            except:
              pass
            alrtprdnode +=5
          else:
            alrtprdnode +=5
    time.sleep(5)
    td += 5

# NEAR Node sync monitoring
def AlertsNotificationsSync():
  td = 0
  alrtprdsync = 5
  while True:
    if td == 5:
      try:
        td = 0
#        netcurlrequest = str("curl -s " + "https://rpc." + config.nearnetwork + ".near.org/status | jq .sync_info.latest_block_height")
        netcurlrequest = str("curl -s " + rpcurl + "/status | jq .sync_info.latest_block_height")
        netblockheight = int(subprocess.check_output([netcurlrequest], shell = True,encoding='utf-8'))
        localblockheight = str(subprocess.check_output(["curl -s http://127.0.0.1:3030/status | jq .sync_info.latest_block_height"], shell = True, encoding='utf-8'))
        localblockheight = localblockheight or 1
        syncdiff = int(netblockheight - localblockheight)
#        with open(os.path.join(config.tontgpathdb, "sync.dat"), "a") as i:
#          i.write(str(int(time.time())) + ";" + netblockheight + localblockheight + syncdiff + "\n")
        if int(float(syncdiff)) >= config.syncalarm:
          if alrtprdsync in config.repeattimealarmnode:
            try:
                bot.send_message(config.tg,"\U0001F6A8 " + ("Node out of sync ") + str(syncdiff) + (" blocks behind") )
            except:
              pass
            alrtprdsync +=5
          else:
            alrtprdsync +=5
        if int(float(syncdiff)) < config.syncalarm:
          alrtprdsync = 5
        time.sleep(5)
        td += 5
      except:
        time.sleep(5)
        td += 5
    else:
      time.sleep(5)
      td += 5

# NEAR Blocks pruduce monitoring
def AlertsNotificationsBlocks():
  td = 0
  alrtprdblocks = 30
  while True:
    if td == 30:
      try:
        td = 0
        values = '{"jsonrpc": "2.0", "method": "validators", "id": "dontcare", "params": [null]}'
        session = requests.Session()
        H = {"Content-Type": "application/json"}
        response = session.post(rpcurl, values, headers = H)#
        response_text = response.text
        json_str = response_text.replace("'", "\"")
        json_main = json.loads(json_str)
        level_one = json_main["result"]
        level_two = level_one["current_validators"]
        accounts_list = []
        target_account = config.poolname
        for item in level_two:
            account_id = item['account_id']
            if account_id == target_account:
                num_produced_blocks = item["num_produced_blocks"]
                num_expected_blocks = item["num_expected_blocks"]
                num_produced_chunks = item["num_produced_chunks"]
                num_expected_chunks = item["num_expected_chunks"]
                blocksdiff = num_expected_blocks - num_produced_blocks
                chunksdiff = num_expected_chunks - num_produced_chunks
        # History data
        with open(os.path.join(config.serverbotpathdb, "blocks.dat"), "a") as i:
            i.write(str(int(time.time())) + ";" + str(int(num_produced_blocks)) + ";" + str(int(num_expected_blocks)) + ";" + str(int(blocksdiff)) + "\n")
        # Alert blocks
        if int(float(blocksdiff)) >= config.blocksdiff:
          if alrtprdblocks in config.repeattimealarmnode:
            try:
                bot.send_message(config.tg,"\U0001F6A8 " + str(blocksdiff) + ("blocks pruduced less than expected !!! "))
            except:
              pass
            alrtprdblocks +=30
          else:
            alrtprdblocks +=30
        if int(float(blocksdiff)) < config.blocksdiff:
          alrtprdblocks = 30
        time.sleep(30)
        td += 30
      except:
        time.sleep(30)
        td += 30
    else:
      time.sleep(30)
      td += 30

# NEAR Chunks pruduce monitoring
def AlertsNotificationsChunks():
  td = 0
  alrtprdchunks = 30
  while True:
    if td == 30:
      try:
        td = 0
        values = '{"jsonrpc": "2.0", "method": "validators", "id": "dontcare", "params": [null]}'
        session = requests.Session()
        H = {"Content-Type": "application/json"}
        response = session.post(rpcurl, values, headers = H)#
        response_text = response.text
        json_str = response_text.replace("'", "\"")
        json_main = json.loads(json_str)
        level_one = json_main["result"]
        level_two = level_one["current_validators"]
        accounts_list = []
        target_account = config.poolname
        for item in level_two:
            account_id = item['account_id']
            if account_id == target_account:
                num_produced_blocks = item["num_produced_blocks"]
                num_expected_blocks = item["num_expected_blocks"]
                num_produced_chunks = item["num_produced_chunks"]
                num_expected_chunks = item["num_expected_chunks"]
                blocksdiff = num_expected_blocks - num_produced_blocks
                chunksdiff = num_expected_chunks - num_produced_chunks
        # History data
        with open(os.path.join(config.serverbotpathdb, "chunks.dat"), "a") as i:
            i.write(str(int(time.time())) + ";" + str(int(num_produced_chunks)) + ";" + str(int(num_expected_chunks)) + ";" + str(int(chunksdiff)) + "\n")
        # Alert chunks
        if int(float(chunksdiff)) >= config.chunksdiff:
          if alrtprdchunks in config.repeattimealarmnode:
            try:
                bot.send_message(config.tg,"\U0001F6A8 " + str(chunksdiff) + ("chunks pruduced less than expected !!! "))
            except:
              pass
            alrtprdchunks +=30
          else:
            alrtprdchunks +=30
        if int(float(chunksdiff)) < config.chunksdiff:
          alrtprdchunks = 30
        time.sleep(30)
        td += 30
      except:
        time.sleep(30)
        td += 30
    else:
      time.sleep(30)
      td += 30

# RAM Monitoring
def AlertsNotificationsRam():
  td = 0
  alrtprdmem = 5
  while True:
    if td == 5:
      try:
        td = 0
        memload = "free -m | grep Mem | awk '/Mem/{used=$3} /Mem/{total=$2} END {printf (used*100)/total}'"
        memload = str(subprocess.check_output(memload, shell = True, encoding='utf-8'))
        # History data
        with open(os.path.join(config.serverbotpathdb, "ramload.dat"), "a") as i:
          i.write(str(int(time.time())) + ";" + memload + "\n")
        # Notification
        if int(float(memload)) >= config.memloadalarm:
          if alrtprdmem in config.repeattimealarmsrv:
            try:
              bot.send_message(config.tg, text="\U0001F6A8 " + ("High memory load! ") + memload,  parse_mode="Markdown")
            except:
              pass
            alrtprdmem +=5
          else:
            alrtprdmem +=5
        if int(float(memload)) < config.memloadalarm:
          alrtprdmem = 5
        time.sleep(5)
        td += 5
      except:
        time.sleep(5)
        td += 5
    else:
      time.sleep(5)
      td += 5

# CPU Monitoring
def AlertsNotificationsCPU():
  td = 0
  alrtprdcpu = 5
  while True:
    if td == 5:
      try:
        td = 0
        cpuutilalert = str(psutil.cpu_percent())
        with open(os.path.join(config.serverbotpathdb, "cpuload.dat"), "a") as i:
          i.write(str(int(time.time())) + ";" + cpuutilalert + "\n")
        if int(float(cpuutilalert)) >= config.cpuutilalarm:
          if alrtprdcpu in config.repeattimealarmsrv:
            try:
              bot.send_message(config.tg,"\U000026A1" + ("High CPU Utilization! ") + cpuutilalert + "%")
            except:
              pass
            alrtprdcpu +=5
          else:
            alrtprdcpu +=5
        if int(float(cpuutilalert)) < config.cpuutilalarm:
          alrtprdcpu = 5
        time.sleep(5)
        td += 5
      except:
        time.sleep(5)
        td += 5
    else:
      time.sleep(5)
      td += 5

# Ping Monitoring
def AlertsNotificationsping():
  td = 0
  alrtprdpng = 5
  while True:
    if td == 5:
      try:
        td = 0
        pingc = "ping -c 1 " + config.srvping + " | tail -1 | awk '{printf $4}' | cut -d '/' -f 1 | tr -d $'\n'"
        pingc = str(subprocess.check_output(pingc, shell = True, encoding='utf-8'))
        with open(os.path.join(config.serverbotpathdb, "pingcheck.dat"), "a") as i:
          i.write(str(int(time.time())) + ";" + pingc + "\n")
        if int(float(pingc)) >= config.pingcalarm:
          if alrtprdpng in config.repeattimealarmsrv:
            try:
              bot.send_message(config.tg,"\U000026A1 " + ("High ping! ") + pingc + " ms")
            except:
              pass
            alrtprdpng +=5
          else:
            alrtprdpng +=5
        if int(float(pingc)) < config.pingcalarm:
          alrtprdpng = 5
        time.sleep(5)
        td += 5
      except:
        time.sleep(5)
        td += 5
    else:
      time.sleep(5)
      td += 5

# Network Monitoring
def monitoringnetwork():
  td = 0
  while True:
    if td == 5:
      td = 0
      try:
        currentloadn = psutil.net_io_counters()
        bytes_sent = getattr(currentloadn, 'bytes_sent')
        bytes_recv = getattr(currentloadn, 'bytes_recv')
        time.sleep(1)
        currentloadn1 = psutil.net_io_counters()
        bytes_sent1 = getattr(currentloadn1, 'bytes_sent')
        bytes_recv1 = getattr(currentloadn1, 'bytes_recv')
        sentspd = (bytes_sent1-bytes_sent)
        recvspd = (bytes_recv1-bytes_recv)
        with open(os.path.join(config.serverbotpathdb, "networkload.dat"), "a") as i:
          i.write(str(int(time.time())) + ";" + str(int(sentspd)) + ";" + str(int(recvspd)) + "\n")
      except:
        pass
    else:
      time.sleep(4)
      td += 5

# Disk monitoring
def monitoringdiskio():
  td = 0
  while True:
    if td == 5:
      td = 0
      try:
        currentloadd = psutil.disk_io_counters()
        bytes_read = getattr(currentloadd, 'read_bytes')
        bytes_writ = getattr(currentloadd, 'write_bytes')
        time.sleep(1)
        currentloadd1 = psutil.disk_io_counters()
        bytes_read1 = getattr(currentloadd1, 'read_bytes')
        bytes_writ1 = getattr(currentloadd1, 'write_bytes')
        readio = (bytes_read1-bytes_read)
        writio = (bytes_writ1-bytes_writ)
        readio = str((round(readio, 2)))
        writio = str((round(writio, 2)))
        with open(os.path.join(config.serverbotpathdb, "diskioload.dat"), "a") as i:
          i.write(str(int(time.time())) + ";" + str(int(readio)) + ";" + str(int(writio)) + "\n")
      except:
        pass
    else:
      time.sleep(4)
      td += 5

# write the docker ps metrics into db file
def collectDockerMetrics() :
    while True :
        try :
            result = run(["docker", "ps", "-a"], stdout=PIPE, stderr=PIPE, universal_newlines=True)
            # have error message
            if not str(result.stderr) == "" :
                error_msg = "\nError : \n" + str(result.stderr)
                bot.send_message(config.tg, error_msg, reply_markup=markup)
                continue
            # std out
            result = str(result.stdout).split("\n")
            now_time = str(time.time())
            content = {now_time : []}
            #print(str(result) + error_msg)
            container_id = []
            # get container id
            for i in range(1, len(result)-1) :
                container_id.append(str(result[i]).split(" ")[0])
            # write docker container info into file
            for container in container_id :
                result = run(["docker", "inspect", container], stdout=PIPE, stderr=PIPE, universal_newlines=True)
                result = json.loads(result.stdout)[0]
                content[now_time].append(str(result["Name"]) + " " + str(result["State"]["Running"]))
            # read file of storing the docker container info
            db_file = open(os.path.join(config.serverbotpathdb, "dockerContainer.dat"))
            origin_content = json.load(db_file)
            db_file.close()
            # check whether the db is empty
            if not len(origin_content) == 0 :
                # not empty, then
                # check whether the number of containers have changed compare to last metrics
                checkContainerNumber(origin_content[len(origin_content)-1:][0], content[now_time])
            # write the new metric
            origin_content.append(content)
            db_file = open(os.path.join(config.serverbotpathdb, "dockerContainer.dat"), "w")
            json.dump(origin_content, db_file)
            db_file.close()
            time.sleep(5)
        except Exception as e:
            bot.send_message(config.tg, e, reply_markup=markup)
            print(e)

# check whether the number of containers have changed compare to last metrics
def checkContainerNumber(docker_last_history, content) :
    try :
        # key is the time found this metrics
        for key in docker_last_history.keys() :
            # last record
            last_name = []
            last_running = []
            for i in range(len(docker_last_history[key])) :
                last = docker_last_history[key][i].split(" ")
                last_name.append(last[0])
                last_running.append(last[1])
            # current record
            cur_name = []
            cur_running = []
            for i in range(len(content)) :
                cur = content[i].split(" ")
                cur_name.append(cur[0])
                cur_running.append(cur[1])
            # check last record have different with current record
            for i in range(len(last_name)) :
                container_name = last_name[i]
                # check whether the past container name not exist in new record
                if container_name not in cur_name :
                    msg = "Container not Existed !" + "\n" + container_name
                    bot.send_message(config.tg, msg, reply_markup=markup)
                # still existed then check whether it still running
                else :
                    # container index in current record
                    cur_index = cur_name.index(container_name)
                    # 
                    if last_running[i] == cur_running[cur_index] :
                        continue
                    else :
                        # running convert to not running
                        if last_running[i] == "True" :
                            msg = "Container not Running !" + "\n" + container_name
                            bot.send_message(config.tg, msg, reply_markup=markup)
                        else :
                            msg = "Container start Running !" + "\n" + container_name
                            bot.send_message(config.tg, msg, reply_markup=markup)
            # check current record have different with last record
            for container_name in cur_name :
                if container_name not in last_name :
                    msg = "New Container !" + "\n" + container_name
                    bot.send_message(config.tg, msg, reply_markup=markup)
            #bot.send_message(config.tg, str(cur_name) + "\n" + str(last_name), reply_markup=markup)
            #bot.send_message(config.tg, str(time.time()), reply_markup=markup)
    except Exception as e:
        bot.send_message(config.tg, e, reply_markup=markup)


if __name__ == '__main__':
  if config.start_monitor_docker_container == 1 :
    collectDockerMetrics = threading.Thread(target = collectDockerMetrics)
    collectDockerMetrics.start()

  if config.cfgAlertsNotificationsNode == 1:
    AlertsNotificationsNode = threading.Thread(target = AlertsNotificationsNode)
    AlertsNotificationsNode.start()

  if config.cfgAlertsNotificationsSync == 1:
    AlertsNotificationsSync = threading.Thread(target = AlertsNotificationsSync)
    AlertsNotificationsSync.start()

  if config.cfgAlertsNotificationsBlocks == 1:
    AlertsNotificationsBlocks = threading.Thread(target = AlertsNotificationsBlocks)
    AlertsNotificationsBlocks.start()

  if config.cfgAlertsNotificationsChunks == 1:
    AlertsNotificationsChunks = threading.Thread(target = AlertsNotificationsChunks)
    AlertsNotificationsChunks.start()

  if config.cfgAlertsNotificationsRam == 1:
    AlertsNotificationsRam = threading.Thread(target = AlertsNotificationsRam)
    AlertsNotificationsRam.start()

  if config.cfgAlertsNotificationsCPU == 1:
    AlertsNotificationsCPU = threading.Thread(target = AlertsNotificationsCPU)
    AlertsNotificationsCPU.start()

  if config.cfgmonitoringnetwork == 1:
    monitoringnetwork = threading.Thread(target = monitoringnetwork)
    monitoringnetwork.start()

  if config.cfgAlertsNotificationsping == 1:
    AlertsNotificationsping = threading.Thread(target = AlertsNotificationsping)
    AlertsNotificationsping.start()

  if config.cfgmonitoringdiskio == 1:
    monitoringdiskio = threading.Thread(target = monitoringdiskio)
    monitoringdiskio.start()

  else:
    pass

while True:
  try:
    bot.polling(none_stop=True, timeout=10) #constantly get messages from Telegram
  except:
    bot.stop_polling()
    time.sleep(5)
