# Instagram Management Toolkit

## Overview

A comprehensive Python-based Instagram management tool that provides multiple functionalities for social media management and analysis. This toolkit allows users to efficiently manage their Instagram account with features like follower discovery, mass following, unfollowing non-followers, and detailed relationship insights.

## 🌟 Features

### 1. Follower Fetcher
- Fetch followers or following list for any Instagram user
- Option to select a random user from your following list
- Detailed relationship insights
- Save results to JSON for further analysis

### 2. Mass Follower
- Follow users from a pre-generated JSON file
- Intelligent following with rate limiting
- Customizable follow strategy

### 3. User Discovery
- Discover potential followers from your existing network
- Configurable target number of users
- Save discovered users to JSON

### 4. Unfollow Non-Followers
- Identify users who don't follow you back
- Bulk unfollow with customizable delay
- Logging of unfollow actions

## 🔒 Security Features
- Secure password input
- Random delays to avoid Instagram rate limits
- Caching mechanisms to reduce API calls

## 📦 Requirements
- Python 3.7+
- `instagrapi` library
- Internet connection

## 🛠️ Installation

1. Clone the repository
```bash
git clone https://github.com/yourusername/instagram-management-toolkit.git
cd instagram-management-toolkit
```

2. Install required dependencies
```bash
pip install instagrapi
```

## 🚀 Usage

Run the main script:
```bash
python instagram_manager.py
```

Follow the on-screen prompts to:
- Choose your desired action
- Input Instagram credentials
- Configure specific operations

## ⚠️ Disclaimer and Important Warnings

### Account Safety
**CRITICAL NOTICE:** Using automated tools like this can significantly risk your Instagram account:

- **High Risk of Account Restrictions:** Instagram actively monitors and can permanently ban or shadowban accounts using automation tools.
- **Personal Warning:** From my experience, attempting to use longer delays or more complex timing mechanisms does NOT reduce the risk. In fact, it may increase the likelihood of your account being flagged. I used this on/off for about a week and never got truly flagged until I started stretching my delay-times. I believe the method is to have it function as humanly as possible, which is how it's configured at the moment. Use with caution

### Potential Consequences
- Temporary action blocks
- Permanent account suspension
- Removal of follow/unfollow privileges
- Reduced account visibility

### Best Practices
- Use this tool sparingly, if at all
- Never run mass actions on your primary account
- Be prepared for potential account restrictions
- Consider the risks before each action

**ABSOLUTE CAUTION:** Instagram's terms of service explicitly prohibit the use of unauthorized automation tools. Use of this script is entirely at your own risk.

## 🔧 Troubleshooting
- Ensure you have the latest version of `instagrapi`
- Check your internet connection
- Verify Instagram credentials
- Respect Instagram's rate limits

## 🤝 Contributing
Contributions, issues, and feature requests are welcome!

**Note:** This project is not affiliated with or endorsed by Instagram. Use at your own risk and with extreme caution.