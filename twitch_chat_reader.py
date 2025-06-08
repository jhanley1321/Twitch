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
    def __init__(self, channel, log_file="chat_log.csv"):
        load_dotenv()
        self.channel = channel.lower().strip('#')
        self.nickname = "justinfan12345"  # Anonymous user
        self.server = "irc.chat.twitch.tv"
        self.port = 6667
        self.socket = None
        self.is_connected = False
        self.listen_thread = None
        self.log_file = log_file
        self.csv_header = ['timestamp', 'username', 'message', 'channel', 'tags', 'raw']
        self.log_queue = queue.Queue()
        self.logging_thread = threading.Thread(target=self._log_worker, daemon=True)
        self._setup_csv()
        self.logging_thread.start()

    def _setup_csv(self):
        """Set up the CSV file with header if it doesn't exist"""
        if not os.path.exists(self.log_file):
            try:
                with open(self.log_file, 'w', newline='', encoding='utf-8') as csvfile:
                    csv_writer = csv.writer(csvfile)
                    csv_writer.writerow(self.csv_header)
            except Exception as e:
                print(f"Error setting up CSV file: {e}")

    def _log_worker(self):
        """Background thread for writing log entries asynchronously"""
        while True:
            data = self.log_queue.get()
            if data is None:
                break  # Sentinel value to stop the thread
            try:
                with open(self.log_file, 'a', newline='', encoding='utf-8') as csvfile:
                    csv_writer = csv.writer(csvfile)
                    csv_writer.writerow(data)
            except Exception as e:
                print(f"Error writing to CSV file: {e}")
            self.log_queue.task_done()

    def connect(self):
        """Connect to Twitch IRC server."""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.server, self.port))

            # Send authentication (anonymous)
            self.socket.send(f"PASS oauth:justinfan12345\r\n".encode())
            self.socket.send(f"NICK {self.nickname}\r\n".encode())
            self.socket.send(f"JOIN #{self.channel}\r\n".encode())

            # Request capabilities for better message parsing
            self.socket.send("CAP REQ :twitch.tv/tags\r\n".encode())
            self.socket.send("CAP REQ :twitch.tv/commands\r\n".encode())

            self.is_connected = True
            print(f"Connected to #{self.channel}")
            return True

        except Exception as e:
            print(f"Connection failed: {e}")
            return False

    def disconnect(self):
        """Disconnect from Twitch IRC server."""
        self.is_connected = False
        if self.socket:
            try:
                self.socket.close()
            except:
                pass
        # Stop the logging thread
        self.log_queue.put(None)
        self.logging_thread.join()
        print("Disconnected from Twitch chat")

    def _parse_message(self, response):
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

    def listen(self):
        """Listen for messages with improved buffer handling"""
        buffer = ""

        while self.is_connected:
            try:
                data = self.socket.recv(1024).decode('utf-8', errors='ignore')
                if not data:
                    break

                buffer += data

                # Process complete lines
                while '\r\n' in buffer:
                    line, buffer = buffer.split('\r\n', 1)

                    # Handle PING to stay connected
                    if line.startswith('PING'):
                        self.socket.send("PONG :tmi.twitch.tv\r\n".encode('utf-8'))
                        continue

                    # Parse chat messages
                    elif 'PRIVMSG' in line:
                        username, message, tags = self._parse_message(line)
                        if username and message:
                            message_data = {
                                'username': username,
                                'message': message,
                                'channel': self.channel,
                                'timestamp': time.time(),
                                'tags': tags,
                                'raw': line
                            }

                            self.handle_chat_message(message_data)

            except Exception as e:
                if self.is_connected:
                    print(f"Error listening: {e}")
                break

    def start_listening(self):
        """Start listening in a separate thread"""
        if not self.is_connected:
            print("Not connected to chat")
            return False

        self.listen_thread = threading.Thread(
            target=self.listen,
            args=()
        )
        self.listen_thread.daemon = True
        self.listen_thread.start()
        return True

    def stop_listening(self):
        """Stop listening and disconnect"""
        self.disconnect()
        if self.listen_thread and self.listen_thread.is_alive():
            self.listen_thread.join(timeout=1)

    def run(self):
        """Main function to run the chat reader"""
        try:
            if self.connect():
                print(f"Successfully connected to #{self.channel}")
                print("Starting to listen for messages... (Press Ctrl+C to stop)")
                self.start_listening()
                while self.is_connected:
                    time.sleep(1)
            else:
                print("Failed to connect to Twitch chat")
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

        log_data = [timestamp, username, message, self.channel, str(message_data['tags']), message_data['raw']]
        print(f"[{timestamp}] {username}: {message}")
        self.log_queue.put(log_data)

        # Add custom logic here
        if "hello" in message.lower():
            print(f"  -> {username} said hello!")

        if message_data['tags']:
            subscriber = message_data['tags'].get('subscriber', '0') == '1'
            if subscriber:
                print(f"  -> {username} is a subscriber!")

    def __str__(self):
        return f"TwitchChatReader(channel=#{self.channel}, connected={self.is_connected})"

    def __repr__(self):
        return f"TwitchChatReader(channel='{self.channel}', connected={self.is_connected})"