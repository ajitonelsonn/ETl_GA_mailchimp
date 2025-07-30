# Google Analytics 4 ETL Pipeline

This module extracts data from Google Analytics 4 properties using the Google Analytics Data API v1, transforms it into structured formats, and exports it for analysis.

## 🎯 What This Pipeline Does

- **Extracts** website analytics data from your GA4 property
- **Transforms** raw API responses into clean, structured DataFrames
- **Loads** processed data into CSV, Excel, or JSON formats
- **Handles** timezone conversions, data type casting, and error management
- **Provides** summary analytics for quick insights

## 📊 Available Data

### Default Dimensions

- **country**: User's country
- **city**: User's city
- **date**: Date of the data
- **pagePath**: Page URL path
- **deviceCategory**: Device type (desktop, mobile, tablet)

### Default Metrics

- **sessions**: Number of sessions
- **totalUsers**: Total number of users
- **screenPageViews**: Page views (GA4 terminology)
- **userEngagementDuration**: Time users spent engaged with content

### Additional Available Dimensions

You can customize with other GA4 dimensions:

- `source`, `medium`, `campaign` (traffic source data)
- `browser`, `operatingSystem` (technology data)
- `ageGroup`, `gender` (demographic data)
- `eventName`, `eventAction` (event tracking)
- `hostname`, `landingPage` (page data)

### Additional Available Metrics

Customize with other GA4 metrics:

- `newUsers`, `activeUsers` (user metrics)
- `bounceRate`, `engagementRate` (engagement metrics)
- `conversions`, `keyEvents` (conversion tracking)
- `eventCount`, `eventValue` (event metrics)

## 🛠️ Setup Requirements

### 1. Google Cloud Project

