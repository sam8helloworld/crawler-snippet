import argparse

from chat_gpt_automation import ChatGPTAutomation
import chromedriver_autoinstaller

def main():
    parser = argparse.ArgumentParser(description="Process a text file with optional settings.")
    parser.add_argument("--model", default="gpt-4o", help="AI model")
    parser.add_argument("--research", action="store_true", default=False, help="Using deep Reasearch.")
    parser.add_argument("--file", required=True, help="Path to the text file")
    parser.add_argument("--md", action="store_true", help="Output in Markdown format")
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

    chrome_driver_path = chromedriver_autoinstaller.install()

    chrome_path = r'"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"'

    chatgpt = ChatGPTAutomation(chrome_path, chrome_driver_path, args.model, args.chatid)
    
    # Deep Researchのオンオフを設定する
    if args.research:
        chatgpt.toggle_deep_research()
        print("Deep ResearchをONにしました")
    
    is_new_chat = True if args.chatid is None else False
    chatgpt.send_prompt(content, is_new_chat)

    # # Retrieve the last response from ChatGPT
    if args.md:
        response = chatgpt.return_last_response_markdown()
        print(response)
    else:    
        response = chatgpt.return_last_response()
        print(response)
    
    if args.chatid is None:
        chat_id = chatgpt.get_chat_id()
        print(f"生成されたチャットID: {chat_id}")

    # Close the browser and terminate the WebDriver session
    chatgpt.quit()

if __name__ == "__main__":
    main()
