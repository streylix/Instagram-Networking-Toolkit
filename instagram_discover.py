from instagrapi import Client
import time
import json
from datetime import datetime
import random
import os

class InstagramFollowerDiscovery:
    def __init__(self):
        self.client = Client()
        self.user_id = None
        self.my_followers = set()
        self.my_following = set()
        self.searched_users = set()
        self.my_following_usernames = {}
        self.potential_follows = {}
        self.search_history = []
        self.target_users = 5000
        self.load_searched_users()
    
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
             
    def load_searched_users(self):
        """Load previously searched users from file"""
        try:
            if os.path.exists('searched_users.json'):
                with open('searched_users.json', 'r') as f:
                    data = json.load(f)
                    self.searched_users = set(data['searched_users'])
                    print(f"Loaded {len(self.searched_users)} previously searched users")
        except Exception as e:
            print(f"Error loading searched users: {str(e)}")
            self.searched_users = set()

    def save_searched_users(self):
        """Save searched users to file"""
        try:
            data = {
                'searched_users': list(self.searched_users)
            }
            with open('searched_users.json', 'w') as f:
                json.dump(data, f)
            print(f"Saved {len(self.searched_users)} searched users")
        except Exception as e:
            print(f"Error saving searched users: {str(e)}")
        
    def login(self, username, password):
        """Login to Instagram account with additional configuration"""
        try:
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
            
            self.client.set_user_agent("Instagram 203.0.0.29.118 Android (29/10.0; 640dpi; 1440x2560; Samsung; SM-G973F; beyond1; qcom; en_US; 314665256)")
            
            self.client.login(username, password)
            self.user_id = self.client.user_id
            print("Successfully logged in!")
            
            # Cache our followers
            self._cache_relationships()
            return True
        except Exception as e:
            print(f"Login failed: {str(e)}")
            return False

    def get_random_follower(self):
        """Get a random follower that hasn't been searched yet"""
        available_followers = self.my_followers - self.searched_users
        if not available_followers:
            return None
        return random.choice(list(available_followers))

    def check_relationship(self, user_id):
        """Check if there's a following relationship with the logged-in user"""
        return {
        'following': user_id in self.my_following,
        'followed_by': user_id in self.my_followers
    }

    def process_user_followers(self, user_id, parent_username):
        """Get and process followers for a specific user"""
        try:
            user_info = self.client.user_info(user_id)
            print(f"\nProcessing followers for: {user_info.username}")
            
            followers = self.client.user_followers_v1(user_id, amount=0)
            followers_list = list(followers)
            total = len(followers_list)
            total_processed = 0
            
            for follower in followers:
                relationship = self.check_relationship(follower.pk)

                if follower.pk not in self.potential_follows and follower.pk != self.user_id:
                    self.potential_follows[follower.pk] = {
                        'username': follower.username,
                        'full_name': follower.full_name,
                        'is_private': follower.is_private,
                        'you_follow_them': relationship['following'],
                        'they_follow_you': relationship['followed_by'],
                        'parent': parent_username
                    }
                    print(f"\rProcessed {total_processed}/{total} new potential follows", end='', flush=True)
                    total_processed += 1
                    
                time.sleep(random.uniform(0.1, 0.3))
                
            print(f"\nCompleted processing {user_info.username}'s followers")
            return user_info.username
            
        except Exception as e:
            error_msg = str(e)
            if "protect our community" in error_msg:
                print("\nInstagram rate limit reached. Saving and ending...")
                self.save_results()
                exit()
            else:
                print(f"\nError processing followers: {error_msg}")
                self.save_results()
                exit()

    def discover_follows(self):
        """Main discovery process"""
        try:
            print(f"Starting follower discovery. Target: {self.target_users} users")
            
            while len(self.potential_follows) < self.target_users:
                try:
                    # Get random follower
                    random_follower_id = self.get_random_follower()
                    if not random_follower_id:
                        print("No more followers to search!")
                        break
                    
                    random_id = self.client.user_info(random_follower_id)
                    random_follower_name = random_id.username
                    print(f"----=====Selected \"{random_follower_name}\"=====----")

                    # Process their followers
                    processed_username = self.process_user_followers(random_follower_id, 
                        random_follower_name)
                    
                    if processed_username:
                        self.search_history.append({
                            'username': processed_username,
                        })
                    
                    # Mark as searched
                    self.searched_users.add(random_follower_id)
                    self.save_searched_users()  # Save after each new user
                    
                    print(f"\nTotal potential follows found: {len(self.potential_follows)}")
                    
                    # Add delay between users
                    delay = random.uniform(0.1, 0.3)
                    print(f"Waiting {delay:.1f} seconds...")
                    time.sleep(delay)
                    
                except Exception as e:
                    error_msg = str(e)
                    if "protect our community" in error_msg:
                        print("\nInstagram rate limit reached. Saving and ending...")
                        break
                    else:
                        print(f"\nError during discovery: {error_msg}")
                        print("Skipping this user and continuing...")
                        continue
            
        except Exception as e:
            print(f"Fatal error during discovery: {str(e)}")
        
        finally:
            print("\nSaving final results...")
            self.save_results()

    def save_results(self):
        """Save results to JSON file"""
        output_data = {
            'total_users_found': len(self.potential_follows),
            'searched_users': self.search_history,
            'followers': self.potential_follows
        }
        
        filename = f'discovery_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=4, ensure_ascii=False)
            
        print(f"\nResults saved to {filename}")

def main():
    discovery = InstagramFollowerDiscovery()

    # Get credentials once
    username = input("Enter your Instagram username: ")
    password = input("Enter your Instagram password: ")
    
    # Login
    if not discovery.login(username, password):
        return
    
    while True:
        try:
            target = input("Enter target number of users to find (default 5000): ").strip()
            if target == "":
                discovery.target_users = 5000
                break
            target = int(target)
            if target > 0:
                discovery.target_users = target
                break
            else:
                print("Please enter a positive number")
        except ValueError:
            print("Please enter a valid number")
    
    discovery.discover_follows()

if __name__ == "__main__":
    main()