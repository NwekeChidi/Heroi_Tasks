from cgitb import html
from http.client import HTTPResponse
from django.shortcuts import render
from django.http import HttpResponse
from pathlib import Path as path
from selenium import webdriver
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from webdriver_manager.firefox import GeckoDriverManager

import os
import time
import logging


# options = Options()
# options.add_argument('--headless')
driver = webdriver.Firefox(executable_path=GeckoDriverManager().install()) #, options=options)
delay = 5


def wait_for_element_ready(by, text):
    try:
        WebDriverWait(driver, delay).until(EC.presence_of_element_located((by, text)))
    except TimeoutException:
        logging.debug("wait_for_element_ready TimeoutException")
        pass

def wait(t_delay=None):
        """Just easier to build this in here.
        Parameters
        ----------
        t_delay [optional] : int
            seconds to wait.
        """
        delay = 5 if t_delay == None else t_delay
        time.sleep(delay)

def new_generator(title, industry, location):

    data = []
    [title, industry, location] = [i.lower().replace(" ", "+") for i in [title, industry, location]]
    print("Getting Search Results: \n......")
    driver.get(f'https://www.google.com/search?q="{title}"+{industry}+{location}+contact+email+"gmail"+site:linkedin.com')
    wait_for_element_ready(By.CLASS_NAME, 'v7W49e')
    time.sleep(delay)
    wait()
    
    
    print("Scraping Results\n.....")
    idx = 1
    for page in range(2, 11):
        wait_for_element_ready(By.CLASS_NAME, 'g')
        wait()
        elements = driver.find_elements_by_class_name('g')
        for element in elements:
            details = element.find_element_by_class_name('VwiC3b').text
            head_details = element.find_element_by_class_name('LC20lb').text
            data.append({
                "S/N"    : idx,
                "Name"   : head_details.split("-")[0].strip(),
                "Title"  : head_details.split("-")[1].strip(" .(:'") if len(head_details.split("-")) > 1 else "NaN",
                "Email"  : details[details.lower().find("email")+5:details.find("gmail.com")+9].strip(" .(:'") if "email" in details.lower() else "NaN",
                "Address": details.split(".")[0].strip(" .(:'") if "." in details else "NaN",
                "Phone"  : details[details.find("phone"):].split(" ")[0].strip(" .(:'") if "phone" in details.lower() else "NaN",
                "Company": head_details.split("-")[2].strip() if len(head_details.split("-")) > 2 else "NaN",
            })
            idx += 1

        time.sleep(delay)
        driver.find_element_by_xpath(f"//a[@aria-label='Page {page}']").click()
        print(f"Completed Scrape of page {page}...")
        wait()

    logging.info("\n\n Scrapping Complete!")
    # driver.close()
    driver.quit()

    return data

def create_csv(data_dict):
    import csv

    with open("leads.csv", "w", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=data_dict[0].keys())
        writer.writeheader()
        writer.writerows(data_dict)



def home(request):
    import pandas as pd
    html_data = None
    if 'title' in request.GET and 'industry' in request.GET and 'location' in request.GET:

        title = request.GET.get('title')
        industry = request.GET.get('industry')
        location = request.GET.get('location')

        data = new_generator(title, industry, location)
        create_csv(data)
        with open(os.path.join("templates/core/leads_table.html"), "w") as html_file:
            pd.read_csv("leads.csv").to_html(html_file)
        

    return render(request, 'core/home.html', {'data': html_data })

def result():
    return render('core/leads_table.html')