# main.py
from dotenv import load_dotenv
load_dotenv()
# from twitch_client import TwitchClient 
# from twitch_vod_chat_logger import TwitchVODChatLogger
from twitch_master import Twitch



def main():
    twitch = Twitch()
    twitch.run_fetch_and_save_multiple_vods(streamer_name="haunibunni", save_to="json", limit=None) # 
    # twitch.get_user_info(login="haunibunni")
    # twitch.get_user(login="haunibunni")
    # print(twitch.user_id)

if __name__ == "__main__":
    main()