# Mailchimp ETL Pipeline

This module extracts data from Mailchimp using the Mailchimp Marketing API v3.0, transforms it into structured formats, and exports it for email marketing analysis.

## 🎯 What This Pipeline Does

- **Extracts** mailing lists, campaigns, and subscriber data from Mailchimp
- **Transforms** API responses into clean, structured DataFrames with derived metrics
- **Loads** processed data into CSV, Excel, or JSON formats with summary dashboards
- **Handles** rate limiting, pagination, and timezone normalization
- **Provides** engagement analytics and geographic insights

## 📊 Available Data

### Mailing Lists Data

- **List Information**: Name, creation date, visibility settings
- **Member Statistics**: Total subscribers, unsubscribe counts
- **Performance Metrics**: Average open rates, click rates
- **Health Indicators**: Unsubscribe rates, list growth trends

### Campaign Data

- **Campaign Details**: Subject lines, send times, campaign types
- **Performance Metrics**: Open rates, click rates, unsubscribe rates
- **Engagement Analytics**: Unique opens/clicks, engagement rates
- **Delivery Statistics**: Emails sent, bounces, delivery rates

### Member/Subscriber Data

- **Demographics**: Email addresses, signup timestamps, member ratings
- **Geographic Data**: Country codes, timezones, IP addresses
- **Engagement History**: Opt-in dates, activity scores
- **Segmentation Data**: Tags, interests, custom fields

## 🛠️ Setup Requirements

### 1. Mailchimp API Key

- Log into your Mailchimp account
- Go to Account → Extras → API keys
- Generate a new API key
- Note your server prefix (e.g., us1, us2, eu1)

### 2. Environment Variables

```env
MAILCHIMP_API_KEY=your-api-key-here
MAILCHIMP_SERVER_PREFIX=us1
```

### 3. Required Permissions

Your API key needs access to:

- ✅ Read campaigns
- ✅ Read lists and members
- ✅ View reports

## 🚀 Usage Examples

### Basic Usage

```python
from mailchimp_etl_pipeline import MailchimpETL

# Initialize
mc_etl = MailchimpETL(
    api_key="your-api-key",
    server_prefix="us1"
)

# Run basic ETL (lists and campaigns only)
output_file = mc_etl.run_etl()
print(f"Data saved to: {output_file}")
```

### Include Member Data

```python
# Extract everything including member data
output_file = mc_etl.run_etl(
    include_members=True,
    output_format="excel"
)
```

### Filter by Date

```python
# Only campaigns since January 2024
output_file = mc_etl.run_etl(
    since_date="2024-01-01",
    output_format="csv"
)
```

### Process Specific Lists

```python
# Extract members from specific lists only
output_file = mc_etl.run_etl(
    include_members=True,
    specific_list_ids=["abc123", "def456"],
    output_format="excel"
)
```

### Step-by-Step ETL Process

```python
# Step 1: Extract lists
lists_data = mc_etl.extract_lists()
print(f"Found {len(lists_data)} mailing lists")

# Step 2: Extract campaigns
campaigns_data = mc_etl.extract_campaigns(since_date="2024-01-01")
print(f"Found {len(campaigns_data)} campaigns")

# Step 3: Transform data
lists_df = mc_etl.transform_data('lists', lists_data)
campaigns_df = mc_etl.transform_data('campaigns', campaigns_data)

# Step 4: Load data
dataframes = {'lists': lists_df, 'campaigns': campaigns_df}
filename = mc_etl.load_data(dataframes, output_format="excel")
```

## 📋 Output Data Schema

### Lists Data (CSV/Excel)

| Column            | Type     | Description                       |
| ----------------- | -------- | --------------------------------- |
| list_id           | string   | Unique Mailchimp list identifier  |
| list_name         | string   | Name of the mailing list          |
| member_count      | integer  | Total number of subscribers       |
| unsubscribe_count | integer  | Total unsubscribes                |
| open_rate         | float    | Average open rate (0-1)           |
| click_rate        | float    | Average click rate (0-1)          |
| date_created      | datetime | When list was created             |
| visibility        | string   | Public or private list            |
| unsubscribe_rate  | float    | Calculated unsubscribe percentage |
| extracted_at      | datetime | When data was extracted           |

