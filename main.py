from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import StaleElementReferenceException
from selenium.common.exceptions import TimeoutException

from tkinter import  ttk
import tkinter as tk

import pandas as pd
import time

root = tk.Tk()
root.title("Rentals Scraping")
root.geometry('300x230')
entry_widget=tk.Entry(root,width=33)
entry_widget.pack(expand=True,fill=tk.X,padx=10)
lbl_finished = tk.Label(text='...finished...check output.xlsx file...')

chrome_options = Options()
chrome_options.headless = False
chrome_options.add_argument("start-maximized")
# options.add_experimental_option("detach", True)
chrome_options.add_argument("--no-sandbox")
chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
chrome_options.add_experimental_option('useAutomationExtension', False)
chrome_options.add_argument('--disable-blink-features=AutomationControlled')

driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=chrome_options)

#search for rentals
def foo():
    var_inp=entry_widget.get()
    if var_inp =='':
        var_inp = 'Santa Monica, CA'
    print(var_inp)
    driver.get('https://www.apartments.com/')
    element=WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "quickSearchLookup")))
    element.click()
    time.sleep(.5)
    element.send_keys(var_inp)
    time.sleep(.5)
    button=WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//a[@class='go']")))
    button.click()
    driver.implicitly_wait(15)
    element=WebDriverWait(driver, 15).until(EC.element_to_be_clickable((By.ID, "searchBarLookup")))
    if element.text!=var_inp:
        driver.execute_script("arguments[0].setAttribute('value','Santa Monica, CA')", element)
        element.send_keys(var_inp+Keys.ENTER)
        driver.implicitly_wait(15)
    foo2(var_inp)

def foo2(var_inp):

    try:
        driver.implicitly_wait(15)
        lst_prices=creating_list_d("//p[@class='property-pricing']")
        lst_beds=creating_list_d("//p[@class='property-beds']")
        #lst_specials=creating_list_d("//p[@class='property-specials']")
        lst_addresses=creating_list_d("//div[contains(@class,'property-address')]")
    except StaleElementReferenceException or TimeoutException:
        print('---except')
        try:
            driver.implicitly_wait(15)
            lst_prices=creating_list_d2("//p[@class='property-pricing']")
            lst_beds=creating_list_d2("//p[@class='property-beds']")
            #lst_specials=creating_list_d2("//p[@class='property-specials']")
            lst_addresses=creating_list_d2("//div[contains(@class,'property-address')]")
        except TimeoutException:
            pass

    try:
        elemBtnNext = WebDriverWait(driver, 15).until(
            EC.visibility_of_element_located((By.XPATH, '//a[@class="next "]/span')))
        if (elemBtnNext.text)=='Next':
            WebDriverWait(driver, 15).until(EC.visibility_of_element_located((By.XPATH, '//a[@class="next "]'))).click()
            time.sleep(.5)
            print(lst_prices, lst_beds, lst_addresses)
            print(len(lst_prices), len(lst_beds), len(lst_addresses))
            datas = {'Beds': lst_beds,
                     'Prices': lst_prices,
                     'Address': lst_addresses
                     }
            df = pd.DataFrame(data=datas)
            df.to_excel('output.xlsx', sheet_name='Sheet1')
            foo2(var_inp)


        else:
            pass
    except TimeoutException:
        pass


    driver.quit()


    lbl_finished.pack()


def creating_list_d(v_xpath):
    try:
        v_data_elements=WebDriverWait(driver,15).until(EC.presence_of_all_elements_located((By.XPATH,v_xpath)))
        lst_v_data_elems=[]
        for v_data in v_data_elements:
            lst_v_data_elems.append(v_data.text)
    except TimeoutException:
        return None
    return lst_v_data_elems

def creating_list_d2(v_xpath):
    v_data_elements=WebDriverWait(driver,15).until(EC.visibility_of_all_elements_located((By.XPATH,v_xpath)))
    lst_v_data_elems=[]
    for v_data in v_data_elements:
        lst_v_data_elems.append(v_data.text)
    return lst_v_data_elems


button1 = tk.Button(root,text='scrape', command=foo, bg='darkblue', fg='white',width=33)
button1.pack(padx=3,pady=3,anchor='center')

root.mainloop()
#pyinstaller -F  main.py --onefile --noconsole