# main.py
# from twitch_api import TwitchAPI
# from twitch_chat_reader import TwitchChatReader
# from sully import SullyGnomeScraper
from vod_logger import TwitchVODChatLogger


# Run to get user info
def main():
    twitch = TwitchAPI()

    # Get user info
    user = twitch.get_user('shroud')
    if user:
        print(f"User: {user['display_name']}")
        print(f"Description: {user['description']}")
    else:
        print("User not found.")

    # Get top 5 games
    games = twitch.get_top_games(5)
    print("\nTop 5 Games:")
    for game in games:
        print(f"- {game['name']}")






# Run logic for logging chat history 
# def main():
#     # Set the channel names directly in the script
#     channel_names = ["therealtianamusarra", "shannonmais", "Taylor_Jevaux", "Haunnibuni"]  # Replace with your desired channel names

#     # Initialize the chat reader
#     chat = TwitchChatReader(channel_names)

#     # Run the chat reader
#     chat.run()


# # sullyghone puller)
# def main():
#     # Get the content creator's name from the user
#     creator_name = input("Enter the content creator's name: ").strip()

#     # Initialize the scraper
#     scraper = SullyGnomeScraper(creator_name)

#     # Run the scraper
#     scraper.run()


# Run Twitch vod logger
def main():
    # vod_input = input("Enter Twitch VOD URL or ID: ").strip()
    TwitchVod = TwitchVODChatLogger(output_dir="chat_logs")
    TwitchVod.run_download_vod(vod_url_or_id = 'https://www.twitch.tv/videos/2526604149' )
    # logger.fetch_all_vods_chat("Haunibunni", vod_limit=10)
    # logger.log_all_vods_chat()
    # logger.run()


if __name__ == "__main__":
    main()