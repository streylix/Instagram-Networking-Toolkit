from instagrapi import Client
import time
import json
from datetime import datetime
import random
import os
import getpass

from instagram_finder import InstagramFollowerFetcher
from instgram_unfollow import InstagramUnfollower

class InstagramManager:
    def __init__(self):
        self.client = Client()
        self.fetcher = None
        self.unfollow_tool = None
        
        # Create data directory if it doesn't exist
        self.data_dir = 'data'
        os.makedirs(self.data_dir, exist_ok=True)
        
        # Update file paths to use data directory
        self.following_cache_file = os.path.join(self.data_dir, 'following_cache.json')
        self.followers_cache_file = os.path.join(self.data_dir, 'followers_cache.json')
        
    def _save_relationship_cache(self, following, followers):
        """Save following and followers to cache files"""
        try:
            # Save following cache
            with open(self.following_cache_file, 'w', encoding='utf-8') as f:
                json.dump(following, f, indent=4, ensure_ascii=False)
            
            # Save followers cache
            with open(self.followers_cache_file, 'w', encoding='utf-8') as f:
                json.dump(followers, f, indent=4, ensure_ascii=False)
            
            print("Relationship lists cached successfully.")
        except Exception as e:
            print(f"Error saving relationship cache: {str(e)}")
    
    def _load_relationship_cache(self):
        """Load following and followers from cache files"""
        try:
            # Check if cache files exist
            if not (os.path.exists(self.following_cache_file) and 
                    os.path.exists(self.followers_cache_file)):
                return None, None
            
            # Load following cache
            with open(self.following_cache_file, 'r', encoding='utf-8') as f:
                following = json.load(f)
            
            # Load followers cache
            with open(self.followers_cache_file, 'r', encoding='utf-8') as f:
                followers = json.load(f)
            
            print("Relationship lists loaded from cache.")
            return following, followers
        
        except Exception as e:
            print(f"Error loading relationship cache: {str(e)}")
            return None, None
    
    def login(self, username, password):
        """Login and initialize tools with caching"""
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
            
            # Login
            self.client.login(username, password)
            
            print("Successfully logged in!")
            return True
            
        except Exception as e:
            print(f"Login failed: {str(e)}")
            return False
    
    def show_menu(self):
        """Display main menu"""
        while True:
            try:
                print("\n=== Instagram Manager ===")
                print("1. Fetch followers from a user")
                print("2. Unfollow non-followers")
                print("3. Exit")
                
                choice = input("\nEnter your choice (1-3): ")
                
                if choice == "1":
                    self._initialize_shared_tools()
                    self.run_fetcher()
                elif choice == "2":
                    self._initialize_shared_tools()
                    self.run_unfollow()
                elif choice == "3":
                    print("Goodbye!")
                    break
                else:
                    print("Invalid choice. Please try again.")
            except KeyboardInterrupt:
                continue
    
    def _initialize_shared_tools(self):
        """Initialize tools with shared client and relationships"""
        # Try to load from cache first
        following_cache, followers_cache = self._load_relationship_cache()
        
        if not following_cache or not followers_cache:
            # If no cache, fetch from API
            print("Fetching relationships from API...")
            fetcher = InstagramFollowerFetcher()
            fetcher.client = self.client
            fetcher.user_id = self.client.user_id
            
            # Fetch following and followers
            following_users = fetcher.client.user_following_v1(fetcher.user_id, amount=0)
            follower_users = fetcher.client.user_followers_v1(fetcher.user_id, amount=0)
            
            # Convert to dictionaries
            following_cache = {user.pk: user.username for user in following_users}
            followers_cache = {user.pk: user.username for user in follower_users}
            
            # Save to cache for future use
            self._save_relationship_cache(following_cache, followers_cache)
        
        return following_cache, followers_cache
    
    def run_fetcher(self):
        """Run the follower fetcher functionality"""
        # Initialize fetcher
        self.fetcher = InstagramFollowerFetcher()
        self.fetcher.client = self.client
        self.fetcher.user_id = self.client.user_id

        while True:
            target_username = input("\nEnter the username whose followers you want to fetch (or 'random' for random pick): ")
            
            if target_username.lower() == 'random':
                # Get random following username from cache
                following_cache, _ = self._load_relationship_cache()
                if not following_cache:
                    print("No following list available. Please try again.")
                    return
                
                random_user = random.choice(list(following_cache.values()))
                print(f"\nRandom pick: {random_user}")
                confirm = input("Would you like to fetch followers for this user? (y/n): ")
                
                if confirm.lower() != 'y':
                    continue
                
                target_username = random_user
            
            target_user_id = self.fetcher.get_user_id(target_username)
            if target_user_id:
                break
            print("Could not find user. Please check the username and try again.")
        
        # Get followers with retry mechanism
        max_retries = 3
        retry_count = 0
        followers = None

        option = int(input("(1) followers (2) following for selected user (default is followers): "))
        
        while retry_count < max_retries:
            followers = self.fetcher.get_user_followers(target_user_id, option)
            if followers:
                break
            retry_count += 1
            if retry_count < max_retries:
                wait_time = 60 * retry_count
                print(f"\nRetrying in {wait_time} seconds... (Attempt {retry_count + 1}/{max_retries})")
                time.sleep(wait_time)
        
        if not followers:
            print("Failed to fetch followers after multiple attempts. Please try again later.")
            return
        
        # Modify save_followers_to_file to use data directory
        output_data = {
            'target_user': target_username,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'follower_count': len(followers),
            'relationship_summary': {
                'you_follow': sum(1 for f in followers.values() if f['you_follow_them']),
                'follow_you': sum(1 for f in followers.values() if f['they_follow_you']),
                'mutual_followers': sum(1 for f in followers.values() if f['you_follow_them'] and f['they_follow_you'])
            },
            'followers': followers
        }
        
        # Ensure the data directory exists
        os.makedirs(self.data_dir, exist_ok=True)
        
        # Generate filename in the data directory
        filename = os.path.join(self.data_dir, f'{target_username}_followers.json')
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=4, ensure_ascii=False)
            
        print(f"\nFollowers list saved to {filename}")

    def run_unfollow(self):
        """Run unfollow tool"""
        # Initialize unfollow tool
        self.unfollow_tool = InstagramUnfollower()
        self.unfollow_tool.client = self.client
        self.unfollow_tool.user_id = self.client.user_id

        # Get cached relationships
        following_cache, followers_cache = self._load_relationship_cache()

        # Find non-followers
        non_followers = []
        for user_id, username in following_cache.items():
            if user_id not in followers_cache:
                non_followers.append({
                    'user_id': user_id,
                    'username': username
                })
        
        # Show summary
        print(f"\nFound {len(non_followers)} users who don't follow you back:")
        for user in non_followers:
            print(f"- {user['username']}")
        
        # Confirm before unfollowing
        if input("\nWould you like to unfollow these users? (y/n): ").lower() != 'y':
            print("Operation cancelled")
            return
        
        delay_range = (0.1, 0.3)
        
        # Perform unfollow
        success, failed = self.unfollow_tool.unfollow_users(non_followers, delay_range)
        
        # Update cache after unfollowing
        if success > 0:
            # Remove unfollowed users from cache
            for user in non_followers[:success]:
                if user['user_id'] in following_cache:
                    del following_cache[user['user_id']]
            
            # Save updated cache
            self._save_relationship_cache(following_cache, followers_cache)
        
        # Save results to log
        self.unfollow_tool.save_log(non_followers)
        
        # Show results
        print(f"\nOperation complete:")
        print(f"Successfully unfollowed: {success}")
        print(f"Failed to unfollow: {failed}")

def main():
    manager = InstagramManager()
    
    # Get credentials once with hidden password input
    username = input("Enter your Instagram username: ")
    password = getpass.getpass("Enter your Instagram password: ")
    
    # Login
    if not manager.login(username, password):
        return
    
    # Show menu
    manager.show_menu()

if __name__ == "__main__":
    main()