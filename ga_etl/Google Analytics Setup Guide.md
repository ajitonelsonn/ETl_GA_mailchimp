# Google Analytics Setup Guide

This guide shows you how to get the Google Analytics Property ID and Service Account credentials needed for the ETL pipeline.

## Part 1: Get Your Google Analytics Property ID

### Step 1: Access Google Analytics

1. Go to [https://analytics.google.com](https://analytics.google.com)
2. Sign in with your Google account
3. Select the GA4 property you want to use

### Step 2: Find Your Property ID

1. Click the **Admin** (gear icon) in the bottom left corner
2. In the **Property** column (middle), click **Property Settings**
3. Look for the **Property ID** field at the top right - it will be a number like `123456789`
4. Click the copy icon next to it to copy the ID
5. **Important**: The Property ID should be just numbers, NOT starting with "G-" (that's the Measurement ID)

### Step 3: Format for .env File

Your Property ID should be formatted as:

```
GA_PROPERTY_ID=properties/123456789
```

**Note**: Add `properties/` before your numeric ID.

---

## Part 2: Create Service Account Credentials

### Step 1: Create Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click **Select a project** → **New Project**
3. Enter a project name (e.g., "UN Analytics ETL")
4. Click **Create**

### Step 2: Enable Google Analytics Data API

1. In the Google Cloud Console, go to **APIs & Services** → **Library**
2. Search for "Google Analytics Data API"
3. Click on it and press **Enable**

### Step 3: Create Service Account

1. Go to **IAM & Admin** → **Service Accounts**
2. Click **Create Service Account**
3. Fill in:
   - **Service account name**: `analytics-etl-service`
   - **Service account ID**: (auto-generated)
   - **Description**: "Service account for UN analytics ETL pipeline"
4. Click **Create and Continue**
5. Skip role assignment for now (click **Continue**)
6. Click **Done**

### Step 4: Generate Credentials Key

1. In the Service Accounts list, click on your newly created service account
2. Go to the **Keys** tab
3. Click **Add Key** → **Create new key**
4. Select **JSON** format
5. Click **Create**
6. The JSON file will download automatically - **save this file securely!**
7. Rename the file to something like `ga-service-account-key.json`

### Step 5: Copy Service Account Email

From the service account details page, copy the email address (it looks like `analytics-etl-service@your-project.iam.gserviceaccount.com`)

---

## Part 3: Grant Service Account Access to Google Analytics

### Step 1: Add Service Account to GA4 Property

1. Go back to [Google Analytics](https://analytics.google.com)
2. Click **Admin** (gear icon)
3. In the **Property** column, click **Property Access Management**
4. Click the blue **+** button → **Add users**
5. Paste the service account email address
6. Set role to **Viewer** (sufficient for reading data)
7. Uncheck "Notify new users by email" (service accounts don't need emails)
8. Click **Add**

---

## Part 4: Update Your .env File

Create or update your `.env` file with:

```env
# Google Analytics Configuration
GA_PROPERTY_ID=properties/123456789
GA_CREDENTIALS_PATH=./credentials/ga-service-account-key.json

# Mailchimp Configuration (if you have them)
MAILCHIMP_API_KEY=your-mailchimp-api-key-here
MAILCHIMP_SERVER_PREFIX=us1
```

---

## Part 5: File Structure

Organize your files like this:

```
your-project/
├── main.py
├── .env
├── credentials/
│   └── ga-service-account-key.json
└── output/
    └── (generated files will go here)
```

---

## Part 6: Test Your Setup

Run this test script to verify everything works:

```python
import os
from dotenv import load_dotenv
from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.oauth2.service_account import Credentials

load_dotenv()

# Test credentials loading
property_id = os.getenv('GA_PROPERTY_ID')
credentials_path = os.getenv('GA_CREDENTIALS_PATH')

print(f"Property ID: {property_id}")
print(f"Credentials Path: {credentials_path}")

# Test authentication
try:
    credentials = Credentials.from_service_account_file(
        credentials_path,
        scopes=["https://www.googleapis.com/auth/analytics.readonly"]
    )
    client = BetaAnalyticsDataClient(credentials=credentials)
    print("✅ Authentication successful!")
except Exception as e:
    print(f"❌ Authentication failed: {e}")
```

---

## Troubleshooting

### Common Issues:

1. **"Property not found" error**

   - Make sure you're using the numeric Property ID, not the Measurement ID
   - Ensure you added `properties/` prefix

2. **"Permission denied" error**

   - Check that you added the service account email to GA4 Property Access Management
   - Verify the service account has at least "Viewer" role

3. **"API not enabled" error**

   - Make sure you enabled the Google Analytics Data API in Google Cloud Console

4. **File not found error**
   - Check the path to your JSON credentials file
   - Make sure the file wasn't corrupted during download

### Security Best Practices:

- ✅ Keep your JSON credentials file secure and never commit to version control
- ✅ Add `credentials/` and `.env` to your `.gitignore` file
- ✅ Use environment variables for all sensitive data
- ✅ Regularly rotate service account keys if needed

---

## Need Help?

If you encounter issues:

1. Double-check each step above
2. Verify your Google Analytics property is GA4 (not Universal Analytics)
3. Ensure you have the necessary permissions in both Google Cloud and Google Analytics
4. Check the Google Analytics Data API documentation for updates
