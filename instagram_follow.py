from instagrapi import Client
import json
import time
import random
from datetime import datetime

class CountdownTimer:
    def __init__(self):
        self.remaining_time = 3600  # 1 hour in seconds
        
    def start_countdown(self):
        """Start or resume countdown with interruption handling"""
        while self.remaining_time > 0:
            mins, secs = divmod(self.remaining_time, 60)
            hours, mins = divmod(mins, 60)
            
            try:
                print(f"\rTime remaining: {hours:02d}:{mins:02d}:{secs:02d}", end='', flush=True)
                time.sleep(1)
                self.remaining_time -= 1
                
            except KeyboardInterrupt:
                print("\n\nTimer paused! Choose an option:")
                print("1. Skip wait and try again")
                print("2. Continue countdown")
                print("3. Stop following operation")
                
                choice = input("Choice (1-3): ")
                if choice == "1":
                    return True  # Skip wait
                elif choice == "2":
                    continue  # Resume countdown
                else:
                    return False  # Stop operation
                    
        # Timer completed naturally
        self.remaining_time = 3600  # Reset timer
        return True


class InstagramMassFollower:
    def __init__(self):
        self.client = Client()
        self.user_id = None
        self.follow_count = 0
        self.max_follows_per_session = 1000  # Instagram typically limits to ~150-200 follows per day (1000 for a whole day)
        
    def login(self, username, password):
        """Login to Instagram account with additional configuration"""
        try:
            # Set up custom device info and user agent
            self.client.set_device({
                "app_version": "203.0.0.29.118",
                "android_version": "29",
                "android_release": "10.0",
                "dpi": "640dpi",
                "resolution": "1440x2560",
                "manufacturer": "Samsung",
                "device": "SM-G973F",
                "model": "beyond1",
                "cpu": "qcom",
                "version_code": "314665256"
            })
            
            # Set custom user agent
            self.client.set_user_agent("Instagram 203.0.0.29.118 Android (29/10.0; 640dpi; 1440x2560; Samsung; SM-G973F; beyond1; qcom; en_US; 314665256)")
            
            # Attempt login
            self.client.login(username, password)
            self.user_id = self.client.user_id
            print("Successfully logged in!")
            return True
        except Exception as e:
            print(f"Login failed: {str(e)}")
            return False

    def load_json_data(self, filename):
        """Load and parse the JSON file"""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading JSON file: {str(e)}")
            return None

    def update_json_file(self, filename, data):
        """Update the JSON file with new following status"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"Error updating JSON file: {str(e)}")

    def follow_users(self, json_data, filename):
        """Follow users from the JSON data who aren't following or being followed"""
        followers_data = json_data['followers']
        users_to_follow = []
        timer = CountdownTimer()

        # Identify all users we need to follow
        for user_id, user_data in followers_data.items():
            if not user_data['you_follow_them'] and not user_data['they_follow_you']:
                users_to_follow.append({
                    'id': user_id,
                    'username': user_data['username'],
                    'full_name': user_data['full_name'],
                    'is_private': user_data['is_private']
                })

        print(f"Found {len(users_to_follow)} users to follow")
        if not users_to_follow:
            print("No users to follow!")
            return

        for user in users_to_follow:
            if self.follow_count >= self.max_follows_per_session:
                print(f"\nReached maximum follow limit ({self.max_follows_per_session})")
                print("Stopping follow operation and updating JSON...")
                break

            try:
                print(f"Following {user['full_name']} (@{user['username']})...", end='')
                success = self.client.user_follow(user['id'])

                if success or user['is_private']:
                    print(" Success!" + (" (Private account - Request sent)" if user['is_private'] else ""))
                    self.follow_count += 1
                    # Update JSON data
                    followers_data[user['id']]['you_follow_them'] = True
                    json_data['followers'] = followers_data
                    self.update_json_file(filename, json_data)
                else:
                    print(" Failed!")

                delay = random.uniform(0.1, 0.3)
                print(f"Waiting {delay:.1f} seconds...")
                time.sleep(delay)

            except Exception as e:
                if "We limit how often you can do certain things on Instagram" in str(e):
                    print("\nInstagram rate limit reached. Starting 1 hour countdown...")
                    print("(Press Ctrl+C to pause and show menu)")
                    
                    if not timer.start_countdown():
                        print("Operation stopped by user.")
                        break
                        
                    print("\nRetrying...")
                    continue
                else:
                    print(f"\nError following user: {str(e)}")
                    print("Stopping follow operation and updating JSON...")
                    break # assume worse case and end things prematurely

        print("\nOperation complete!")
        print(f"Successfully followed {self.follow_count} users")
        print("JSON file has been updated with new following status")

def main():
    # Initialize the follower
    follower = InstagramMassFollower()
    
    # Get JSON filename
    filename = input("Enter the path to your JSON file: ")
    
    # Load JSON data
    json_data = follower.load_json_data(filename)
    if not json_data:
        return
        
    # Get credentials
    username = input("Enter your Instagram username: ")
    password = input("Enter your Instagram password: ")
    
    # Login
    if not follower.login(username, password):
        return
        
    # Start following process
    follower.follow_users(json_data, filename)

if __name__ == "__main__":
    main()