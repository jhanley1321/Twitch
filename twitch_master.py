from twitch_client import TwitchCon
from twitch_vod_chat_logger import TwitchVODChatLogger

class Twitch(TwitchCon, TwitchVODChatLogger):
    def __init__(self, client_id=None, client_secret=None, output_dir="chat_logs"):
        # Initialize both parent classes explicitly
        TwitchCon.__init__(self, client_id=client_id, client_secret=client_secret)
        TwitchVODChatLogger.__init__(self, output_dir=output_dir)

    def fetch_and_save_multiple_vods(self, streamer_name: str, vod_ids: list, save_to: str = 'json'):
        """
        Given a list of VOD IDs, fetch chat for each and save to a file named <streamer_name>_<vod_id>.<ext>.
        Supports 'csv' and 'json' file types. Defaults to 'csv'.
        """
    
        # ADD: Create logic so that given streamer_name, will look up user_id
        self.get_user(login = streamer_name)
        
        for vod_id in vod_ids:
            # Fetch chat for the current VOD ID
            self.fetch_chat(vod_id)
            # Construct filename with streamer name and vod id
            file_name = f"{self.user_id}_{vod_id}.{save_to}"
            # Save chat data in the requested format
            if save_to == 'csv':
                self.save_csv(file_name=file_name)
            elif save_to == 'json':
                self.save_json(file_name=file_name)
            else:
                raise ValueError("Invalid save_to value. Must be 'csv' or 'json'.")

   

    
    def run_fetch_and_save_multiple_vods(self, streamer_name: str, save_to: str = 'json', limit: int = None):
            """
            Encapsulates the default flow:
            - connect
            - fetch VOD ids for streamer_name
            - print summary
            - fetch and save chats for each VOD (optionally limited)
            - disconnect

            Args:
                streamer_name: Twitch login name (lowercase).
                save_to: 'csv' or 'json' for chat export format.
                limit: if provided, only process the first N VODs.
            """
            try:
                # self.connect()
                vod_ids = self.get_vod_ids(streamer_name)
                print(f"Found {len(vod_ids)} VODs. First: {vod_ids[0] if vod_ids else None}")

                if limit is not None:
                    vod_ids = vod_ids[:limit]

                if vod_ids:
                    self.fetch_and_save_multiple_vods(streamer_name, vod_ids, save_to=save_to)
            finally:
                self.disconnect()