### Campaigns Data (CSV/Excel)

| Column               | Type     | Description                     |
| -------------------- | -------- | ------------------------------- |
| campaign_id          | string   | Unique campaign identifier      |
| campaign_name        | string   | Campaign subject line           |
| list_id              | string   | Associated mailing list         |
| send_time            | datetime | When campaign was sent          |
| emails_sent          | integer  | Total emails sent               |
| opens                | integer  | Total opens (including repeats) |
| unique_opens         | integer  | Unique opens                    |
| open_rate            | float    | Open rate (0-1)                 |
| clicks               | integer  | Total clicks                    |
| unique_clicks        | integer  | Unique clicks                   |
| click_rate           | float    | Click rate (0-1)                |
| unsubscribes         | integer  | Unsubscribes from this campaign |
| bounces              | integer  | Hard + soft bounces             |
| engagement_rate      | float    | Calculated engagement rate      |
| performance_category | string   | Low/Medium/High/Excellent       |
| send_date            | date     | Date portion of send time       |
| send_hour            | integer  | Hour of day sent                |

### Members Data (CSV/Excel)

| Column            | Type     | Description                             |
| ----------------- | -------- | --------------------------------------- |
| member_id         | string   | Unique member identifier                |
| email             | string   | Email address                           |
| status            | string   | subscribed, unsubscribed, cleaned, etc. |
| list_id           | string   | Associated mailing list                 |
| timestamp_signup  | datetime | When member signed up                   |
| timestamp_opt     | datetime | When member confirmed opt-in            |
| country_code      | string   | Two-letter country code                 |
| country_name      | string   | Full country name                       |
| timezone          | string   | Member's timezone                       |
| ip_signup         | string   | IP address at signup                    |
| language          | string   | Preferred language                      |
| member_rating     | integer  | Mailchimp's engagement rating (1-5)     |
| days_since_signup | integer  | Days since initial signup               |

## ⚙️ Configuration Options

### Output Formats

```python
# CSV files (separate file per data type)
mc_etl.run_etl(output_format="csv")

# Excel with multiple sheets and dashboard
mc_etl.run_etl(output_format="excel")

# JSON format
mc_etl.run_etl(output_format="json")
```

### Member Data Options

```python
# Skip member data for faster processing
mc_etl.run_etl(include_members=False)

# Include member data (slower but comprehensive)
mc_etl.run_etl(include_members=True)

# Process only specific lists
mc_etl.run_etl(
    include_members=True,
    specific_list_ids=["list123", "list456"]
)
```

### Date Filtering

```python
# All campaigns
mc_etl.run_etl()

# Campaigns since specific date
mc_etl.run_etl(since_date="2024-01-01")

# Recent campaigns only
from datetime import datetime, timedelta
last_month = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
mc_etl.run_etl(since_date=last_month)
```

## 🔧 Advanced Features

### Custom Data Transformation

```python
class CustomMailchimpETL(MailchimpETL):
    def transform_data(self, data_type, raw_data):
        # Call parent transformation
        df = super().transform_data(data_type, raw_data)

        if data_type == 'campaigns':
            # Add custom campaign analysis
            df['is_high_performing'] = df['open_rate'] > 0.25
            df['engagement_score'] = (df['open_rate'] * 0.6) + (df['click_rate'] * 0.4)

        elif data_type == 'members':
            # Add custom member segmentation
            df['member_tenure'] = pd.cut(
                df['days_since_signup'],
                bins=[0, 30, 90, 365, float('inf')],
                labels=['New', 'Recent', 'Established', 'Veteran']
            )

        return df
```

### Rate Limiting Handling

```python
# The pipeline automatically handles Mailchimp's API limits:
# - 10 simultaneous connections
# - 500 requests per minute per API key

# For large lists, the pipeline includes:
# - Automatic delays between requests
# - Exponential backoff on rate limit errors
# - Progress tracking for long operations
```

### Error Recovery

```python
import logging

# Enable detailed logging
logging.basicConfig(level=logging.INFO)

try:
    # Long-running operation with progress tracking
    mc_etl = MailchimpETL(api_key, server_prefix)
    output_file = mc_etl.run_etl(
        include_members=True,
        output_format="excel"
    )
    print(f"ETL completed successfully: {output_file}")

except Exception as e:
    logging.error(f"ETL failed: {str(e)}")
    # The pipeline will log specific error details for debugging
```

