from selenium.webdriver import Chrome
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By

from os import path, makedirs
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

        return login_route

    def log_following(self, log_filepath="following.txt"):
        """
            Navigates to /username/following and records the usernames of everyone
            you follow into the log_filepath.
        """
        # Go to profile page
        desired_url = f"https://www.instagram.com/{self.user['username']}/"
        self.driver.get(desired_url)

        wait = WebDriverWait(self.driver, 10)
        wait.until(lambda driver: driver.current_url == desired_url)

        # Click anchor with href="/username/following/"
        anchor_href = f"/{self.user['username']}/following/"
        link = self.driver.find_element_by_css_selector(
            f'a[href="{anchor_href}"]')
        link.click()
        sleep(2)

        list_container = self.driver.find_element_by_css_selector(
            'div[role="dialog"] div.isgrP ul div.PZuss')
        sleep(1)  # Wait for content to load

        # Scroll through list to get them all to load
        keep_scrolling = True
        while keep_scrolling:
            # Get all links currenty in list
            links = list_container.find_elements_by_css_selector('li a')
            last_link = links[-1]
            self.driver.execute_script(  # Scroll so the last link gets displayed
                "arguments[0].scrollIntoView()", last_link)

            sleep(1)  # Wait a second for more results to load
            # Refresh the list of links, to include the new results
            links = list_container.find_elements_by_css_selector('li a')

            # Remove empty links
            accounts = [l.text for l in links if l.text is not ""]

            # If the last link is the same as before, no more results
            keep_scrolling = links[-1] != last_link

        print(
            f"Found {len(accounts)} accounts that {self.user['username']} is following.")
        with open(log_filepath, 'w') as out:
            print("Saving results...")
            out.write('\n'.join(accounts))
            print("Done.")
            return accounts

    def log_followers(self, log_filepath="followers.txt"):
        """
            Navigates to /username/followers and records the usernames of everyone
            that follows you into the log_filepath.
        """
        # Go to profile page
        desired_url = f"https://www.instagram.com/{self.user['username']}/"
        self.driver.get(desired_url)

        wait = WebDriverWait(self.driver, 10)
        wait.until(lambda driver: driver.current_url == desired_url)

        # Click anchor with href="/username/followers/"
        anchor_href = f"/{self.user['username']}/followers/"
        link = self.driver.find_element_by_css_selector(
            f'a[href="{anchor_href}"]')
        link.click()
        sleep(2)

        list_container = self.driver.find_element_by_css_selector(
            'div[role="dialog"] div.isgrP ul div.PZuss')
        sleep(1)  # Wait for content to load

        # Scroll through list to get them all to load
        keep_scrolling = True
        while keep_scrolling:
            # Get all links currenty in list
            links = list_container.find_elements_by_css_selector('li a')
            last_link = links[-1]
            self.driver.execute_script(  # Scroll so the last link gets displayed
                "arguments[0].scrollIntoView()", last_link)

            sleep(1)  # Wait a second for more results to load
            # Refresh the list of links, to include the new results
            links = list_container.find_elements_by_css_selector('li a')

            # Remove empty links
            accounts = [l.text for l in links if l.text is not ""]

            # If the last link is the same as before, no more results
            keep_scrolling = links[-1] != last_link

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


if __name__ == '__main__':
    print("> Opening Chrome Webdriver...")
    print("> Instagram requires login credentials to proceed.")
    username = input("Enter your Instagram username: ")
    password = input("Enter your Instagram password: ")

    print("> Logging you into instagram.com in Chrome browser...")
    scraper = InstagramScrapper(username, password)

    print("> What would you like to do?\n\t1) Log usernames that follow me\n\t2) Log usernames I follow\n\t3) Log usernames who I follow and follow me back")
    choice = valid_input("Enter 1/2/3: ", ['1', '2', '3'])

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

    # For getting second order network:
    # connections = open(
    #     f'data/{scraper.user["username"]}/connections.txt').read().splitlines()
    # for connection in connections:
    #     scraper.user["username"] = connection

    #     if not path.isdir(f"data/{connection}"):
    #         mkdir(f"data/{connection}")

    #     scraper.log_connections(f'data/{connection}/connections.txt')
