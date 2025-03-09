import os
import socket
import threading
import time
import re

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys


class ChatGPTAutomation:

    def __init__(self, chrome_path, chrome_driver_path, chat_id=None):
        """
        This constructor automates the following steps:
        1. Open a Chrome browser with remote debugging enabled at a specified URL.
        2. Prompt the user to complete the log-in/registration/human verification, if required.
        3. Connect a Selenium WebDriver to the browser instance after human verification is completed.

        :param chrome_path: file path to chrome.exe (ex. C:\\Users\\User\\...\\chromedriver.exe)
        :param chrome_driver_path: file path to chromedriver.exe (ex. C:\\Users\\User\\...\\chromedriver.exe)
        """

        self.chrome_path = chrome_path
        self.chrome_driver_path = chrome_driver_path

        if chat_id: 
            url = f"https://chat.openai.com/c/{chat_id}"
        else:
            url = r"https://chat.openai.com/"
        free_port = self.find_available_port()
        self.launch_chrome_with_remote_debugging(free_port, url)
        self.wait_for_human_verification()
        self.driver = self.setup_webdriver(free_port)
        self.cookie = self.get_cookie()

    @staticmethod
    def find_available_port():
        """ This function finds and returns an available port number on the local machine by creating a temporary
            socket, binding it to an ephemeral port, and then closing the socket. """

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('', 0))
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            return s.getsockname()[1]

    def launch_chrome_with_remote_debugging(self, port, url):
        """ Launches a new Chrome instance with remote debugging enabled on the specified port and navigates to the
            provided url """

        def open_chrome():
            chrome_cmd = f"{self.chrome_path} --remote-debugging-port={port} --user-data-dir=remote-profile {url}"
            os.system(chrome_cmd)

        chrome_thread = threading.Thread(target=open_chrome)
        chrome_thread.start()

    def setup_webdriver(self, port):
        """  Initializes a Selenium WebDriver instance, connected to an existing Chrome browser
             with remote debugging enabled on the specified port"""

        chrome_options = webdriver.ChromeOptions()
        chrome_options.binary_location = self.chrome_driver_path
        chrome_options.add_experimental_option("debuggerAddress", f"127.0.0.1:{port}")
        driver = webdriver.Chrome(options=chrome_options)
        return driver

    def get_cookie(self):
        """
        Get chat.openai.com cookie from the running chrome instance.
        """
        cookies = self.driver.get_cookies()
        cookie = [elem for elem in cookies if elem["name"] == '__Secure-next-auth.session-token'][0]['value']
        return cookie

    def send_prompt_to_chatgpt(self, prompt, is_new_chat=True):
        """ Sends a message to ChatGPT and waits for 20 seconds for the response """
        if is_new_chat:
            target_turn_data = 'data-testid="conversation-turn-3"'
        else:
            last_turn_tag = self.driver.find_elements(by=By.TAG_NAME, value='article')[-1]
            last_turn_data = last_turn_tag.get_attribute("data-testid")
            match = re.search(r"(conversation-turn-)(\d+)", last_turn_data)
            if match:
                prefix, number = match.groups()
                target_turn_data =  f"{prefix}{int(number) + 1}"
            
        input_box = self.driver.find_element(by=By.ID, value='prompt-textarea')
        paragraphs = prompt.strip().split("\n")
        prompt_html = "".join(f"<p>{line}</p>" for line in paragraphs if line.strip())

        self.driver.execute_script(f"arguments[0].innerHTML = '{prompt_html}';", input_box)
        input_box.send_keys(Keys.RETURN)
        self.check_response_ended(target_turn_data)

    def check_response_ended(self, target_turn_data):
        """ Checks if ChatGPT response ended """
        start_time = time.time()
        while time.time() - start_time <= 60:
            try:
                target_element = self.driver.find_element(by=By.CSS_SELECTOR, value=f'article[{target_turn_data}]')
                if len(target_element.find_elements(by=By.CSS_SELECTOR, value='[data-testid="copy-turn-action-button"]')) >= 1:
                    break
            except:
                # 要素が見つからなかった場合はcontinue
                continue
            time.sleep(0.5)
        time.sleep(1)


    def return_chatgpt_conversation(self):
        """
        :return: returns a list of items, even items are the submitted questions (prompts) and odd items are chatgpt response
        """

        return self.driver.find_elements(by=By.CSS_SELECTOR, value='div.text-base')

    def save_conversation(self, file_name):
        """
        It saves the full chatgpt conversation of the tab open in chrome into a text file, with the following format:
            prompt: ...
            response: ...
            delimiter
            prompt: ...
            response: ...

        :param file_name: name of the file where you want to save
        """

        directory_name = "conversations"
        if not os.path.exists(directory_name):
            os.makedirs(directory_name)

        delimiter = "|^_^|"
        chatgpt_conversation = self.return_chatgpt_conversation()
        with open(os.path.join(directory_name, file_name), "a") as file:
            for i in range(0, len(chatgpt_conversation), 2):
                file.write(
                    f"prompt: {chatgpt_conversation[i].text}\nresponse: {chatgpt_conversation[i + 1].text}\n\n{delimiter}\n\n")

    def return_last_response(self):
        """ :return: the text of the last chatgpt response """

        response_elements = self.driver.find_elements(by=By.CSS_SELECTOR, value='[data-message-author-role="assistant"]')
        return response_elements[-1].text

    @staticmethod
    def wait_for_human_verification():
        print("You need to manually complete the log-in or the human verification if required.")

        while True:
            user_input = input(
                "Enter 'y' if you have completed the log-in or the human verification, or 'n' to check again: ").lower().strip()

            if user_input == 'y':
                print("Continuing with the automation process...")
                break
            elif user_input == 'n':
                print("Waiting for you to complete the human verification...")
                time.sleep(5)  # You can adjust the waiting time as needed
            else:
                print("Invalid input. Please enter 'y' or 'n'.")

    def quit(self):
        """ Closes the browser and terminates the WebDriver session."""
        print("Closing the browser...")
        self.driver.close()
        self.driver.quit()