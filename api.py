from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException
from selenium.webdriver.chrome.options import Options

import json

from bs4 import BeautifulSoup
import time


def parse_by_zipcode(zipcode: int):

    URL = "https://factfinder.census.gov/faces/nav/jsf/pages/community_facts.xhtml?src=bkmk"

    options = Options()
    options.add_argument("--headless")

    driver = webdriver.Chrome(options=options)
    driver.get(URL)
    soup = BeautifulSoup(driver.page_source, "lxml")

    while driver.execute_script("return document.readyState") != "complete":
        time.sleep(1)

    delay = 3

    try:
        while driver.execute_script("return document.readyState") != "complete":
            time.sleep(1)

        time.sleep(1)

        search_form = WebDriverWait(driver, delay).until(
            EC.presence_of_element_located((By.ID, "cfsearchform"))
        )

        time.sleep(1)

        while driver.execute_script("return document.readyState") != "complete":
            time.sleep(1)

        time.sleep(1)

        search_box = WebDriverWait(driver, delay).until(
            EC.presence_of_element_located((By.ID, "cfsearchtextbox"))
        )
        search_box.send_keys(zipcode)

        while driver.execute_script("return document.readyState") != "complete":
            time.sleep(1)

        time.sleep(1)

        WebDriverWait(search_form, delay).until(
            EC.presence_of_element_located((By.TAG_NAME, "a"))
        ).click()

        time.sleep(1)

        while driver.execute_script("return document.readyState") != "complete":
            time.sleep(1)

        time.sleep(1)

        element = WebDriverWait(driver, delay).until(
            EC.presence_of_element_located(
                (By.PARTIAL_LINK_TEXT, "Race and Hispanic Origin")
            )
        )
        time.sleep(1)

        element.click()

        while driver.execute_script("return document.readyState") != "complete":
            time.sleep(1)

        time.sleep(1)

        element = WebDriverWait(driver, delay).until(
            EC.presence_of_element_located(
                (By.PARTIAL_LINK_TEXT, "Demographic and Housing Estimates")
            )
        )
        time.sleep(1)


        element.click()

        time.sleep(1)
        while driver.execute_script("return document.readyState") != "complete":
            time.sleep(1)

        year_selector = WebDriverWait(driver, delay).until(
            EC.presence_of_element_located((By.ID, "year_selector_content"))
        )

        res = {}

        years = year_selector.find_elements_by_tag_name("li")

        table = WebDriverWait(driver, delay).until(
            EC.presence_of_element_located((By.ID, "year_table_column"))
        )

        year = year_selector.find_elements_by_tag_name("li")[0].text

        current_year_data = {}

        current_row = table.find_element_by_xpath(
            "//tr[th[contains(text(), 'Race alone or in combination with one or more other races')]]/following-sibling::tr/following-sibling::tr"
        )

        while True:
            if current_row.text.isspace():
                break
            race = current_row.find_element_by_tag_name("th").text

            d = []

            for data in current_row.find_elements_by_tag_name("td"):
                d.append(data.text)

            current_year_data[race] = {
                "estimate": d[0],
                "margin_of_error": d[1],
                "percent": d[2],
            }

            current_row = current_row.find_element_by_xpath("following-sibling::tr")

        res[year] = current_year_data

        return res

    except Exception as e:
        print(e)
        raise e


def parse_text_file():
    text_file = open("zipcodes.txt", "r")
    zips = []
    with open("zipcodes.txt") as f:
        for line in f:
            zips += line.strip("\n").split(",")
    return zips


def scrape_data():
    zips = parse_text_file()

    def recursion(zipcode: int, attempts: int, max_tries=3):
        try:
            return parse_by_zipcode(zipcode)
        except Exception as e:
            if attempts == max_tries:
                print("Max tries of {}".format(zipcode))
                return "FAILED"
            attempts += 1
            return recursion(zipcode, attempts)

    final = {}

    for zipcode in zips:
        final[zipcode] = recursion(zipcode, 0)
        print("Done with {}".format(zipcode))

    with open("result.json", "w") as fp:
        json.dump(final, fp)

    print("FINISH")


scrape_data()
