# main.py
from dotenv import load_dotenv
load_dotenv()
# from twitch_client import TwitchClient 
# from twitch_vod_chat_logger import TwitchVODChatLogger





from twitch_master import Twitch

def main():
    twitch = Twitch()
    twitch.connect()
    vod_ids = twitch.get_vod_ids("haunibunni")
    print("Found", len(vod_ids), "VODs. First:", vod_ids[0] if vod_ids else None)

    # Use TwitchVODChatLogger methods
    if vod_ids:
        # twitch.run_download_vod(vod_url_or_id=vod_ids[0], save_to='csv')
        twitch.fetch_and_save_multiple_vods("haunibunni", vod_ids, save_to='csv')

    twitch.disconnect()

if __name__ == "__main__":
    main()