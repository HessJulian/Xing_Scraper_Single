#!/usr/bin/env python
# coding: utf-8

# In[ ]:


from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException
from bs4 import BeautifulSoup
import urllib.request 
import time 
from datetime import date
from datetime import datetime 
import pandas as pd
import json
import os
import errno
from lxml import html
import lxml.html
import requests
import pymysql
from sqlalchemy import create_engine
import re
from timeit import default_timer as timer

class Xing_Scraper:
    def __init__(self,company_url,browser_path,user_login_name,user_login_password):
        self.company_url        = company_url
        self.browser_path       = browser_path
        self.user_login_name    = user_login_name
        self.user_login_password= user_login_password
        
    def scraping(company_url,browser_path,user_login_name,user_login_password):
        #Start Point
        start = timer()
  
        try: 
            options = Options()
            #options.add_argument(r"user-data-dir=C:\Users\drink\AppData\Local\Google\Chrome\User Data")#Login daten speichern
            #options.add_argument("--headless")  
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--window-size=1920,1080")
            options.add_argument("start-maximised")
            options.add_argument('--disable-gpu')
            driver = webdriver.Chrome(str(browser_path),options=options)  # Chrome ist der Browser der benutzt wird,der Pfad zur EXE dazu in Klammer
        except:
            pass

        #Login
        driver.get("https://login.xing.com")
        try:
            driver.maximize_window()
            driver.find_element_by_xpath("//*[@id='consent-accept-button']/div/span").click() 
            driver.find_element_by_xpath("//*[@id='consent-accept-button']").click() 
        except:
            pass
        
        #Login-Daten senden, falls nicht schon eingeloggt-->Später aus Database Login ziehen und als Klasse schreiben
        while True:
            try:
                username = driver.find_element_by_xpath("//input[@name='username']")
                password = driver.find_element_by_xpath("//input[@name='password']")
                username.send_keys(str(user_login_name))
                password.send_keys(str(user_login_password))
                
                time.sleep(3)
                #Einloggen Button
                driver.find_element_by_xpath("//button[@type='submit']").click()
                time.sleep(2)
                driver.find_element_by_xpath("//button[@type='button']").click()
                
            except:
                break    
            
        #Firma url aufrufen
        time.sleep(2)
        driver.get(company_url)
        time.sleep(4)
        try:
            driver.find_element_by_xpath("//*[@id='consent-accept-button']/div/span").click() 
            driver.find_element_by_xpath("//*[@id='consent-accept-button']").click() 
            print("button found")
        except:
            print("no button found")
            None
        
        #Get Company Name
        company_html=driver.page_source 
        company_soup = BeautifulSoup(company_html)
        company_mainname= company_soup.find('h1',{'class':'name organization-name fn'}).get("title")
        company_mainname_short= company_soup.find('h1',{'class':'name organization-name fn'}).get("title").split(" ")[0]
        print(company_mainname)
              
        column_dict = {'Name': [], 'Profile URL': [], 'Occupation': [],'Company': [],'Image_URL': []}
        df = pd.DataFrame(data=column_dict)
        columns=list(df)            
                               
        #----------------Beginn Scraper----------------
        total_height = int(driver.execute_script("return document.body.scrollHeight"))
        
        for i in range(50, total_height, 100):
            name_list=[]
            profile_url_list=[]
            occupation_list=[]
            image_list=[]
            company_list=[]
            
            #try:
            #    WebDriverWait(driver, 3).until(EC.element_to_be_clickable((By.CSS_SELECTOR, '#members-list > div.contact-list > div:nth-child(1) > div:nth-child(2) > ul > li > a')))
            #except:
            #    print("waiting")
            #    time.sleep(1)
            #    driver.execute_script("window.scrollBy(0,-250);")
            #    pass
            time.sleep(0.5)
  
            Source=driver.page_source 
            soup = BeautifulSoup(Source)
            
            #Scrape Names from Employee List on Xing
            for names in soup.find_all('a',{'class':'user-name-link'}):
                if r"/profile/" in str(names.get("href")): 
                    name_list.append(re.sub('[0-9]+', '',names.get("href").split("/")[2]).replace("_"," "))
            #Scrape profile url from Employee List on Xing
            for profiles in soup.find_all('a',{'class':'user-name-link'}):
                if r"/profile/" in str(profiles.get("href")): 
                    profile_url_list.append("https://www.xing.com"+str(profiles.get("href")))
            #Scrape Occupations from Employee List on Xing
            for occupation in soup.find_all('ul',{'class':'user-card-information'}):
                try:
                    occupation_list.append((str(occupation).split("<li>")[3].split("</li>")[0]))
                except:
                    None
            #Scrape Company from Employee List on Xing
            for companys in soup.find_all('a',{'class':'user-card-company'}):
                company_list.append(str(companys).split(">")[1].split("</")[0])
            #Scrape JPG URL        
            for images in soup.find_all('img',{'class':'member'}):
                image_list.append(images.get("src"))
                
            div_length=int(len(image_list))-int(len(name_list))
            image_list=image_list[div_length:] #Oft wird über den Mitarbeitern ein Ansprechpartner geladen, diese werden gelöscht

        
            df = df.append(pd.DataFrame({'Name': name_list, 'Profile URL': profile_url_list, 'Occupation': occupation_list,'Company': company_list,'Image_URL': image_list}))
        
            df=df.drop_duplicates(subset=None, keep='first', inplace=False)
            driver.execute_script("window.scrollTo(0, {});".format(i))
        #----------------Ende Scraper----------------
        amount=len(list(df['Name']))
        print("Anzahl Einträge: "+str(amount))
        #Webbrowser beenden
        driver.quit()
    
    #Add Companyname from Variable
        df['Main Company'] = company_mainname
        
    #Add Date 
        today = date.today()

        # dd/mm/YY
        today_formated = today.strftime("%d/%m/%Y")
    
        df['Date'] = today_formated  
        
        companys_aggr_list=[]
        companys_raw_list=[]
        companys_split_list=[]
        subsidiarys=[]
        subsidiarys_dict={}
        
        parts_list = ['part of ', 'Part of ', 'teil von', 'Teil von']
        
        #Tochterfirman ausfindig machen anhand Textbeigabe "part of" etc., diejenigen die diesen Teil nicht enthalten, werden trotzdem gekennzeichnet
        for companyname_raw in df['Company']:
            for parts in parts_list:
                if parts in companyname_raw:
                    try:
                        companys_aggr_list.append(companyname_raw.split(str(parts))[1].replace("(","").replace(")","").replace("`","").replace(", "," "))
                        companys_split_list.append(companyname_raw.split(str(parts))[0].replace("(","").replace(")","").replace("`","").replace(", "," "))
                        subsidiarys.append(companyname_raw.split(str(parts))[0].replace("(","").replace(")","").replace("`","").replace(", "," ").split(" ")[0])
                        subsidiarys_dict[companyname_raw.split(str(parts))[0].replace("(","").replace(")","").replace("`","").replace(", "," ").split(" ")[0]]=companyname_raw.split(str(parts))[1].replace("(","").replace(")","").replace("`","").replace(", "," ")
                        break
                    except:
                        continue
            else:
                companys_split_list.append(companyname_raw.replace("(","").replace(")","").replace("`","").replace(", "," "))
                companys_aggr_list.append(companyname_raw.replace("(","").replace(")","").replace("`","").replace(", "," "))
            companys_raw_list.append(companyname_raw)
        
        #zweiter Loop zur Identifikation dieser Tochterfirmen und der Zuordnung zur Hauptgesellschaft
        companys_aggr_list2=[]
        for i in companys_aggr_list:
            for c in subsidiarys:
                if c in i:
                    print(str(c)+" is a match")
                    companys_aggr_list2.append(subsidiarys_dict[str(c)])
                    break
            else:
                companys_aggr_list2.append(str(i))
        
        #dritter Loop , hier sollen nun evtl schreibfehler etc ebenfalls berücksichtigt werden
        companys_aggr_list3=[]
        for i in companys_aggr_list2:
            for c in subsidiarys:
                if c.lower() in i.replace(" ","").lower():
                    print(str(c)+" is a match")
                    companys_aggr_list3.append(subsidiarys_dict[str(c)])
                    break
            else:
                companys_aggr_list3.append(str(i))           
        
        #vierter Loop , hier sollen nun Groß und Kleinschreibung sowohl fehlöerhafte & zeichen aus der html korrigiert werden
        companys_aggr_list4=[]
        for i in companys_aggr_list3:
             companys_aggr_list4.append(i.lower().replace("&amp;","&").replace("e","e").replace("i̇","i").title().replace("Ltd.","Ltd").replace("ı","i"))
        
        #fünfter Loop , Gersellschaftskürzel wieder als Uppercases darstellen
        companys_aggr_list5=[]
        for i in companys_aggr_list4:
            split_string=""
            for split_word in i.split(" "):
                if len(split_word)==2:
                    split_word_new=split_word.upper()
                else:
                    split_word_new=split_word
                split_string+=split_word_new+" "  
            companys_aggr_list5.append(split_string.rstrip())
        
        df_new = pd.DataFrame({'Company': companys_raw_list, 'Company New': companys_aggr_list,'Company New2': companys_aggr_list2, 'Company New3': companys_aggr_list3, 'Company New4': companys_aggr_list4, 'Company New5': companys_aggr_list5})
        
        df['Company New'] = pd.Series(companys_aggr_list5).values
        
        return df
                      
        end = timer()
        
        print("Dauer: "+str(((end - start)/60))+" min") # Time in seconds, e.g. 5.38091952400282


# In[ ]:




