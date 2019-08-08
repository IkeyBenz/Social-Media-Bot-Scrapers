from selenium.webdriver import Chrome
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.common.exceptions import StaleElementReferenceException

from os import path, makedirs, listdir
from time import sleep

from util import valid_input


class InstagramScrapper(object):
    """
        An bot that grabs instagram data from your browser
    """

    def __init__(self, username, password):
        self.driver = Chrome()
        self.user = {'username': username.lower(), 'password': password}

        self.open_instagram_and_login()

    def open_instagram_and_login(self):
        """ Opens instagram.com in Chrome and logs you in using given credentials """

        login_route = "https://www.instagram.com/accounts/login/?source=auth_switcher"

        # Open Instragram
        self.driver.get(login_route)
        wait = WebDriverWait(self.driver, 10)
        wait.until(lambda driver: driver.current_url == login_route)

        # Input Login Credentials
        username_input = self.driver.find_element_by_name("username")
        password_input = self.driver.find_element_by_name("password")
        username_input.send_keys(self.user['username'])
        password_input.send_keys(self.user['password'])

        # Login
        self.driver.find_element_by_css_selector("button[type=submit]").click()
        sleep(2)

    def _generate_accounts_from(self, container, expectation):
        def get_account(li):
            return li.find_elements_by_tag_name('a')[-1].text

        count = 0
        while count < expectation:
            try:
                list_items = container.find_elements_by_css_selector(
                    f'li:nth-child(n+{count+1})')
                self.driver.execute_script(
                    'arguments[0].scrollIntoView()', list_items[-1])

                for account in map(get_account, list_items):
                    yield account

                count += len(list_items)
            except:
                sleep(0.1)

    def _log(self, account_type: str, log_filepath: str, update=False) -> [str]:
        if not update and path.exists(log_filepath):
            print(
                f"{self.user['username']}'s {account_type} have been previously downloaded.")
            choice = valid_input(
                "Would you like to update them? (y/n) ", ["y", "n", "Y", "N"])
            if choice in "Nn":
                return open(log_filepath).read().splitlines()

        # Go to profile page
        desired_url = f"https://www.instagram.com/{self.user['username']}/"
        self.driver.get(desired_url)

        wait = WebDriverWait(self.driver, 10)
        wait.until(lambda driver: driver.current_url == desired_url)

        # Click anchor with href="/username/{following | followers}/"
        anchor_href = f"/{self.user['username']}/{account_type}/"
        link = self.driver.find_element_by_css_selector(
            f'a[href="{anchor_href}"]')

        num_following = int(link.find_element_by_tag_name('span').text)
        link.click()
        sleep(1)

        list_container = self.driver.find_element_by_css_selector(
            'div[role="dialog"] div.isgrP ul div.PZuss')

        accounts_gen = self._generate_accounts_from(
            list_container, num_following-1)

        accounts = []
        with open(log_filepath, 'w') as out:
            for account in accounts_gen:
                accounts.append(account)
                out.write(account + "\n")

        return accounts

    def log_following(self, log_filepath="following.txt", update=False):
        """
            Navigates to /username/following and records the usernames of everyone
            you follow into the log_filepath.
        """
        return self._log("following", log_filepath, update)

    def log_followers(self, log_filepath="followers.txt", update=False):
        """
            Navigates to /username/followers and records the usernames of everyone
            that follows you into the log_filepath.
        """
        return self._log("followers", log_filepath, update)

    def log_connections(self, log_filepath="connections.txt"):

        # Get followers
        followers_path = f"data/instagram/{self.user['username']}/followers.txt"
        followers = self.log_followers(followers_path)

        # Get following
        following_path = f"data/instagram/{self.user['username']}/following.txt"
        following = self.log_following(following_path)

        # Get intersection
        connections = set(following).intersection(set(followers))

        print(
            f"Found {len(connections)} connections with {self.user['username']}")
        with open(log_filepath, 'w') as out:
            print("Saving results...")
            out.write("\n".join(connections))
            print("Done.")

        return connections
