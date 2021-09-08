#!/bin/python3

import telebot
import logging
import asyncio
import requests
import json
import xmltodict
from time import sleep
from bs4 import BeautifulSoup

token = open('./token').readlines()[0]

tb = telebot.TeleBot(token, parse_mode="MARKDOWN")

old_items = []

def getRSSItems(rss):
    items = xmltodict.parse(rss.content)
    items = items['rss']['channel']['item']

    itx = {x['infoHash']: x for x in items}
    return itx

def setInitialRSS(url):
    rss = requests.get(url)
    items = getRSSItems(rss)
    global old_items
    old_items = items

def checkRSS(url):
    try:
        global old_items
        rss = requests.get(url)
        items = getRSSItems(rss)

        hashDiff = list(set(list(items)) - set(list(old_items)))

        print(hashDiff)
        if len(hashDiff) > 0:
            for t in hashDiff:
                title = items[t]['title']
                size = items[t]['size']
                link = items[t]['guid']['#text']
                category = items[t]['category']
                msg = f"**{title}** @ {size}\n{link}"
                size = size.split()
                size[0] = float(size[0])
                print(size)
                print(msg)
                if size[0] > 7 and size[1] == 'GiB':
                    if category == 'REDACTED':
                        tb.send_message('REDACTED', msg, True)
            old_items = items

    except Exception as e:
        print('The scraping job failed. See exception:\n', e)

setInitialRSS('https://REDACTED/?page=rss')
while True:
    checkRSS('https://REDACTED/?page=rss')
    sleep(50)
tb.polling()
