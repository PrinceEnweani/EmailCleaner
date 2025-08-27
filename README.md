Python Script that helps user's delete emails in batch
Email Cleaner - Setup Guide
📋 Prerequisites
Python 3.6 or higher

A Google account

Basic command line knowledge

🚀 Quick Setup
1. Install Required Packages
bash
pip install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib
2. Enable Gmail API & Create Credentials
Step-by-Step:
Go to Google Cloud Console

Create a new project or select existing one

Name it (e.g., "Gmail Cleaner")

Enable Gmail API

Navigate to "APIs & Services" > "Library"

Search for "Gmail API"

Click "Enable"

Configure OAuth Consent Screen

Go to "APIs & Services" > "OAuth consent screen"

Choose "External" user type

Fill in:

App name: "Gmail Cleaner"

User support email: Your email

Developer contact email: Your email

Click "Save and Continue"

Add Scopes

Click "Add or Remove Scopes"

Search for and add: https://mail.google.com/

Click "Update" > "Save and Continue"

Add Test Users

Under "Test users", click "Add users"

Add your email address

Click "Save and Continue"

Create Credentials

Go to "APIs & Services" > "Credentials"

Click "Create Credentials" > "OAuth 2.0 Client ID"

Choose "Desktop application"

Name: "Gmail Cleaner Desktop"

Click "Create"

Download Credentials

Click the download icon (📎) next to your new OAuth client

Save the file as credentials.json in the same folder as the Python script

3. First Run Authentication
Run the script:

bash
python gmail_cleaner.py
Complete OAuth Flow:

A browser window will open

You may see "App not verified" warning → Click "Advanced" → "Go to [App Name] (unsafe)"

Sign in with your Google account

Review permissions and click "Allow"

The app will create a token.pickle file for future authentication

🔧 Troubleshooting
Common Issues:
"App not verified" warning

This is normal for testing apps

Click "Advanced" → "Go to [App Name] (unsafe)"

"Insufficient authentication scopes"

Make sure you added https://mail.google.com/ scope in OAuth consent screen

Delete token.pickle and re-authenticate

Credentials file not found

Ensure credentials.json is in the same folder as the script

Check the file name is exactly credentials.json

Authentication errors

Delete token.pickle and run the script again

Make sure your email is added as a test user

⚠️ Important Notes
The app is in testing mode - it only works for email addresses you explicitly add as test users

You don't need to publish the app for personal use

Deleted emails are permanent - use with caution

Large deletions may take time - be patient for thousands of emails

📊 Usage Tips
Start with a small test (limit to 10 emails) before large deletions

The script shows progress for batch operations

You can interrupt with Ctrl+C if needed

🔒 Security
Your credentials are stored locally

The app only has access to what you authorize

You can revoke access anytime at Google Account Security Settings
