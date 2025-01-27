from instagrapi import Client
import time
import json
from datetime import datetime
import random

class InstagramFollowerFetcher:
    def __init__(self):
        self.client = Client()
        self.user_id = None
        self.my_following = set()
        self.my_followers = set()
        self.my_following_usernames = {}
        
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
            
            # Cache our following/followers
            print("Fetching your following/followers lists...")
            self._cache_relationships()
            
            print("Successfully logged in!")
            return True
        except Exception as e:
            print(f"Login failed: {str(e)}")
            return False
            
    def check_relationship(self, user_id):
        """Check if there's a following relationship with the logged-in user"""
        return {
            'following': user_id in self.my_following,
            'followed_by': user_id in self.my_followers
        }
            
    def get_user_id(self, username):
        """Get user ID from username"""
        try:
            user_info = self.client.user_info_by_username(username)
            return user_info.pk
        except Exception as e:
            print(f"Error getting user ID: {str(e)}")
            return None

    def get_user_followers(self, user_id, option):
        """Get list of followers for a specific user"""
        followers = {}
        
        try:
            if option == 2:
                print("Fetching user's following...")
                follower_users = self.client.user_following_v1(user_id, amount=0)
            else:
                print("Fetching user's followers...")
                follower_users = self.client.user_followers_v1(user_id, amount=0)
            
            for user in follower_users:
                # Check relationship status
                relationship = self.check_relationship(user.pk)
                
                followers[user.pk] = {
                    'username': user.username,
                    'full_name': user.full_name,
                    'is_private': user.is_private,
                    'you_follow_them': relationship['following'],
                    'they_follow_you': relationship['followed_by']
                }
                
                print(f"{user.full_name}", end="")
                if relationship['followed_by']:
                    print(" | follows you", end="")
                if relationship['following']:
                    print(" | following", end="")
                print("\n")
                
                time.sleep(random.uniform(0.5, 1))  # Random delay between requests
                
            print(f"\nFound {len(followers)} followers")
            
            # Print relationship summary
            you_follow = sum(1 for f in followers.values() if f['you_follow_them'])
            follow_you = sum(1 for f in followers.values() if f['they_follow_you'])
            mutual = sum(1 for f in followers.values() if f['you_follow_them'] and f['they_follow_you'])
            
            print(f"\nRelationship Summary:")
            print(f"You follow: {you_follow} of these users")
            print(f"Following you: {follow_you} of these users")
            print(f"Mutual followers: {mutual} users")
            
            return followers
            
        except Exception as e:
            print(f"Error fetching followers: {str(e)}")
            print("Try these troubleshooting steps:")
            print("1. Wait a few minutes before trying again")
            print("2. Use a VPN or different network")
            print("3. Make sure your account isn't temporarily restricted")
            return None
            
    def save_followers_to_file(self, username, followers):
        """Save followers list to a JSON file"""
        output_data = {
            'target_user': username,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'follower_count': len(followers),
            'relationship_summary': {
                'you_follow': sum(1 for f in followers.values() if f['you_follow_them']),
                'follow_you': sum(1 for f in followers.values() if f['they_follow_you']),
                'mutual_followers': sum(1 for f in followers.values() if f['you_follow_them'] and f['they_follow_you'])
            },
            'followers': followers
        }
        
        filename = f'{username}_followers.json'
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=4, ensure_ascii=False)
            
        print(f"\nFollowers list saved to {filename}")

    def _cache_relationships(self):
        """Cache the logged-in user's following and followers"""
        try:
            # Get following
            print("Caching your following list...")
            following = self.client.user_following_v1(self.user_id, amount=0)
            self.my_following = set()

            following_list = list(following)
            total = len(following_list)

            for i, user in enumerate(following, 1):
                self.my_following.add(user.pk)
                self.my_following_usernames[user.pk] = {
                    'username': user.username,
                    'full_name': user.full_name
                }
                print(f"\rProcessing: {i}/{total} users", end='', flush=True)
                time.sleep(random.uniform(0.1, 0.3))
            print("\n")

            # Get followers
            print("Caching your followers list...")
            followers = self.client.user_followers_v1(self.user_id, amount=0)
            self.my_followers = set()

            follower_list = list(followers)
            total = len(follower_list)

            for i, user in enumerate(followers, 1):
                self.my_followers.add(user.pk)
                print(f"\rProcessing: {i}/{total} users", end='', flush=True)
                time.sleep(random.uniform(0.1, 0.3))
            print("\n")
                
        except Exception as e:
            print(f"Error caching relationships: {str(e)}")
            
    def get_random_following(self):
        """Get a random user from following list"""
        if not self.my_following:
            print("No following found!")
            return None
            
        random_id = random.choice(list(self.my_following))
        user_data = self.my_following_usernames[random_id]
        return user_data['username']

def main():
    # Initialize the fetcher
    fetcher = InstagramFollowerFetcher()
    
    # Get credentials
    username = input("Enter your Instagram username: ")
    password = input("Enter your Instagram password: ")
    
    # Login
    if not fetcher.login(username, password):
        return
    
    while True:
        # Get target user
        target_username = input("\nEnter the username whose followers you want to fetch (or 'random' for random pick): ")
        
        if target_username.lower() == 'random':
            while True:
                random_user = fetcher.get_random_following()
                if not random_user:
                    return
                    
                print(f"\nRandom pick: {random_user}")
                confirm = input("Would you like to fetch followers for this user? (y/n): ")
                
                if confirm.lower() == 'y':
                    target_username = random_user
                    break
                print("\nRolling again...")
        
        # Get user ID
        target_user_id = fetcher.get_user_id(target_username)
        if target_user_id:
            break
        print("Could not find user. Please check the username and try again.")
    
    # Get followers with retry mechanism
    max_retries = 3
    retry_count = 0
    followers = None

    option = int(input("(1) followers (2) following for selected user (default is followers)"))
    
    while retry_count < max_retries:
        followers = fetcher.get_user_followers(target_user_id, option)
        if followers:
            break
        retry_count += 1
        if retry_count < max_retries:
            wait_time = 60 * retry_count  # Increase wait time with each retry
            print(f"\nRetrying in {wait_time} seconds... (Attempt {retry_count + 1}/{max_retries})")
            time.sleep(wait_time)
    
    if not followers:
        print("Failed to fetch followers after multiple attempts. Please try again later.")
        return
    
    # Save to file
    fetcher.save_followers_to_file(target_username, followers)

if __name__ == "__main__":
    main()