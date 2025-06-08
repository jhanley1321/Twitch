# main.py
from twitch_api import TwitchAPI
from twitch_chat_reader import TwitchChatReader

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




def main():
    # Get channel name from user
    channel_name = input("Enter Twitch channel name: ").strip()

    # Initialize the chat reader
    chat = TwitchChatReader(channel_name)

    # Run the chat reader
    chat.run()




if __name__ == "__main__":
    main()