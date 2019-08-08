"""
    Using this file as a playground to test new functionality
    without running the whole bot.
"""

from selenium.webdriver import Chrome
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.common.exceptions import StaleElementReferenceException

from os import path, makedirs
from time import sleep

driver = Chrome()
username, password = open('ig.credentials.txt').read().split(',')
user = {'username': username, 'password': password}


def open_instagram_and_login():
    """ Opens instagram.com in Chrome and logs you in using given credentials """

    login_route = "https://www.instagram.com/accounts/login/?source=auth_switcher"

    # Open Instragram
    driver.get(login_route)
    wait = WebDriverWait(driver, 10)
    wait.until(lambda d: d.current_url == login_route)

    # Input Login Credentials
    username_input = driver.find_element_by_name("username")
    password_input = driver.find_element_by_name("password")
    username_input.send_keys(user['username'])
    password_input.send_keys(user['password'])

    # Login
    driver.find_element_by_css_selector("button[type=submit]").click()
    sleep(2)


def scroll():
    # Go to profile page
    desired_url = f"https://www.instagram.com/{user['username']}/"
    driver.get(desired_url)

    wait = WebDriverWait(driver, 10)
    wait.until(lambda driver: driver.current_url == desired_url)

    # Click anchor with href="/username/following/"
    anchor_href = f"/{user['username']}/following/"
    link = driver.find_element_by_css_selector(
        f'a[href="{anchor_href}"]')

    num_following = int(link.find_element_by_tag_name('span').text)

    link.click()
    sleep(1)

    list_container = driver.find_element_by_css_selector(
        'div[role="dialog"] div.isgrP ul div.PZuss')
    sleep(1)  # Wait for content to load

    list_items = list_container.find_elements_by_tag_name('li')

    while len(list_items) < num_following - 1:
        try:
            driver.execute_script(
                'arguments[0].scrollIntoView()', list_items[-1])
        except StaleElementReferenceException:
            sleep(0.5)

        list_items = list_container.find_elements_by_tag_name('li')

    for item in list_items:
        anchors = item.find_elements_by_tag_name('a')
        print(
            f"Anchors in item: {len(anchors)}. Text: {', '.join([a.text for a in anchors])}")


def detect_duplicates(lst):
    duplicates = {}
    items = set()
    for item in lst:
        if item in items:
            if item not in duplicates:
                duplicates[item] = 0
            duplicates[item] += 1
        else:
            items.add(item)
    return duplicates


if __name__ == '__main__':
    path = 'data/instagram/ikeybenz/followers.txt'
    accounts = open(path).read().splitlines()
    for account, appearances in detect_duplicates(accounts).items():
        print(f"{account}: {appearances}")