### Batch Processing for Large Lists

```python
def process_large_lists():
    mc_etl = MailchimpETL(api_key, server_prefix)

    # Get all lists first
    lists_data = mc_etl.extract_lists()

    # Process members in batches
    for list_info in lists_data:
        list_id = list_info['list_id']
        list_name = list_info['list_name']

        print(f"Processing list: {list_name} ({list_info['member_count']} members)")

        # Extract members for this list only
        members_data = mc_etl.extract_members(list_id)

        # Transform and save
        members_df = mc_etl.transform_data('members', members_data)
        filename = f"output/members_{list_name.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.csv"
        members_df.to_csv(filename, index=False)

        print(f"Saved {len(members_df)} members to {filename}")
```

## 📊 Data Analysis Examples

### Load and Analyze Campaign Performance

```python
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Load campaign data
campaigns = pd.read_csv('output/mailchimp_data_campaigns_20250730_153325.csv')

# Basic campaign statistics
print(f"Total campaigns analyzed: {len(campaigns)}")
print(f"Average open rate: {campaigns['open_rate'].mean():.2%}")
print(f"Average click rate: {campaigns['click_rate'].mean():.2%}")

# Performance analysis
print("\nCampaign Performance Distribution:")
print(campaigns['performance_category'].value_counts())

# Top performing campaigns
top_campaigns = campaigns.nlargest(10, 'engagement_rate')[
    ['campaign_name', 'open_rate', 'click_rate', 'engagement_rate']
]
print("\nTop 10 Campaigns by Engagement:")
print(top_campaigns)

# Time-based analysis
campaigns['send_time'] = pd.to_datetime(campaigns['send_time'])
campaigns['month'] = campaigns['send_time'].dt.to_period('M')

monthly_performance = campaigns.groupby('month').agg({
    'open_rate': 'mean',
    'click_rate': 'mean',
    'emails_sent': 'sum'
}).round(4)

print("\nMonthly Performance Trends:")
print(monthly_performance)

# Visualization
plt.figure(figsize=(12, 8))

# Subplot 1: Open vs Click rates
plt.subplot(2, 2, 1)
plt.scatter(campaigns['open_rate'], campaigns['click_rate'], alpha=0.6)
plt.xlabel('Open Rate')
plt.ylabel('Click Rate')
plt.title('Campaign Performance: Open vs Click Rates')

# Subplot 2: Performance by send hour
plt.subplot(2, 2, 2)
hourly_performance = campaigns.groupby('send_hour')['open_rate'].mean()
plt.bar(hourly_performance.index, hourly_performance.values)
plt.xlabel('Hour of Day')
plt.ylabel('Average Open Rate')
plt.title('Performance by Send Time')

# Subplot 3: Monthly trends
plt.subplot(2, 2, 3)
monthly_performance['open_rate'].plot(kind='line', marker='o')
plt.title('Open Rate Trends Over Time')
plt.ylabel('Open Rate')

# Subplot 4: Engagement distribution
plt.subplot(2, 2, 4)
campaigns['engagement_rate'].hist(bins=20, alpha=0.7)
plt.xlabel('Engagement Rate')
plt.ylabel('Frequency')
plt.title('Engagement Rate Distribution')

plt.tight_layout()
plt.show()
```

### Analyze Subscriber Demographics

```python
# Load member data
members = pd.read_csv('output/mailchimp_data_members_20250730_153325.csv')

# Geographic analysis
print("Subscriber Distribution by Country:")
country_distribution = members['country_name'].value_counts().head(10)
print(country_distribution)

# Member tenure analysis
print("\nMember Tenure Distribution:")
tenure_stats = members.groupby('member_tenure').agg({
    'member_id': 'count',
    'member_rating': 'mean'
}).rename(columns={'member_id': 'count'})
print(tenure_stats)

# Engagement by country
country_engagement = members.groupby('country_name').agg({
    'member_rating': 'mean',
    'member_id': 'count'
}).sort_values('member_rating', ascending=False).head(10)

print("\nTop Countries by Member Engagement:")
print(country_engagement)

# Signup trends
members['timestamp_signup'] = pd.to_datetime(members['timestamp_signup'])
members['signup_month'] = members['timestamp_signup'].dt.to_period('M')

signup_trends = members.groupby('signup_month').size()
print("\nMonthly Signup Trends:")
print(signup_trends.tail(12))  # Last 12 months
```

