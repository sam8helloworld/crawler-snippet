import os
import socket
import threading
import time
import re
import pyperclip
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys


class ChatGPTAutomation:

    def __init__(self, chrome_path, chrome_driver_path, model_name, chat_id=None):
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
            url = f"https://chat.openai.com/c/{chat_id}/?model={model_name}"
        else:
            url = f"https://chat.openai.com/?model={model_name}"
        # free_port = self.find_available_port()
        free_port = 9222
        self.launch_chrome_with_remote_debugging(free_port, url)
        # self.wait_for_human_verification()
        self.driver = self.setup_webdriver(free_port)
        self.close_unneccesary_tabs()
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
            profile_directory="Profile 1"
            user_data_dir='user_data_dir_temp'
            chrome_cmd = (
                f"{self.chrome_path} --remote-debugging-port={port} "
                f"--user-data-dir={user_data_dir} --profile-directory={profile_directory} "
                f"--no-first-run --no-default-browser-check --homepage='about:blank' "
                f"--disable-background-networking {url}"
            )
            os.system(chrome_cmd)

        chrome_thread = threading.Thread(target=open_chrome)
        chrome_thread.start()

    def setup_webdriver(self, port):
        """  Initializes a Selenium WebDriver instance, connected to an existing Chrome browser
             with remote debugging enabled on the specified port"""
        chrome_options = webdriver.ChromeOptions()
        # ✅ GPUレンダリングを無効化
        chrome_options.add_argument("--disable-gpu")
        # ✅ ハードウェアアクセラレーションを無効化
        chrome_options.add_argument("--disable-software-rasterizer")
        # ✅ ログレベルを変更（WARNING以上のログのみ表示）
        chrome_options.add_argument("--log-level=3")
        # ✅ 不要なエラーを非表示
        chrome_options.add_argument("--disable-backgrounding-occluded-windows")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.binary_location = self.chrome_driver_path
        chrome_options.add_argument(f"--remote-debugging-port={port}")
        driver = webdriver.Chrome(options=chrome_options)
        return driver

    def close_unneccesary_tabs(self):
        """ 指定したURLのタブを閉じる """
        for handle in self.driver.window_handles:
            self.driver.switch_to.window(handle)
            if self.driver.current_url in ["http://support/Google/Chrome/", "http://0.0.0.1/"]:
                self.driver.close()

        # 残っているタブの中で最後のタブにフォーカスを戻す
        self.driver.switch_to.window(self.driver.window_handles[-1])
    
    def get_cookie(self):
        """
        Get chat.openai.com cookie from the running chrome instance.
        """
        cookies = self.driver.get_cookies()
        cookie = [elem for elem in cookies if elem["name"] == '__Secure-next-auth.session-token'][0]['value']
        return cookie
    
    def toggle_deep_research(self):
        try:
            # 最大10秒間、要素が表示されるまで待つ
            button = WebDriverWait(self.driver, 10).until(
                EC.visibility_of_element_located((By.XPATH, '//button[@aria-label="Deep Research"]'))
            )
            button.click()
        except Exception as e:
            print(f"ボタンの表示を待つ間にエラーが発生しました: {e}")
    
    def change_model(self, model_name):
        current_url = self.driver.current_url
        # URLを解析
        parsed_url = urlparse(current_url)
        query_params = parse_qs(parsed_url.query)  # クエリ部分を辞書に変換
        
        # クエリがない場合、新しい辞書を作成
        if not query_params:
            query_params = {}

        # クエリの値を変更（例: model=gpt-4o → model=gpt-3.5-turbo に変更）
        query_params["model"] = [model_name]

        # 新しいURLを生成
        new_query_string = urlencode(query_params, doseq=True)
        new_url = urlunparse((parsed_url.scheme, parsed_url.netloc, parsed_url.path, parsed_url.params, new_query_string, parsed_url.fragment))
        self.driver.get(new_url)
        
    def send_prompt(self, prompt, is_new_chat):
        """ Sends a message to ChatGPT and waits for 20 seconds for the response """
        if is_new_chat:
            target_turn_data = 'conversation-turn-3'
        else:
            # 最大60秒間、要素が表示されるまで待つ
            WebDriverWait(self.driver, 60).until(
                EC.visibility_of_element_located((By.TAG_NAME, 'article'))
            )
            last_turn_tag = self.driver.find_elements(by=By.TAG_NAME, value='article')[-1]
            last_turn_data = last_turn_tag.get_attribute("data-testid")
            match = re.search(r"(conversation-turn-)(\d+)", last_turn_data)
            if match:
                prefix, number = match.groups()
                target_turn_data =  f"{prefix}{int(number) + 2}"
            
        input_box = self.driver.find_element(by=By.ID, value='prompt-textarea')
        paragraphs = prompt.strip().split("\n")
        prompt_html = "".join(f"<p>{line}</p>" for line in paragraphs if line.strip())

        self.driver.execute_script(f"arguments[0].innerHTML = '{prompt_html}';", input_box)
        input_box.send_keys(Keys.RETURN)
        print("プロンプトを送信しました")
        self.check_response_ended(target_turn_data)

    def check_response_ended(self, target_turn_data):
        """ Checks if ChatGPT response ended """
        print("ChatGPTによる出力を待機中...")
        start_time = time.time()
        while time.time() - start_time <= 900:
            try:
                target_element = self.driver.find_element(by=By.CSS_SELECTOR, value=f'article[data-testid="{target_turn_data}"]')
                if len(target_element.find_elements(by=By.CSS_SELECTOR, value='[data-testid="copy-turn-action-button"]')) >= 1:
                    print(target_element.find_elements(by=By.CSS_SELECTOR, value='[data-testid="copy-turn-action-button"]')[0].text)
                    break
            except Exception as e:
                # 要素が見つからなかった場合はcontinue
                continue
            time.sleep(0.5)
        time.sleep(1)
        print("ChatGPTによる出力が完了しました")
    
    def return_last_response_markdown(self):
        try:
            # aria-label="コピーする" のボタンを探してクリック
            copy_button = self.driver.find_elements(by=By.CSS_SELECTOR, value='[data-testid="copy-turn-action-button"]')[-1]
            copy_button.click()

            # クリップボードの内容が更新されるのを待つ
            time.sleep(1)  # 必要に応じて調整

            # クリップボードの値を取得
            return pyperclip.paste()

        except Exception as e:
            print(f"エラーが発生しました: {e}")

    def get_chat_id(self):
        url = self.driver.current_url
        # 正規表現でUUIDを抽出
        match = re.search(r"/c/([a-f0-9-]+)$", url)

        if match:
            extracted_uuid = match.group(1)
            return extracted_uuid
        else:
            print("UUIDが見つかりませんでした")

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