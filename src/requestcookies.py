import json

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import requests

with open("../config/config.json") as config:
    parameters = json.load(config)

START_PAGE = parameters["start_page"]
BUTTON_NAME = parameters["button_name"]


def get_cookies() -> requests.cookies.RequestsCookieJar:
    options = Options()
    options.headless = True

    with webdriver.Chrome(options=options) as driver:
        driver.get(START_PAGE)
        button = driver.find_element_by_class_name(BUTTON_NAME)
        button.click()

        cookies = driver.get_cookies()
        jar = requests.cookies.RequestsCookieJar()

    for cookie in cookies:
        if "expiry" in cookie:
            cookie["expires"] = cookie.pop("expiry")
        del cookie["httpOnly"]
        jar.set(**cookie, rest={'HttpOnly': False})

    return jar
