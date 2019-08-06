from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import requests


def get_cookies():
    print("Start retrieving cookies...")

    options = Options()
    options.headless = True
    driver = webdriver.Chrome(options=options)

    driver.get("https://tweakers.net/aanbod/zoeken")
    button = driver.find_element_by_class_name("ctaButton")
    button.click()

    cookie_list = driver.get_cookies()

    jar = requests.cookies.RequestsCookieJar()

    for cookie in cookie_list:
        jar.set(cookie["name"], cookie["value"], domain=cookie["domain"], expires=1628169833, path='/',
                secure=cookie["secure"], rest={'HttpOnly': False})

    driver.quit()
    print("Cookies retrieved\n")

    return jar