- Create a project in [Google Cloud Console](https://console.cloud.google.com/)
- Enable the Google Analytics Data API

### 2. Service Account

- Create a service account with Analytics API access
- Download the JSON credentials file
- Store it securely in your `credentials/` folder

### 3. GA4 Property Access

- Add the service account email to your GA4 property
- Grant "Viewer" role (minimum required)

### 4. Environment Variables

```env
GA_PROPERTY_ID=properties/123456789
GA_CREDENTIALS_PATH=./credentials/ga-service-account-key.json
```

## 🚀 Usage Examples

### Basic Usage

```python
from ga_etl_pipeline import GoogleAnalyticsETL

# Initialize
ga_etl = GoogleAnalyticsETL(
    property_id="properties/123456789",
    credentials_path="./credentials/ga-service-account-key.json"
)

# Run ETL for last 30 days
output_file = ga_etl.run_etl()
print(f"Data saved to: {output_file}")
```

### Custom Date Range

```python
# Extract data for specific date range
output_file = ga_etl.run_etl(
    start_date="2024-01-01",
    end_date="2024-03-31",
    output_format="excel"
)
```

### Custom Dimensions and Metrics

```python
# Extract with custom dimensions and metrics
response = ga_etl.extract_data(
    start_date="2024-01-01",
    end_date="2024-01-31",
    dimensions=["country", "source", "medium", "deviceCategory"],
    metrics=["sessions", "totalUsers", "conversions", "engagementRate"]
)

# Transform and load
df = ga_etl.transform_data(response)
filename = ga_etl.load_data(df, output_format="csv")
```

### Step-by-Step ETL Process

```python
# Step 1: Extract
response = ga_etl.extract_data("2024-01-01", "2024-01-31")

# Step 2: Transform
df = ga_etl.transform_data(response)

# Step 3: Analyze (optional)
print(f"Total sessions: {df['sessions'].sum()}")
print(f"Top countries:\n{df.groupby('country')['sessions'].sum().head()}")

# Step 4: Load
filename = ga_etl.load_data(df, output_format="excel")
```

## 📋 Output Data Schema

### CSV/Excel Columns

| Column                  | Type     | Description                               |
| ----------------------- | -------- | ----------------------------------------- |
| country                 | string   | User's country (cleaned and standardized) |
| city                    | string   | User's city                               |
| date                    | datetime | Date of the data point                    |
| pagePath                | string   | URL path of the page                      |
| deviceCategory          | string   | desktop, mobile, or tablet                |
| sessions                | integer  | Number of sessions                        |
| totalUsers              | integer  | Total users count                         |
| screenPageViews         | integer  | Page views                                |
| userEngagementDuration  | float    | Engagement duration in seconds            |
| avg_engagement_duration | float    | Average engagement per session            |
| extracted_at            | datetime | When data was extracted                   |

### Summary Sheet (Excel only)

When using Excel output, a summary sheet includes:

- Top 10 countries by sessions
- Key metrics aggregated
- Performance indicators

## ⚙️ Configuration Options

### File Output Options

```python
# CSV output (default)
ga_etl.run_etl(output_format="csv")

# Excel with summary sheet
ga_etl.run_etl(output_format="excel")

# JSON format
ga_etl.run_etl(output_format="json")
```

### Date Range Options

```python
# Last 30 days (default)
ga_etl.run_etl()

# Custom range
ga_etl.run_etl(start_date="2024-01-01", end_date="2024-12-31")

# Yesterday only
from datetime import datetime, timedelta
yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
ga_etl.run_etl(start_date=yesterday, end_date=yesterday)
```

## 🔧 Advanced Features

### Custom Data Transformation

```python
class CustomGAETL(GoogleAnalyticsETL):
    def transform_data(self, response):
        # Call parent transformation
        df = super().transform_data(response)

        # Add custom transformations
        df['sessions_per_user'] = df['sessions'] / df['totalUsers']
        df['engagement_rate'] = df['userEngagementDuration'] / df['sessions']

        # Add business logic
        df['country_tier'] = df['country'].map({
            'United States': 'Tier 1',
            'United Kingdom': 'Tier 1',
            'Germany': 'Tier 1'
        }).fillna('Tier 2')

        return df
```

### Error Handling

```python
import logging

# Enable detailed logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    output_file = ga_etl.run_etl()
    logger.info(f"ETL completed successfully: {output_file}")
except Exception as e:
    logger.error(f"ETL failed: {str(e)}")
    # Handle error (retry, alert, etc.)
```

### Rate Limiting and Quotas

The GA4 Data API has quotas:

- **25,000 tokens per day** (each request consumes tokens)
- **250 tokens per hour**
- **10 concurrent requests**

The pipeline handles these automatically with:

- Request batching
- Automatic retry logic
- Token consumption optimization

## 📊 Data Analysis Examples

### Load and Analyze Data

```python
import pandas as pd
import matplotlib.pyplot as plt

# Load extracted data
df = pd.read_csv('output/ga_data_20250730_162528.csv')

# Basic analysis
print(f"Date range: {df['date'].min()} to {df['date'].max()}")
print(f"Total sessions: {df['sessions'].sum():,}")
print(f"Total users: {df['totalUsers'].sum():,}")

# Top pages
top_pages = df.groupby('pagePath')['sessions'].sum().sort_values(ascending=False).head(10)
print("\nTop 10 pages by sessions:")
print(top_pages)

# Geographic analysis
country_stats = df.groupby('country').agg({
    'sessions': 'sum',
    'totalUsers': 'sum',
    'userEngagementDuration': 'mean'
}).sort_values('sessions', ascending=False).head(10)

print("\nTop countries:")
print(country_stats)

# Device analysis
device_stats = df.groupby('deviceCategory')['sessions'].sum()
print("\nSessions by device:")
print(device_stats)

# Time series analysis
daily_stats = df.groupby('date')['sessions'].sum().reset_index()
daily_stats['date'] = pd.to_datetime(daily_stats['date'])

# Simple plot
plt.figure(figsize=(12, 6))
plt.plot(daily_stats['date'], daily_stats['sessions'])
plt.title('Daily Sessions Over Time')
plt.xlabel('Date')
plt.ylabel('Sessions')
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()
```

### Export for Further Analysis

```python
# Export specific segments
mobile_data = df[df['deviceCategory'] == 'mobile']
mobile_data.to_csv('output/mobile_sessions.csv', index=False)

# Export summary statistics
summary = df.groupby(['country', 'deviceCategory']).agg({
    'sessions': 'sum',
    'totalUsers': 'sum',
    'userEngagementDuration': 'mean'
}).reset_index()

summary.to_excel('output/country_device_summary.xlsx', index=False)
```

## 🚨 Troubleshooting

### Common Errors and Solutions

1. **"Property not found"**

   ```
   Error: 400 Property "123456789" does not exist
   ```

   **Solution**: Ensure Property ID is formatted as `properties/123456789`

2. **"Permission denied"**

   ```
   Error: 403 User does not have sufficient permissions
   ```

   **Solution**: Add service account email to GA4 property with Viewer role

3. **"Invalid dimensions/metrics"**

   ```
   Error: 400 Field 'users' is not a valid metric
   ```

   **Solution**: Use correct GA4 metric names (e.g., `totalUsers` not `users`)

4. **"API not enabled"**
   ```
   Error: Google Analytics Data API has not been used
   ```
   **Solution**: Enable the API in Google Cloud Console

### Debug Mode

```python
import logging

# Enable debug logging
logging.basicConfig(level=logging.DEBUG)

# Run with verbose output
ga_etl = GoogleAnalyticsETL(property_id, credentials_path)
output_file = ga_etl.run_etl()
```

### Validate Setup

```python
# Test authentication and basic access
def test_ga_setup():
    try:
        ga_etl = GoogleAnalyticsETL(property_id, credentials_path)

        # Test authentication
        ga_etl._authenticate()
        print("✅ Authentication successful")

        # Test data extraction (1 day only)
        response = ga_etl.extract_data("2024-01-01", "2024-01-01")
        print(f"✅ Data extraction successful: {len(response.rows)} rows")

        return True
    except Exception as e:
        print(f"❌ Setup test failed: {e}")
        return False

# Run test
test_ga_setup()
```

## 📚 Resources

- [GA4 Data API Documentation](https://developers.google.com/analytics/devguides/reporting/data/v1)
- [GA4 Dimensions & Metrics Reference](https://developers.google.com/analytics/devguides/reporting/data/v1/api-schema)
- [Google Cloud Console](https://console.cloud.google.com/)
- [GA4 Property Setup](https://support.google.com/analytics/answer/9304153)

## 🔄 Updates and Maintenance

### Regular Tasks

- **Monitor API quotas** and usage
- **Rotate service account keys** periodically
- **Update dependencies** with `pip install -U -r requirements.txt`
- **Review and clean output files** regularly

### Version Compatibility

- **Google Analytics Data API**: v1beta (current)
- **Python**: 3.7+ required
- **Dependencies**: See `requirements.txt` for current versions

---

**Ready to extract your Google Analytics data? Run `python3 main.py` to get started!**
