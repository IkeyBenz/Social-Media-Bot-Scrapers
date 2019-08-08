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
        log_path = user_data_path + "followers.txt"
        print(f"> Saving followers to {log_path}")
        scraper.log_followers(log_path)

    elif choice == '2':
        log_path = user_data_path + "following.txt"
        print(f"> Saving following to {log_path}")
        scraper.log_following(log_path)

    elif choice == '3':
        log_path = user_data_path + "connections.txt"
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
