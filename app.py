import os
import platform
import time

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.firefox_profile import FirefoxProfile
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import pandas as pd
from alive_progress import alive_bar

logging = False #Print log statements or not

ENTER = Keys.ENTER
CONTROL = Keys.META if platform.uname().system == "Darwin" else Keys.CONTROL
XPATHS = {
    'searchbox' : "/html/body/div[1]/div/div/div[3]/div/div[1]/div/div/div[2]/div/div[2]",
    'textbox' : "/html/body/div[1]/div/div/div[4]/div/footer/div[1]/div/span[2]/div/div[2]/div[1]/div/div[1]",
    'attachment_button' : "/html/body/div[1]/div/div/div[4]/div/footer/div[1]/div/span[2]/div/div[1]/div[2]/div/div",
    'attach_image_button' : "/html/body/div[1]/div/div/div[4]/div/footer/div[1]/div/span[2]/div/div[1]/div[2]/div/span/div/div/ul/li[1]/button/input",
    'send_image_button' : "/html/body/div[1]/div/div/div[2]/div[2]/span/div/span/div/div/div[2]/div/div[2]/div[2]/div/div",
    'image_textbox' : "/html/body/div[1]/div/div/div[2]/div[2]/span/div/span/div/div/div[2]/div/div[1]/div[3]/div/div/div[2]/div[1]/div[1]",
    'send_button' : "html/body/div[1]/div/div/div[4]/div/footer/div[1]/div/span[2]/div/div[2]/div[2]/button",
}


def os_name():
    return platform.uname().system


def get_appdata_dir(os_name):
    if os_name == "Windows":
        return os.environ.get("APPDATA")
    elif os_name == "Linux":
        return os.environ.get("HOME") + "/.mozilla/firefox/"
    else:
        raise ValueError


def firefox_profile(os_name: str):
    appdata = get_appdata_dir(os_name)  
    return "C:\\Users\\DELL\\AppData\\Roaming\\Mozilla\\Firefox\\Profiles\\pfqzm6fa.default"


def driver_path(os_name: str, driver_name: str):
    if os_name == "Windows":
        return f"./drivers/{driver_name}.exe"
    elif os_name in ["Linux","Darwin"]:
        return f"./drivers/{driver_name}"


def select_driver(browser: str):
    driver = None
    if browser in["chrome","c"]:
        options = Options()
        # options.add_argument("--user-data-dir=./browserddata/chrome-data")
        # options.add_experimental_option("excludeSwitches",
        #   ["enable-automation"])
        # options.add_experimental_option('useAutomationExtension', False)
        driver = webdriver.Chrome(
            driver_path(os_name(), "chromedriver"), options=options
        )
    elif browser in ["firefox" ,"f",""]:
        driver = webdriver.Firefox(
            executable_path=driver_path(os_name(), "geckodriver"),
            # firefox_profile = FirefoxProfile(firefox_profile(os_name()))
        )
    else:
        raise ValueError
    return driver

def log(text):
    if logging:
        print(text)


def patientFindElement(driver,elementname:str,timeout:int = 10,poll:int=1):
    log(f'waiting to find: {elementname}')
    return WebDriverWait(driver,timeout).until(lambda x: x.find_element('xpath',XPATHS[elementname]))

def sendmsg_to_contact(driver, contact: str, messages: list):
    contact = str(contact).replace("-", "")
    if contact.startswith("0"):
        contact = contact[1:]

    log(f"Searching contact {contact}")    
    searchbox = patientFindElement(driver,'searchbox')
    searchbox.clear()
    searchbox.send_keys(contact)
    searchbox.send_keys(ENTER)

    for message in messages:
        df=pd.DataFrame(message["text"].split("\n"))
        df.to_clipboard(header=False, index=False)

        if message.get("image"):
            log('message contains image')    
            log('finding attachment button')
            attachment_button = patientFindElement(driver,'attachment_button')
            log('clicking attachment button')
            attachment_button.click()
            log('finding attach image button')
            attach_image_button = patientFindElement(driver,'attach_image_button')
            log('sending image')
            attach_image_button.send_keys(message["image"])
            
            log('finding image textbox')
            textbox = patientFindElement(driver,'image_textbox')
            log('sending text to textbox')
            textbox.send_keys(CONTROL, "V")

            log('finding send image button')
            send_image_button = patientFindElement(driver,'send_image_button')
            log('clicking send image button')
            send_image_button.click()
        else:
            log('finding textbox')
            textbox = patientFindElement(driver,'textbox')
            log('sending text to textbox')
            textbox.send_keys(CONTROL, "V")
            log('finding send message button')
            send_button = patientFindElement(driver,'send_button')
            log('clicking send message button')
            send_button.click()
        
        log('waiting for message to be sent')
        WebDriverWait(driver,10) \
            .until_not(
                lambda x: x.find_element('xpath','//*[@aria-label=" Pending "]'),
                message="Timeout occurred, check connection")
        log('message sent successfully! \n')


def send_messages(contact_list: list, messages: list, options):
    print(f'working directory is: {os.getcwd()}')

    driver = select_driver(options["browser"])
    driver.maximize_window()
    driver.get("https://web.whatsapp.com")  # Already authenticated
    input("press enter to continue when logged into whatsapp")

    with alive_bar(len(contact_list)) as bar:
        for contact in contact_list:
            try:
                sendmsg_to_contact(driver, contact, messages)
            except Exception as ex:
                log(ex)
                input('continue? ')
            bar()

    print('\n ALL DONE! \n')
    input('End program? ')
    driver.close()
