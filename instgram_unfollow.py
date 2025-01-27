from instagrapi import Client
import time
import json
from datetime import datetime
import random

class InstagramUnfollower:
    def __init__(self):
        self.client = Client()
        self.user_id = None
        
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
            
    def get_following_followers_lists(self):
        """Get lists of followers and following with pagination and rate limiting"""
        following = {}
        followers = {}
        
        try:
            print("Fetching users you follow...")
            following_users = self.client.user_following_v1(self.user_id, amount=0)
            for user in following_users:
                following[user.pk] = user.username
                time.sleep(random.uniform(0.1, 0.3))
            
            print("Fetching your followers...")
            follower_users = self.client.user_followers_v1(self.user_id, amount=0)
            for user in follower_users:
                followers[user.pk] = user.username
                time.sleep(random.uniform(0.1, 0.3))
                
            print(f"Found {len(following)} following and {len(followers)} followers")
            return following, followers
            
        except Exception as e:
            print(f"Error fetching lists: {str(e)}")
            print("Try these troubleshooting steps:")
            print("1. Wait a few minutes before trying again")
            print("2. Use a VPN or different network")
            print("3. Make sure your account isn't temporarily restricted")
            return None, None
            
    def find_non_followers(self, following, followers):
        """Find users you follow who don't follow you back"""
        non_followers = []
        for user_id, username in following.items():
            if user_id not in followers:
                non_followers.append({
                    'user_id': user_id,
                    'username': username
                })
        return non_followers
        
    def unfollow_users(self, users_to_unfollow, delay_range=(0.1, 0.3)):
        """Unfollow specified users with random delay to avoid detection"""
        success_count = 0
        failed_count = 0
        
        for user in users_to_unfollow:
            try:
                print(f"Unfollowing {user['username']}...")
                self.client.user_unfollow(user['user_id'])
                success_count += 1
                
                delay = random.uniform(delay_range[0], delay_range[1])
                print(f"Waiting {delay:.1f} seconds...")
                time.sleep(delay)
                
            except Exception as e:
                print(f"Failed to unfollow {user['username']}: {str(e)}")
                failed_count += 1
                
                time.sleep(60)
                
        return success_count, failed_count
        
    def save_log(self, unfollowed_users):
        """Save unfollow operation details to a log file"""
        log_data = {
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'unfollowed_users': unfollowed_users
        }
        
        with open('unfollow_log.json', 'a') as f:
            json.dump(log_data, f)
            f.write('\n')

def main():
    # Initialize the unfollower
    unfollower = InstagramUnfollower()
    
    # Get credentials
    username = input("Enter your Instagram username: ")
    password = input("Enter your Instagram password: ")
    
    # Login
    if not unfollower.login(username, password):
        return
    
    # Get following/followers with retry mechanism
    max_retries = 3
    retry_count = 0
    
    while retry_count < max_retries:
        following, followers = unfollower.get_following_followers_lists()
        if following and followers:
            break
        retry_count += 1
        if retry_count < max_retries:
            wait_time = 60 * retry_count  # Increase wait time with each retry
            print(f"\nRetrying in {wait_time} seconds... (Attempt {retry_count + 1}/{max_retries})")
            time.sleep(wait_time)
    
    if not following or not followers:
        print("Failed to fetch user lists after multiple attempts. Please try again later.")
        return
        
    # Find non-followers
    non_followers = unfollower.find_non_followers(following, followers)
    
    # Show summary
    print(f"\nFound {len(non_followers)} users who don't follow you back:")
    for user in non_followers:
        print(f"- {user['username']}")
    
    # Confirm before unfollowing
    if input("\nWould you like to unfollow these users? (y/n): ").lower() != 'y':
        print("Operation cancelled")
        return
    
    # Ask for delay preference
    use_safe_mode = input("Use safer, longer delays between unfollows? (recommended) (y/n): ").lower() == 'y'
    delay_range = (45, 60) if use_safe_mode else (30, 45)
    
    # Perform unfollow
    success, failed = unfollower.unfollow_users(non_followers, delay_range)
    
    # Save results to log
    unfollower.save_log(non_followers)
    
    # Show results
    print(f"\nOperation complete:")
    print(f"Successfully unfollowed: {success}")
    print(f"Failed to unfollow: {failed}")

if __name__ == "__main__":
    main()