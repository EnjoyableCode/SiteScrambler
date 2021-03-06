from __future__ import unicode_literals

import requests

import re

import os

from random import randint

import time

from bs4 import BeautifulSoup

from SiteScramble import SiteScramble

from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

cap = DesiredCapabilities().FIREFOX
cap["marionette"] = False

cwd = os.getcwd()


#url = 'http://www.google.com'

url = 'http://www.stackoverflow.com'



noise_level = 3


for num in range(3):

    r = requests.get(url)
    site_s = SiteScramble(r.text, noise_level, num, url)
    site_s.scramble_colors()
    site_s.scramble_font_sizes()
 
    with open('output/html' + str(num) + '.html', 'w') as f:
        #f.write(site_s.html.encode('utf-8'))
        f.write(site_s.html)

profile = webdriver.FirefoxProfile()
profile.set_preference("general.useragent.override","Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.78 Safari/537.36")
profile.set_preference("webdriver.load.strategy", "unstable")
driver = webdriver.Firefox(capabilities=cap, firefox_profile=profile)

for num in range(3):
    driver.get('file://' + cwd + '/output/option' + str(num + 1) + '.html')
    time.sleep(2)
    driver.get('file://' + cwd + '/output/html' + str(num) + '.html')
    time.sleep(4)
    driver.save_screenshot('output/screen' + str(num) + '.png')
    time.sleep(2)

driver.quit()

