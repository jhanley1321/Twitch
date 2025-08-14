# main.py
from dotenv import load_dotenv
load_dotenv()
from twitch import TwitchClient 
from twitch_vod_chat_logger import TwitchVODChatLogger





# Get Vod Id
def main():
    client = TwitchClient()
    try:
        client.connect()
        vod_ids = client.get_vod_ids("summit1g")
        print("Found", len(vod_ids), "VODs. First:", vod_ids[0] if vod_ids else None)
        print(vod_ids[0])
    finally:
        client.disconnect()


    # TwitchVod = TwitchVODChatLogger(output_dir="chat_logs")
    # TwitchVod.run_download_vod(vod_url_or_id = str(vod_ids[0]) )

    


if __name__ == "__main__":
    main()