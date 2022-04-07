import time
import random
import datetime
import json
from collections import defaultdict

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from webdriver_manager.chrome import ChromeDriverManager


USERNAME = ''
PASSWORD = ''
SAVED_SEARCH_NAME = 'Saved search 1'
DEFAULT_FILENAME = 'data.json'


def get_random_time():
    return random.random() + random.randint(0, 2)


def get_refresh_button(driver):
    xpath = '//div[@id="filter-summary-panel"]//button[@class="css-ppc4rt"]'
    try:
        button = WebDriverWait(driver, 3+get_random_time()).until(
            EC.presence_of_element_located((By.XPATH, xpath))
        )
    except Exception:
        return None
    else:
        return button


def goto_load_board(driver):
    WebDriverWait(driver, 3+get_random_time()).until(
        EC.presence_of_element_located((By.XPATH, '//div[@id="sidebar"]/div[@class="nav-card"][4]/a'))
    ).click()
    time.sleep(get_random_time())
    driver.find_element(By.XPATH, '//div[text()="Search"]').click()
    WebDriverWait(driver, 3+get_random_time()).until(
        EC.presence_of_element_located((By.XPATH, '//span[text()="Saved searches"]'))
    ).click()

    time.sleep(get_random_time())
    for element in driver.find_elements(By.CLASS_NAME, 'saved-search__list__box'):
        saved_search_name = element.find_element(By.TAG_NAME, 'p').text.strip()
        if saved_search_name == SAVED_SEARCH_NAME:
            element.click()
            driver.find_element(By.XPATH, '//span[text()="Apply"]').click()
            break

    WebDriverWait(driver, 3+get_random_time()).until(
        EC.presence_of_element_located((By.XPATH, '//div[@id="filter-summary-panel"]//button[@class="css-n5d7ax"]'))
    ).click()


def parse_truck_order(text):
    data = text.split('\n')
    result = defaultdict(dict)
    result['stop_1']['name'] = data[1]
    result['stop_1']['datetime'] = data[2]
    result['stop_2']['name'] = data[4]
    result['stop_2']['datetime'] = data[5]
    result['distance'] = data[6]
    result['duration'] = data[7]
    result['equipment_1'] = data[8] + f"({data[9]})"
    result['equipment_2'] = data[8] + f"({data[10]})"
    result['price'] = data[11] + f'({data[12]})'
    action_time = datetime.datetime.utcnow()
    result['action_time'] = action_time.strftime('%Y/%m/%d %H:%M:%S')
    return result


def write_to_json(truck_order: dict, filename=DEFAULT_FILENAME):
    try:
        with open(filename, 'r') as file:
            data = json.load(file)
    except Exception:
        data = []
    finally:
        data.append(truck_order)

    with open(filename, 'w') as file:
        json.dump(data, file)


def main():
    options = Options()
    profile_path = 'C:\\Users\\user\\AppData\\Local\\Google\\Chrome\\User Data\\Profile 4'
    options.add_argument('--allow-profiles-outside-user-dir')
    options.add_argument('--enable-profile-shortcut-manager')
    options.add_argument(f"user-data-dir={profile_path}")
    options.add_argument("start-maximized")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()),
                              options=options)
    driver.get("https://relay.amazon.com/")
    try:
        WebDriverWait(driver, 3+get_random_time()).until(
            EC.presence_of_element_located((By.LINK_TEXT, 'Sign In'))
        ).click()
        time.sleep(get_random_time())
        driver.find_element_by_name('email').send_keys(USERNAME)
        driver.find_element_by_name('password').send_keys(PASSWORD)
        driver.find_element_by_id('signInSubmit').submit()
    except TimeoutException:
        pass

    goto_load_board(driver)
    refresh_button = get_refresh_button(driver)
    while True:
        refresh_button.click()
        xpath = '//div[@class="wo-card"][1]'
        try:
            element = WebDriverWait(driver, get_random_time()).until(
                EC.presence_of_element_located((By.XPATH, xpath))
            )
        except Exception:
            continue

        truck_order = parse_truck_order(element.text)
        # element.find_element(By.TAG_NAME, 'button').click()
        # driver.find_element(By.XPATH('//span[text()="Yes, confirm booking"]')).click()
        time.sleep(get_random_time())
        if (refresh_button := get_refresh_button(driver)) is None:
            truck_order['booked_status'] = True
            goto_load_board(driver)
            refresh_button = get_refresh_button(driver)
        else:
            truck_order['booked_status'] = False

        write_to_json(truck_order)
        time.sleep(3000)


if __name__ == "__main__":
    main()
