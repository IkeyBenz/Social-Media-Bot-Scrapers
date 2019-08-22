from selenium.webdriver import Chrome, ChromeOptions
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.common.exceptions import StaleElementReferenceException, TimeoutException

from os import path, makedirs, listdir
from time import sleep

from util import valid_input


class InstagramScrapper(object):
    """
        An bot that grabs instagram data from your browser
    """

    def __init__(self, username, password):
        opts = ChromeOptions()
        opts.add_experimental_option('w3c', False)
        self.driver = Chrome(chrome_options=opts)

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
        # loading icon = container.find_element_by_css_selector('div.W1Bne.ztp9m')
        count = 0
        while count < expectation:
            try:
                list_items = container.find_elements_by_css_selector(
                    f'li:nth-child(n+{count+1})')
                self.driver.execute_script(
                    'arguments[0].scrollIntoView()', list_items[-1])

                for account in map(get_account, list_items):
                    count += 1
                    yield account
                    if count >= expectation:
                        break

                sleep(0.1)
            except:
                sleep(0.2)

    def _log(self, account_type: str, log_filepath: str, update=False, mutuals_only=False) -> [str]:
        # Go to profile page
        desired_url = f"https://www.instagram.com/{self.user['username']}/"
        self.driver.get(desired_url)

        wait = WebDriverWait(self.driver, 5)
        wait.until(lambda driver: driver.current_url == desired_url)

        anchor_href = f"/{self.user['username']}/{account_type}/"
        if mutuals_only:
            anchor_href += "mutualOnly"

        cancel = False  # Need this flag because the 'finally' runs after return
        try:
            locator = (By.CSS_SELECTOR, f'a[href="{anchor_href}"]')
            link = wait.until(EC.presence_of_element_located(locator))
            link_text = link.find_element_by_tag_name('span').text
            num_following = link_text.split(
                ' ')[-2] if mutuals_only else link_text
            num_following = int(num_following.replace(',', ''))

        except ValueError:  # We will assume this user has 1-3 mutual followers
            spans = link.find_elements_by_css_selector('span span')
            num_following = len(spans)
        except TimeoutException:  # We will assume this user has no mutual
            cancel = True  # followers and we will skip to the next one
        finally:
            if cancel:
                return print(f"> ! {self.user['username']} has no mutual followers")
            link.click()

        if mutuals_only:
            btn = (By.CSS_SELECTOR,
                   f"a[href='/{self.user['username']}/followers/mutualFirst']")
            wait.until(EC.presence_of_element_located(btn)).click()

        selector = 'div[role="dialog"] div.isgrP ul div.PZuss'
        list_container = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, selector)))

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
        try:
            return self._log("following", log_filepath, update)
        except TimeoutException:
            self.driver.refresh()
            sleep(2)
            return self._log("following", log_filepath, update)

    def log_followers(self, log_filepath="followers.txt", update=False):
        """
            Navigates to /username/followers and records the usernames of everyone
            that follows you into the log_filepath.
        """
        try:
            return self._log("followers", log_filepath, update)
        except TimeoutException:
            self.driver.refresh()
            sleep(2)
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

    def log_mutuals_with(self, username):
        log_path = f"data/instagram/{self.user['username']}/"
        if not path.exists(log_path):
            makedirs(log_path)
        log_path += f"mutuals_with_{username}.txt"
        if not path.exists(log_path):
            try:
                self._log("followers", log_path, mutuals_only=True)
                print("> Saved", log_path)
            except TimeoutException:
                print("Stuff didn't load in time. Refreshing and trying again.")
                self.driver.refresh()
                sleep(2)
                return self.log_mutuals_with(username)

        else:
            print("> Skipping", self.user['username'])
