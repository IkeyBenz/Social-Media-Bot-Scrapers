from selenium.webdriver import Chrome
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.common.exceptions import StaleElementReferenceException

from os import path, makedirs, listdir
from time import sleep


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

    def _scroll_for_elements(self, container, expectation):
        list_items = container.find_elements_by_tag_name('li')
        while len(list_items) < expectation:
            try:
                self.driver.execute_script(
                    'arguments[0].scrollIntoView()', list_items[-1])
            except StaleElementReferenceException:
                sleep(0.5)

            list_items = container.find_elements_by_tag_name('li')

        return list_items

    def log_following(self, log_filepath="following.txt", update=False):
        """
            Navigates to /username/following and records the usernames of everyone
            you follow into the log_filepath.
        """
        if not update and path.exists(log_filepath):
            print(
                f"> {self.user['username']}'s following is already recorded. Skipping.")
            return open(log_filepath).read().splitlines()

        # Go to profile page
        desired_url = f"https://www.instagram.com/{self.user['username']}/"
        self.driver.get(desired_url)

        wait = WebDriverWait(self.driver, 10)
        wait.until(lambda driver: driver.current_url == desired_url)

        # Click anchor with href="/username/following/"
        anchor_href = f"/{self.user['username']}/following/"
        link = self.driver.find_element_by_css_selector(
            f'a[href="{anchor_href}"]')

        num_following = int(link.find_element_by_tag_name('span').text)
        link.click()
        sleep(1)

        list_container = self.driver.find_element_by_css_selector(
            'div[role="dialog"] div.isgrP ul div.PZuss')

        list_items = self._scroll_for_elements(list_container, num_following-1)
        accounts = list(
            map(lambda li: li.find_elements_by_tag_name('a')[-1].text, list_items))

        print(
            f"Found {len(accounts)} accounts that {self.user['username']} is following.")

        with open(log_filepath, 'w') as out:
            print("Saving results...")
            out.write('\n'.join(accounts))
            print("Done.")
            return accounts

    def log_followers(self, log_filepath="followers.txt", update=False):
        """
            Navigates to /username/followers and records the usernames of everyone
            that follows you into the log_filepath.
        """

        if not update and path.exists(log_filepath):
            print(
                f"> {self.user['username']}'s followers is already recorded. Skipping.")
            return open(log_filepath).read().splitlines()

        # Go to profile page
        desired_url = f"https://www.instagram.com/{self.user['username']}/"
        self.driver.get(desired_url)

        wait = WebDriverWait(self.driver, 10)
        wait.until(lambda driver: driver.current_url == desired_url)

        # Click anchor with href="/username/followers/"
        anchor_href = f"/{self.user['username']}/followers/"
        link = self.driver.find_element_by_css_selector(
            f'a[href="{anchor_href}"]')

        num_followers = int(link.find_element_by_tag_name('span').text)

        link.click()
        sleep(2)

        list_container = self.driver.find_element_by_css_selector(
            'div[role="dialog"] div.isgrP ul div.PZuss')
        sleep(1)  # Wait for content to load

        list_items = self._scroll_for_elements(list_container, num_followers-1)
        accounts = list(
            map(lambda li: li.find_elements_by_tag_name('a')[-1].text, list_items))

        print(
            f"Found {len(accounts)} accounts that follow {self.user['username']}")
        with open(log_filepath, 'w') as out:
            print("Saving results...")
            out.write('\n'.join(accounts))
            print("Done.")
            return accounts

    def log_connections(self, log_filepath="connections.txt"):

        # Get followers
        followers_path = f"data/instagram/{self.user['username']}/followers.txt"
        if path.exists(followers_path):
            followers = open(followers_path).read().splitlines()
        else:
            followers = self.log_followers(followers_path)

        # Get following
        following_path = f"data/instagram/{self.user['username']}/following.txt"
        if path.exists(following_path):
            following = open(following_path).read().splitlines()
        else:
            following = self.log_following(following_path)

        # Get intersection
        connections = [flwr for flwr in followers if flwr in following]

        print(
            f"Found {len(connections)} connections with {self.user['username']}")
        with open(log_filepath, 'w') as out:
            print("Saving results...")
            out.write("\n".join(connections))
            print("Done.")

        return connections


def valid_input(prompt, acceptable_responses):
    response = input(prompt)
    if response in acceptable_responses:
        return response

    print("Invalid response")
    return valid_input(prompt, acceptable_responses)


def start():
    print("> Opening Chrome Webdriver...")

    credentials_path = "ig.credentials.txt"

    # Check if credentials are saved
    if not path.exists(credentials_path):
        print("> Instagram requires login credentials to proceed.")
        username = input("Enter your Instagram username: ")
        password = input("Enter your Instagram password: ")

        # Ask user if they want to store their login info
        print("Would you like to save these credentials to bypass this step next time?")
        save_creds = valid_input("Enter y/n: ", ["Y", "y", "N", "n"]) in "yY"

        if save_creds:
            out = open(credentials_path, "w")
            out.write(f"{username},{password}")
            out.close()

    else:  # Use stored credentials
        username, password = open(credentials_path).read().split(',')

    print("> Logging you into instagram.com in Chrome browser...")
    scraper = InstagramScrapper(username, password)

    show_interface(scraper)


def show_interface(scraper):
    print("> What would you like to do?\n\t1) Log usernames that follow me\n\t2) Log usernames I follow\n\t3) Log usernames who I follow and follow me back\n\t4) Log my 2nd order network")
    choice = valid_input("Enter 1/2/3/4: ", ['1', '2', '3', '4'])

    user_data_path = f"data/instagram/{scraper.user['username']}/"
    if not path.exists(user_data_path):
        makedirs(user_data_path)

    if choice == '1':
        log_path = f"data/instagram/{scraper.user['username']}/followers.txt"
        print(f"> Saving followers to {log_path}")
        scraper.log_followers(log_path)

    elif choice == '2':
        log_path = f"data/instagram/{scraper.user['username']}/following.txt"
        print(f"> Saving following to {log_path}")
        scraper.log_following(log_path)

    elif choice == '3':
        log_path = f"data/instagram/{scraper.user['username']}/connections.txt"
        print(f"> Saving connections to {log_path}")
        scraper.log_connections(log_path)

    elif choice == '4':
        print("> Getting your connections and their connections")

        # Get all connections of authenticated user
        connections_path = f'data/instagram/{scraper.user["username"]}/connections.txt'
        if path.exists(connections_path):
            connections = open(connections_path).read().splitlines()
        else:
            connections = scraper.log_connections(connections_path)

        # Get the connections of authenticated user's connections
        for connection in connections:
            # Change the username of scraper to be current connection
            print("> Getting connections of", connection)
            scraper.user["username"] = connection

            if not path.exists(f"data/instagram/{connection}/"):
                makedirs(f"data/instagram/{connection}/")

            log_path = f'data/instagram/{scraper.user["username"]}/connections.txt'
            scraper.log_connections(log_path)

    print("> Would you like to run another task?")
    choice = valid_input("Enter y/n: ", ['Y', 'y', 'N', 'n'])
    if choice in 'Yy':
        return show_interface(scraper)

    print("> Stopping processes...")
    print("> Done. Bye Bye.")


if __name__ == '__main__':
    start()
