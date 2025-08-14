# twitch_chat_reader.py
import os
import socket
import threading
import time
import re
import csv
import queue
from dotenv import load_dotenv

class TwitchChatReader:
    def __init__(self, channels, log_directory="chat_logs"):
        load_dotenv()
        self.channels = [channel.lower().strip('#') for channel in channels]
        self.nickname = "justinfan12345"  # Anonymous user
        self.server = "irc.chat.twitch.tv"
        self.port = 6667
        self.sockets = {}
        self.is_connected = False
        self.listen_threads = {}
        self.log_directory = log_directory
        os.makedirs(self.log_directory, exist_ok=True)  # Create log directory if it doesn't exist
        self.log_queues = {}
        self.logging_threads = {}
        self.csv_header = ['timestamp', 'username', 'message', 'channel', 'tags', 'raw']

        for channel in self.channels:
            self.log_queues[channel] = queue.Queue()
            log_file = os.path.join(self.log_directory, f"{channel}_chat_log.csv")
            self.logging_threads[channel] = threading.Thread(target=self._log_worker, args=(channel, log_file), daemon=True)
            self._setup_csv(channel, log_file)
            self.logging_threads[channel].start()

    def _setup_csv(self, channel, log_file):
        """Set up the CSV file with header if it doesn't exist"""
        if not os.path.exists(log_file):
            try:
                with open(log_file, 'w', newline='', encoding='utf-8') as csvfile:
                    csv_writer = csv.writer(csvfile)
                    csv_writer.writerow(self.csv_header)
            except Exception as e:
                print(f"Error setting up CSV file for {channel}: {e}")

    def _log_worker(self, channel, log_file):
        """Background thread for writing log entries asynchronously"""
        while True:
            data = self.log_queues[channel].get()
            if data is None:
                break  # Sentinel value to stop the thread
            try:
                with open(log_file, 'a', newline='', encoding='utf-8') as csvfile:
                    csv_writer = csv.writer(csvfile)
                    csv_writer.writerow(data)
            except Exception as e:
                print(f"Error writing to CSV file for {channel}: {e}")
            self.log_queues[channel].task_done()

    def connect(self, channel):
        """Connect to Twitch IRC server for a specific channel."""
        try:
            self.sockets[channel] = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sockets[channel].connect((self.server, self.port))

            # Send authentication (anonymous)
            self.sockets[channel].send(f"PASS oauth:justinfan12345\r\n".encode())
            self.sockets[channel].send(f"NICK {self.nickname}\r\n".encode())
            self.sockets[channel].send(f"JOIN #{channel}\r\n".encode())

            # Request capabilities for better message parsing
            self.sockets[channel].send("CAP REQ :twitch.tv/tags\r\n".encode())
            self.sockets[channel].send("CAP REQ :twitch.tv/commands\r\n".encode())

            print(f"Connected to #{channel}")
            return True

        except Exception as e:
            print(f"Connection failed for {channel}: {e}")
            return False

    def disconnect(self):
        """Disconnect from Twitch IRC server."""
        self.is_connected = False
        for channel in self.channels:
            if channel in self.sockets and self.sockets[channel]:
                try:
                    self.sockets[channel].close()
                except:
                    pass
            # Stop the logging thread
            self.log_queues[channel].put(None)
            self.logging_threads[channel].join()
        print("Disconnected from Twitch chat")

    def _parse_message(self, response, channel):
        """Parse IRC message and extract username and message with enhanced parsing"""
        try:
            if 'PRIVMSG' in response:
                # Handle messages with tags (enhanced parsing)
                if response.startswith('@'):
                    # Extract tags and message
                    parts = response.split(' ', 3)
                    if len(parts) >= 4:
                        tags = self._parse_tags(parts[0])
                        message_match = re.search(r':(.+)$', parts[3])
                        if message_match:
                            username = tags.get('display-name', 'Unknown')
                            message = message_match.group(1).strip()
                            return username, message, tags

                # Fallback to basic parsing
                username = response.split('!')[0][1:]
                message = response.split('PRIVMSG')[1].split(':', 1)[1].strip()
                return username, message, {}
        except Exception as e:
            print(f"Error parsing message: {e}")
        return None, None, {}

    def _parse_tags(self, tag_string):
        """Parse IRC tags from message"""
        tags = {}
        tag_string = tag_string.lstrip('@')

        for tag in tag_string.split(';'):
            if '=' in tag:
                key, value = tag.split('=', 1)
                tags[key] = value

        return tags

    def listen(self, channel):
        """Listen for messages with improved buffer handling"""
        socket = self.sockets[channel]
        buffer = ""

        while self.is_connected and socket:
            try:
                data = socket.recv(1024).decode('utf-8', errors='ignore')
                if not data:
                    break

                buffer += data

                # Process complete lines
                while '\r\n' in buffer:
                    line, buffer = buffer.split('\r\n', 1)

                    # Handle PING to stay connected
                    if line.startswith('PING'):
                        socket.send("PONG :tmi.twitch.tv\r\n".encode('utf-8'))
                        continue

                    # Parse chat messages
                    elif 'PRIVMSG' in line:
                        username, message, tags = self._parse_message(line, channel)
                        if username and message:
                            message_data = {
                                'username': username,
                                'message': message,
                                'channel': channel,
                                'timestamp': time.time(),
                                'tags': tags,
                                'raw': line
                            }

                            self.handle_chat_message(message_data)

            except Exception as e:
                if self.is_connected:
                    print(f"Error listening to {channel}: {e}")
                break

    def start_listening(self):
        """Start listening in a separate thread for each channel"""
        self.is_connected = True
        for channel in self.channels:
            if channel not in self.sockets or not self.sockets[channel]:
                if not self.connect(channel):
                    print(f"Failed to connect to {channel}, skipping")
                    continue

            self.listen_threads[channel] = threading.Thread(
                target=self.listen,
                args=(channel,)
            )
            self.listen_threads[channel].daemon = True
            self.listen_threads[channel].start()

    def stop_listening(self):
        """Stop listening and disconnect"""
        self.disconnect()
        for channel in self.channels:
            if channel in self.listen_threads and self.listen_threads[channel].is_alive():
                self.listen_threads[channel].join(timeout=1)

    def run(self):
        """Main function to run the chat reader"""
        try:
            self.start_listening()
            while self.is_connected:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\nStopping chat listener...")
        except Exception as e:
            print(f"Error: {e}")
        finally:
            self.stop_listening()
            print("Chat listener stopped")

    def handle_chat_message(self, message_data):
        """Custom message handler"""
        username = message_data['username']
        message = message_data['message']
        timestamp = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(message_data['timestamp']))
        channel = message_data['channel']

        log_data = [timestamp, username, message, channel, str(message_data['tags']), message_data['raw']]
        print(f"[{timestamp}] {username}: {message} (Channel: {channel})")
        self.log_queues[channel].put(log_data)

        # Add custom logic here
        if "hello" in message.lower():
            print(f"  -> {username} said hello!")

        if message_data['tags']:
            subscriber = message_data['tags'].get('subscriber', '0') == '1'
            if subscriber:
                print(f"  -> {username} is a subscriber!")

    def __str__(self):
        return f"TwitchChatReader(channels={self.channels}, connected={self.is_connected})"

    def __repr__(self):
        return f"TwitchChatReader(channels={self.channels}, connected={self.is_connected})"