### List Health Analysis

```python
# Load lists data
lists = pd.read_csv('output/mailchimp_data_lists_20250730_153325.csv')

# List performance metrics
print("Mailing List Health Report:")
print("=" * 50)

for _, list_row in lists.iterrows():
    list_name = list_row['list_name']
    member_count = list_row['member_count']
    open_rate = list_row['open_rate']
    unsubscribe_rate = list_row['unsubscribe_rate']

    print(f"\n📧 {list_name}")
    print(f"   Subscribers: {member_count:,}")
    print(f"   Open Rate: {open_rate:.2%}")
    print(f"   Unsubscribe Rate: {unsubscribe_rate:.2%}")

    # Health indicators
    if open_rate > 0.25:
        health = "🟢 Excellent"
    elif open_rate > 0.20:
        health = "🟡 Good"
    elif open_rate > 0.15:
        health = "🟠 Fair"
    else:
        health = "🔴 Needs Attention"

    print(f"   Health: {health}")

# Overall statistics
total_subscribers = lists['member_count'].sum()
avg_open_rate = lists['open_rate'].mean()
avg_unsubscribe_rate = lists['unsubscribe_rate'].mean()

print(f"\n📊 Overall Statistics:")
print(f"   Total Subscribers: {total_subscribers:,}")
print(f"   Average Open Rate: {avg_open_rate:.2%}")
print(f"   Average Unsubscribe Rate: {avg_unsubscribe_rate:.2%}")
```

### Export for Business Intelligence

```python
# Create executive summary
def create_executive_summary():
    # Load all data
    campaigns = pd.read_csv('output/mailchimp_data_campaigns_20250730_153325.csv')
    lists = pd.read_csv('output/mailchimp_data_lists_20250730_153325.csv')

    # Key metrics
    summary = {
        'total_lists': len(lists),
        'total_subscribers': lists['member_count'].sum(),
        'total_campaigns': len(campaigns),
        'avg_open_rate': campaigns['open_rate'].mean(),
        'avg_click_rate': campaigns['click_rate'].mean(),
        'best_performing_campaign': campaigns.loc[campaigns['open_rate'].idxmax(), 'campaign_name'],
        'total_emails_sent': campaigns['emails_sent'].sum(),
        'total_unsubscribes': campaigns['unsubscribes'].sum()
    }

    # Save summary
    summary_df = pd.DataFrame([summary])
    summary_df.to_csv('output/mailchimp_executive_summary.csv', index=False)

    return summary

# Generate and print summary
summary = create_executive_summary()
print("Executive Summary Generated:")
for key, value in summary.items():
    if isinstance(value, float) and 'rate' in key:
        print(f"{key.replace('_', ' ').title()}: {value:.2%}")
    elif isinstance(value, (int, float)) and 'total' in key:
        print(f"{key.replace('_', ' ').title()}: {value:,}")
    else:
        print(f"{key.replace('_', ' ').title()}: {value}")
```

## 🚨 Troubleshooting

### Common Errors and Solutions

1. **"Invalid API Key"**

   ```
   Error: 401 Your API key may be invalid
   ```

   **Solutions**:

   - Verify API key is correct and active
   - Check that API key hasn't expired
   - Ensure server prefix matches your account

2. **"List not found"**

   ```
   Error: 404 The requested resource could not be found
   ```

   **Solutions**:

   - Verify list IDs are correct
   - Check that lists haven't been deleted
   - Ensure your API key has access to the lists

3. **"Rate limit exceeded"**

   ```
   Error: 429 Too Many Requests
   ```

   **Solutions**:

   - The pipeline handles this automatically with delays
   - For large operations, consider running during off-peak hours
   - Contact Mailchimp support if limits are consistently hit

4. **"No campaigns found"**
   ```
   Warning: Extracted 0 campaigns
   ```
   **Solutions**:
   - Check your date filters (campaigns might be outside date range)
   - Verify campaigns exist and are in "sent" status
   - Ensure API key has permission to access campaign reports

### Debug Mode

