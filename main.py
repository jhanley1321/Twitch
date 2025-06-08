# main.py
from twitch_api import TwitchAPI

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

if __name__ == "__main__":
    main()