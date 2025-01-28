from instagrapi import Client
import time
import json
from datetime import datetime
import random
import os
import getpass

from instagram_finder import InstagramFollowerFetcher
from instagram_follow import InstagramMassFollower
from instgram_unfollow import InstagramUnfollower

class WhitelistManager:
    def __init__(self, data_dir='data', client=None):
        self.data_dir = data_dir
        self.client = client
        os.makedirs(data_dir, exist_ok=True)
        
    def _get_whitelist_path(self, username, list_type):
        """Generate whitelist file path for a specific user and list type"""
        return os.path.join(self.data_dir, f'{username}_{list_type}_whitelist.json')
    
    def _validate_instagram_user(self, username):
        """Validate if the username exists on Instagram"""
        if not self.client:
            print("Instagram client not initialized for user validation.")
            return False
        
        try:
            # Try to get user info
            user_info = self.client.user_info_by_username(username)
            return True
        except Exception as e:
            print(f"Error: {username} is not a valid Instagram user.")
            return False
    
    def add_to_whitelist(self, username, list_type):
        """Add users to a specific whitelist"""
        # Determine which whitelist to use
        if list_type not in ['unfollow', 'followers']:
            print("Invalid whitelist type. Choose 'unfollow' or 'followers'.")
            return
        
        # Get the whitelist file path
        whitelist_path = self._get_whitelist_path(username, list_type)
        
        # Load existing whitelist
        try:
            with open(whitelist_path, 'r') as f:
                whitelist = json.load(f)
        except FileNotFoundError:
            whitelist = []
        
        # Prompt for usernames to add
        while True:
            user_to_add = input(f"Enter username to add to {list_type} whitelist (or press Enter to finish): ").strip()
            
            if not user_to_add:
                break
            
            # Validate the user
            if not self._validate_instagram_user(user_to_add):
                continue
            
            if user_to_add not in whitelist:
                whitelist.append(user_to_add)
                print(f"Added {user_to_add} to {list_type} whitelist.")
                # Save updated whitelist
                with open(whitelist_path, 'w') as f:
                    json.dump(whitelist, f, indent=4)
                
                print(f"{list_type.capitalize()} whitelist updated.")
            else:
                print(f"{user_to_add} is already in the {list_type} whitelist.")
        
    
    def remove_from_whitelist(self, username, list_type):
        """Remove users from a specific whitelist"""
        # Determine which whitelist to use
        if list_type not in ['unfollow', 'followers']:
            print("Invalid whitelist type. Choose 'unfollow' or 'followers'.")
            return
        
        # Get the whitelist file path
        whitelist_path = self._get_whitelist_path(username, list_type)
        
        # Load existing whitelist
        try:
            with open(whitelist_path, 'r') as f:
                whitelist = json.load(f)
        except FileNotFoundError:
            print(f"No {list_type} whitelist found for this user.")
            return
        
        # Prompt for usernames to remove
        while True:
            user_to_remove = input(f"Enter username to remove from {list_type} whitelist (or press Enter to finish): ").strip()
            
            if not user_to_remove:
                break
            
            if user_to_remove in whitelist:
                whitelist.remove(user_to_remove)
                print(f"Removed {user_to_remove} from {list_type} whitelist.")
                # Save updated whitelist
                with open(whitelist_path, 'w') as f:
                    json.dump(whitelist, f, indent=4)
                
                print(f"{list_type.capitalize()} whitelist updated.")
            else:
                print(f"{user_to_remove} is not in the {list_type} whitelist.")
        
    
    def get_whitelist(self, username, list_type):
        """Retrieve a specific whitelist"""
        # Determine which whitelist to use
        if list_type not in ['unfollow', 'followers']:
            print("Invalid whitelist type. Choose 'unfollow' or 'followers'.")
            return []
        
        # Get the whitelist file path
        whitelist_path = self._get_whitelist_path(username, list_type)
        
        # Load whitelist
        try:
            with open(whitelist_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return []

class InstagramManager:
    def __init__(self):
        self.client = Client()
        self.fetcher = None
        self.follower = None
        self.unfollow_tool = None
        self.current_username = None
        
        # Create data directory if it doesn't exist
        self.data_dir = 'data'
        os.makedirs(self.data_dir, exist_ok=True)
        
        # Device settings file
        self.device_file = os.path.join(self.data_dir, 'device_settings.json')
        
        # Whitelist management
        self.whitelist_manager = WhitelistManager(self.data_dir)
    
    def _save_device_settings(self, device_settings):
        """Save device settings to a file"""
        try:
            with open(self.device_file, 'w') as f:
                json.dump(device_settings, f, indent=4)
            print("Device settings saved successfully.")
        except Exception as e:
            print(f"Error saving device settings: {e}")
    
    def _load_device_settings(self):
        """Load device settings from file"""
        try:
            if os.path.exists(self.device_file):
                with open(self.device_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Error loading device settings: {e}")
        return None
    
    def _generate_device_settings(self):
        """Generate a default device configuration"""
        device_settings = {
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
        }
        
        # Save the new settings for future use
        self._save_device_settings(device_settings)
        
        return device_settings
    
    def _get_device_settings(self):
        """
        Retrieve existing device settings or generate new ones.
        Ensures consistent device configuration across sessions.
        """
        # Try to load existing settings
        existing_settings = self._load_device_settings()
        
        if existing_settings:
            print("Using existing device configuration.")
            return existing_settings
        
        # Generate new settings if none exist
        print("Generated new device configuration.")
        return self._generate_device_settings()

    def _get_username_specific_path(self, base_filename):
        """Generate a username-specific file path"""
        if not self.current_username:
            raise ValueError("No username set. Please log in first.")
        return os.path.join(self.data_dir, f'{self.current_username}_{base_filename}')
    
    def _save_relationship_cache(self, following, followers):
        """Save following and followers to cache files"""
        try:
            # Generate username-specific paths
            following_cache_file = self._get_username_specific_path('following_cache.json')
            followers_cache_file = self._get_username_specific_path('followers_cache.json')
            
            # Save following cache
            with open(following_cache_file, 'w', encoding='utf-8') as f:
                json.dump(following, f, indent=4, ensure_ascii=False)
            
            # Save followers cache
            with open(followers_cache_file, 'w', encoding='utf-8') as f:
                json.dump(followers, f, indent=4, ensure_ascii=False)
            
            print("Relationship lists cached successfully.")
        except Exception as e:
            print(f"Error saving relationship cache: {str(e)}")
    
    def _load_relationship_cache(self):
        """Load following and followers from cache files"""
        try:
            # Generate username-specific paths
            following_cache_file = self._get_username_specific_path('following_cache.json')
            followers_cache_file = self._get_username_specific_path('followers_cache.json')
            
            # Check if cache files exist
            if not (os.path.exists(following_cache_file) and 
                    os.path.exists(followers_cache_file)):
                return None, None
            
            # Load following cache
            with open(following_cache_file, 'r', encoding='utf-8') as f:
                following = json.load(f)
            
            # Load followers cache
            with open(followers_cache_file, 'r', encoding='utf-8') as f:
                followers = json.load(f)
            
            print("Relationship lists loaded from cache.")
            return following, followers
        
        except Exception as e:
            print(f"Error loading relationship cache: {str(e)}")
            return None, None

    def login(self, username, password):
        """Login and initialize tools with caching and persistent device settings"""
        try:
            # Set current username
            self.current_username = username
            
            # Get consistent device settings
            device_settings = self._get_device_settings()
            
            # Set device configuration
            self.client.set_device(device_settings)
            
            # Set user agent based on device settings
            user_agent = (f"Instagram {device_settings['app_version']} "
                          f"Android ({device_settings['android_version']}/{device_settings['android_release']}; "
                          f"{device_settings['dpi']}; {device_settings['resolution']}; "
                          f"{device_settings['manufacturer']}; {device_settings['device']}; "
                          f"{device_settings['model']}; {device_settings['cpu']}; "
                          f"en_US; {device_settings['version_code']}")
            
            self.client.set_user_agent(user_agent)
            
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
                print("2. Follow users from JSON file")
                print("3. Unfollow non-followers")
                print("4. Manage Whitelists")
                print("5. Exit")
                
                choice = input("\nEnter your choice (1-5): ")
                
                if choice == "1":
                    self._initialize_shared_tools()
                    self.run_fetcher()
                elif choice == "2":
                    self.run_follower()
                elif choice == "3":
                    self._initialize_shared_tools()
                    self.run_unfollow()
                elif choice == "4":
                    self.manage_whitelists()
                elif choice == "5":
                    print("Goodbye!")
                    break
                else:
                    print("Invalid choice. Please try again.")
            except KeyboardInterrupt:
                continue
    
    def manage_whitelists(self):
        """Manage whitelist options"""
        # Ensure the whitelist manager has access to the client for user validation
        self.whitelist_manager.client = self.client
        
        while True:
            print("\n=== Whitelist Management ===")
            print("1. Add to Unfollow Whitelist")
            print("2. Remove from Unfollow Whitelist")
            print("3. Add to Followers Scrape Whitelist")
            print("4. Remove from Followers Scrape Whitelist")
            print("5. View Unfollow Whitelist")
            print("6. View Followers Scrape Whitelist")
            print("7. Return to Main Menu")
            
            choice = input("\nEnter your choice (1-7): ")
            
            if choice == "1":
                self.whitelist_manager.add_to_whitelist(self.current_username, 'unfollow')
            elif choice == "2":
                self.whitelist_manager.remove_from_whitelist(self.current_username, 'unfollow')
            elif choice == "3":
                self.whitelist_manager.add_to_whitelist(self.current_username, 'followers')
            elif choice == "4":
                self.whitelist_manager.remove_from_whitelist(self.current_username, 'followers')
            elif choice == "5":
                unfollow_whitelist = self.whitelist_manager.get_whitelist(self.current_username, 'unfollow')
                print("\nUnfollow Whitelist:")
                if unfollow_whitelist:
                    for user in unfollow_whitelist:
                        print(user)
                else:
                    print("No users in the unfollow whitelist.")
                input("\nPress Enter to continue...")
            elif choice == "6":
                followers_whitelist = self.whitelist_manager.get_whitelist(self.current_username, 'followers')
                print("\nFollowers Scrape Whitelist:")
                if followers_whitelist:
                    for user in followers_whitelist:
                        print(user)
                else:
                    print("No users in the followers scrape whitelist.")
                input("\nPress Enter to continue...")
            elif choice == "7":
                break
            else:
                print("Invalid choice. Please try again.")

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

        # Get followers scrape whitelist
        followers_whitelist = self.whitelist_manager.get_whitelist(self.current_username, 'followers')

        while True:
            target_username = input("\nEnter the username whose followers you want to fetch (or 'random' for random pick): ")
            
            # Check if target is in followers whitelist
            if target_username.lower() != 'random' and target_username in followers_whitelist:
                print(f"{target_username} is in the followers scrape whitelist. Cannot fetch.")
                continue
            
            if target_username.lower() == 'random':
                # Get random following username from cache
                following_cache, _ = self._load_relationship_cache()
                if not following_cache:
                    print("No following list available. Please try again.")
                    return
                
                random_users = [
                    username for username in following_cache.values() 
                    if username not in followers_whitelist
                ]
                
                if not random_users:
                    print("No available users to fetch followers from.")
                    return
                
                random_user = random.choice(random_users)
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
        filename = os.path.join(self.data_dir, f'{self.current_username}_{target_username}_followers.json')
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=4, ensure_ascii=False)
            
        print(f"\nFollowers list saved to {filename}")

    def run_follower(self):
        """Run the mass follower functionality"""        
        self.follower = InstagramMassFollower()
        self.follower.client = self.client
        self.follower.user_id = self.client.user_id

        filename = input("Enter the path to your JSON file: ")
        json_data = self.follower.load_json_data(filename)
        
        if not json_data:
            return
            
        self.follower.follow_users(json_data, filename)

    def run_unfollow(self):
        """Run unfollow tool"""
        # Initialize unfollow tool
        self.unfollow_tool = InstagramUnfollower()
        self.unfollow_tool.client = self.client
        self.unfollow_tool.user_id = self.client.user_id

        # Get cached relationships
        following_cache, followers_cache = self._load_relationship_cache()

        # Get unfollow whitelist
        unfollow_whitelist = self.whitelist_manager.get_whitelist(self.current_username, 'unfollow')

        # Find non-followers, excluding whitelisted users
        non_followers = []
        for user_id, username in following_cache.items():
            # Skip whitelisted users
            if username in unfollow_whitelist:
                continue
            
            # Check if not a follower
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
        
        # Ask for delay preference
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