```python
import logging

# Enable comprehensive logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Run with detailed output
mc_etl = MailchimpETL(api_key, server_prefix)
output_file = mc_etl.run_etl(include_members=True)
```

### Validate Setup

```python
def test_mailchimp_setup():
    """Test Mailchimp API connection and permissions"""
    try:
        mc_etl = MailchimpETL(api_key, server_prefix)

        # Test basic API access
        lists_data = mc_etl.extract_lists()
        print(f"✅ API connection successful: Found {len(lists_data)} lists")

        # Test campaign access
        campaigns_data = mc_etl.extract_campaigns()
        print(f"✅ Campaign access successful: Found {len(campaigns_data)} campaigns")

        # Test member access if lists exist
        if lists_data:
            first_list = lists_data[0]['list_id']
            members_data = mc_etl.extract_members(first_list)
            print(f"✅ Member access successful: Found {len(members_data)} members in first list")

        return True

    except Exception as e:
        print(f"❌ Setup test failed: {e}")
        return False

# Run test
test_mailchimp_setup()
```

### Performance Optimization

```python
# For large accounts, optimize performance:

# 1. Process lists selectively
priority_lists = ["list_id_1", "list_id_2"]  # Your most important lists
mc_etl.run_etl(
    include_members=True,
    specific_list_ids=priority_lists
)

# 2. Use date filters for campaigns
recent_campaigns_only = mc_etl.run_etl(
    since_date="2024-06-01",  # Last 2 months only
    include_members=False
)

# 3. Extract in stages for very large lists
def extract_in_stages():
    mc_etl = MailchimpETL(api_key, server_prefix)

    # Stage 1: Lists and campaigns only
    print("Stage 1: Extracting lists and campaigns...")
    mc_etl.run_etl(include_members=False, output_format="csv")

    # Stage 2: Members from top 3 lists only
    print("Stage 2: Extracting members from priority lists...")
    lists_data = mc_etl.extract_lists()
    top_lists = sorted(lists_data, key=lambda x: x['member_count'], reverse=True)[:3]
    top_list_ids = [lst['list_id'] for lst in top_lists]

    mc_etl.run_etl(
        include_members=True,
        specific_list_ids=top_list_ids,
        output_format="excel"
    )

# extract_in_stages()
```

## 📚 Resources

- [Mailchimp Marketing API Documentation](https://mailchimp.com/developer/marketing/api/)
- [API Rate Limits and Guidelines](https://mailchimp.com/developer/marketing/docs/fundamentals/#api-limits)
- [Mailchimp Account Settings](https://admin.mailchimp.com/account/api/)
- [Email Marketing Best Practices](https://mailchimp.com/resources/)

## 🔄 Updates and Maintenance

### Regular Tasks

- **Monitor API usage** and stay within rate limits
- **Archive old output files** to save disk space
- **Update API keys** before expiration
- **Review subscriber list health** monthly

### API Version Compatibility

- **Mailchimp Marketing API**: v3.0 (current)
- **Python**: 3.7+ required
- **Dependencies**: See `requirements.txt` for current versions

### Data Retention

```python
# Clean up old output files (optional)
import os
import glob
from datetime import datetime, timedelta

def cleanup_old_files(days_to_keep=30):
    """Remove output files older than specified days"""
    cutoff_date = datetime.now() - timedelta(days=days_to_keep)

    for file_path in glob.glob('output/mailchimp_data_*.csv'):
        file_time = datetime.fromtimestamp(os.path.getctime(file_path))
        if file_time < cutoff_date:
            os.remove(file_path)
            print(f"Removed old file: {file_path}")

# Run cleanup (uncomment to use)
# cleanup_old_files(30)
```

## 🎯 Next Steps

After extracting your Mailchimp data, consider:

1. **Automated Reporting**: Set up scheduled runs to generate regular reports
2. **Data Visualization**: Create dashboards with tools like Tableau, Power BI, or Python/matplotlib
3. **Predictive Analytics**: Analyze patterns to predict subscriber behavior
4. **A/B Testing**: Use historical data to optimize future campaigns
5. **Integration**: Combine with Google Analytics data for comprehensive marketing insights

---

**Ready to analyze your email marketing performance? Run `python3 main.py` to extract your Mailchimp data!**
