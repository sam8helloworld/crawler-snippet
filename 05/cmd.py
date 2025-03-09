import argparse

from chat_gpt_automation import ChatGPTAutomation
from webdriver_manager.chrome import ChromeDriverManager

BASE_URL="https://chatgpt.com/"

def main():
    parser = argparse.ArgumentParser(description="Process a text file with optional settings.")
    parser.add_argument("--file", required=True, help="Path to the text file")
    parser.add_argument("--md", action="store_true", help="Output in Markdown format")
    parser.add_argument("--mode", choices=["research", "infer", "normal"], default="normal", help="Execution mode")
    parser.add_argument("--chatid", help="Chat ID")
    
    args = parser.parse_args()
    
    try:
        with open(args.file, "r", encoding="utf-8") as f:
            content = f.read()
    except FileNotFoundError:
        print("Error: File not found.")
        return
    except Exception as e:
        print(f"Error: {e}")
        return
    
    if args.md:
        print(f"Mode: {args.md}")
    
    print(f"Mode: {args.mode}")
    if args.chatid:
        print(f"Chat ID: {args.chatid}")
    print("Content:")
    print(content)
    
    
    # 最新の chromedriver を自動インストールし、パスを取得
    chrome_driver_path = ChromeDriverManager().install()

    # Define the path where the chrome driver is installed on your computer
    # chrome_driver_path = r"/usr/local/bin/chromedriver"

    # the sintax r'"..."' is required because the space in "Program Files" in the chrome path
    chrome_path = r'"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"'

    # Create an instance
    chatgpt = ChatGPTAutomation(chrome_path, chrome_driver_path, args.chatid)

    chatgpt.send_prompt_to_chatgpt(content)

    # Retrieve the last response from ChatGPT
    response = chatgpt.return_last_response()
    print(response)

    # Save the conversation to a text file
    file_name = "conversation.txt"
    chatgpt.save_conversation(file_name)

    # Close the browser and terminate the WebDriver session
    # chatgpt.quit()


    

if __name__ == "__main__":
    main()
