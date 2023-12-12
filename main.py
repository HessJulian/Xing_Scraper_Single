import sys
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException
from bs4 import BeautifulSoup
import urllib.request 
import time 
from datetime import datetime 
import pandas as pd
import json
import os
import errno
from lxml import html
import lxml.html
import requests
import re
import random
from timeit import default_timer as timer
from .Xing_Scraper import Xing_Scraper

#Wird als Liste ausgegeben, auch wenn nur ein Wert enthalten
Mail='Mail'
Password='Passwort'
requester_company_url='company_url'

browser_path=r'.chromedriver.exe'
user_login_name=str(Mail)
user_login_password=str(Password)

#Prüfung ob URL richtig ist und ggfs korrekte mitgeben
try: 
    options = Options()
    options.add_argument("--headless")  
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("start-maximised")
    options.add_argument('--disable-gpu')
    driver = webdriver.Chrome(str(browser_path),options=options)  # Chrome ist der Browser der benutzt wird,der Pfad zur EXE dazu in Klammer
except:
    pass
       
#Firma url aufrufen
time.sleep(1)
driver.get(requester_company_url)
time.sleep(3)
actual_URL = driver.current_url
print("Actual URL: "+str(actual_URL))
driver.quit()

#URL prüfen
if '/employees' in requester_company_url:
    company_url=actual_URL
else:
    company_url=actual_URL+'/employees'

url_length=len(company_url.split('/'))
#Scraping Beginn
try:
    if company_url.split("www.xing.com/")[1].split("/")[0]=="companies":
        scrapes_init=Xing_Scraper.scraping(company_url,browser_path,user_login_name,user_login_password)#ohne save, aber return des dataframes
    elif company_url.split("www.xing.com/")[1].split("/")[0]=="pages":
        scrapes_init=Xing_Scraper.scraping(company_url,browser_path,user_login_name,user_login_password)#ohne save, aber return des dataframes

    amount = len(scrapes_init['Name'])

    company_mainname=scrapes_init['Main Company'].iloc[0]
except Exception as err:
    print(err)

    #Scraping Ende

def logging(company_mainname):
#    pass
    Logging_Path=r'.'+str(company_mainname)+'/'+str(datetime.now())[:10]+'/'
    if not os.path.exists(os.path.dirname(Logging_Path)):
        try:
            os.makedirs(os.path.dirname(Logging_Path))
        except OSError as exc: # Guard against race condition
            if exc.errno != errno.EEXIST:
                raise
    
    logfile=open(str(Logging_Path)+str(str(company_url.split('/')[url_length-2]))+'.txt','w') #Hier richtigen Speicherpfad eingeben
    logfile.write('Unternehmen '+str(str(company_url.split('/')[url_length-2]))+':\n'+str(err))
    logfile.close()

logging(company_mainname)

time.sleep(random.randrange(100,140,1))
#Nach Scraping ende, available Flag auf yes setzen
#End Session

print('Finished')





