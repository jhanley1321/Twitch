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
        self.vod_url_or_id = vod_url_or_id
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


    def save_csv(self, filename: str = "vod_chat.csv"):
        """Save chat data to a CSV file."""
        if not self.chat_data:
            print("No chat data available. Did you call fetch_chat()?")
            return

        file_path = self.output_dir / filename
        headers = list(self.chat_data[0].keys())

        with open(file_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=headers)
            writer.writeheader()
            writer.writerows(self.chat_data)

        print(f"CSV chat log saved to: {file_path}")

    def save_json(self, filename: str = "vod_chat.json"):
        """Save chat data to a JSON file."""
        file_path = self.output_dir / filename
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(self.chat_data, f, indent=2, ensure_ascii=False)
        print(f"JSON chat log saved to: {file_path}")

    def run_download_vod(self, vod_url_or_id, save_to='csv'):
        self.fetch_chat(vod_url_or_id=vod_url_or_id)
        print(f"Fetching chat for VOD: {self.vod_url_or_id}")
        if save_to == 'csv':
            self.save_csv()
            print("Downloading to CSV")
        
        elif save_to == 'json':
            self.save_json()
            print("Downloading to JSON")
        
        else:
            raise ValueError("Invalid save_to value. Must be 'csv' or 'json'.")

    # def fetch_all_vods_chat(self, streamer_name: str, vod_limit: int = 20):
    #     """
    #     Fetch metadata for all VODs of a streamer up to vod_limit.
    #     Stores the list of VODs internally for later processing.
    #     """
    #     if not streamer_name:
    #         raise ValueError("Streamer name must be provided")

    #     user = self.api.get_user(streamer_name)
    #     if not user:
    #         raise ValueError(f"Streamer '{streamer_name}' not found")

    #     user_id = user['id']
    #     params = {
    #         'user_id': user_id,
    #         'first': vod_limit,
    #         'type': 'archive'  # Only past broadcasts (VODs)
    #     }
    #     data = self.api.get_data('videos', params=params)
    #     self.vods = data.get('data', [])
    #     if not self.vods:
    #         print(f"No VODs found for streamer '{streamer_name}'")
    #     else:
    #         print(f"Fetched {len(self.vods)} VODs for streamer '{streamer_name}'")

    # def log_all_vods_chat(self):
    #     """
    #     For each VOD fetched by fetch_all_vods_chat, download and save chat logs.
    #     Each VOD's chat logs are saved in a separate subdirectory named by VOD ID and date.
    #     """
    #     if not self.vods:
    #         print("No VODs metadata available. Did you call fetch_all_vods_chat()?")
    #         return

    #     for vod in self.vods:
    #         vod_id = vod.get('id')
    #         vod_title = vod.get('title', 'untitled').replace('/', '_').replace('\\', '_')
    #         vod_date = vod.get('created_at', '').replace(':', '-')
    #         vod_dir_name = f"{vod_date}_{vod_id}_{vod_title}"
    #         vod_dir = self.output_dir / vod_dir_name
    #         vod_dir.mkdir(parents=True, exist_ok=True)

    #         print(f"Logging chat for VOD: {vod_title} ({vod_id})")
    #         vod_logger = TwitchVODChatLogger(vod_url_or_id=vod_id, output_dir=str(vod_dir))
    #         vod_logger.run()


