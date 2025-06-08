# twitch_chat_reader.py
import os
import socket
import threading
import time
import re
from dotenv import load_dotenv

class TwitchChatReader:
    def __init__(self, channel):
        load_dotenv()
        self.channel = channel.lower().strip('#')
        self.nickname = "justinfan12345"  # Anonymous user
        self.server = "irc.chat.twitch.tv"
        self.port = 6667
        self.socket = None
        self.is_connected = False
        self.listen_thread = None

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
            # Connect to a channel (replace with desired channel)
            if self.connect():
                print(f"Successfully connected to #{self.channel}")
                print("Starting to listen for messages... (Press Ctrl+C to stop)")

                # Start listening with custom callback
                self.start_listening()

                # Keep the main thread alive
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
        timestamp = time.strftime('%H:%M:%S', time.localtime(message_data['timestamp']))

        print(f"[{timestamp}] {username}: {message}")

        # Add custom logic here
        if "hello" in message.lower():
            print(f"  -> {username} said hello!")

        # You can also access tags for more info
        if message_data['tags']:
            subscriber = message_data['tags'].get('subscriber', '0') == '1'
            if subscriber:
                print(f"  -> {username} is a subscriber!")

    def __str__(self):
        """String representation"""
        return f"TwitchChatReader(channel=#{self.channel}, connected={self.is_connected})"

    def __repr__(self):
        """Developer representation"""
        return f"TwitchChatReader(channel='{self.channel}', connected={self.is_connected})"

