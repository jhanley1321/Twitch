import json
import csv
from pathlib import Path
from chat_downloader import ChatDownloader


class TwitchVODChatLogger:
    def __init__(self, output_dir: str = "chat_logs"):
        self.vod_url_or_id = None
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.chat_data = []
        self.vods = []  # To store fetched VOD metadata for a streamer



    def fetch_chat(self, vod_url_or_id: str):
        """Fetch chat messages from the specified VOD."""
        # If user passed a numeric ID, turn it into a Twitch VOD URL
        s = str(vod_url_or_id).strip()
        if s.isdigit():
            s = f"https://www.twitch.tv/videos/{s}"

        self.vod_url_or_id = s
        chat = ChatDownloader().get_chat(self.vod_url_or_id)
        self.chat_data = [self._extract_message(msg) for msg in chat]
        return self.chat_data

    def _extract_message(self, msg):
        """Extract relevant fields from a chat message."""
        badges = msg.get("author", {}).get("badges", [])
        badge_str = ",".join(
            badge.get("name", badge.get("id", "")) for badge in badges
        )

        return {
            "id": msg.get("message_id"),
            "timestamp_ms": msg.get("timestamp"),
            "vod_time_s": msg.get("time_in_seconds"),
            "vod_time_str": msg.get("time_text"),
            "author": msg.get("author", {}).get("name"),
            "display_name": msg.get("author", {}).get("display_name"),
            "badges": badge_str,
            "color": msg.get("author", {}).get("colour"),
            "message": msg.get("message"),
            "message_type": msg.get("message_type"),
        }


    def save_csv(self, file_name: str = "vod_chat.csv"):
        """Save chat data to a CSV file."""
        if not self.chat_data:
            print("No chat data available. Did you call fetch_chat()?")
            return

        file_path = self.output_dir / file_name
        headers = list(self.chat_data[0].keys())

        with open(file_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=headers)
            writer.writeheader()
            writer.writerows(self.chat_data)

        print(f"CSV chat log saved to: {file_path}")

    def save_json(self, file_name: str = "vod_chat.json"):
        """Save chat data to a JSON file."""
        file_path = self.output_dir / file_name
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(self.chat_data, f, indent=2, ensure_ascii=False)
        print(f"JSON chat log saved to: {file_path}")

    def run_download_vod(self, vod_url_or_id, file_name: str = "vod_chat.csv", save_to='csv'):
        self.fetch_chat(vod_url_or_id=vod_url_or_id)
        print(f"Fetching chat for VOD: {self.vod_url_or_id}")
        if save_to == 'csv':
            self.save_csv(file_name=file_name)
            print("Downloading to CSV")
        
        elif save_to == 'json':
            self.save_json(file_name=file_name)
            print("Downloading to JSON")
        
        else:
            raise ValueError("Invalid save_to value. Must be 'csv' or 'json'.")