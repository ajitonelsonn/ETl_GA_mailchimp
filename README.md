# ETL Pipeline: Google Analytics & Mailchimp Data Extraction

A Python-based ETL (Extract, Transform, Load) pipeline that automatically extracts data from Google Analytics 4 and Mailchimp APIs, transforms it into clean structured formats, and saves it for analysis and reporting.
![Code Structure](/public/Code_Structure.png)

## 🚀 Features

- **Google Analytics 4 Integration**: Extract website analytics data including sessions, users, page views, and geographic information
- **Mailchimp Integration**: Extract mailing lists, campaign performance, and subscriber data
- **Automated Data Processing**: Clean, transform, and normalize data from both platforms
- **Multiple Output Formats**: Save data as CSV, Excel, or JSON files
- **Error Handling**: Comprehensive logging and error management
- **Configurable**: Easy setup with environment variables
- **Production Ready**: Includes timezone handling, rate limiting, and data validation

## 📊 What Data Can You Extract?

### Google Analytics 4

- Website traffic metrics (sessions, users, page views)
- Geographic data (country, city)
- Device and browser information
- User engagement metrics
- Custom date ranges and filtering

### Mailchimp

- Mailing list statistics and subscriber counts
- Campaign performance metrics (open rates, click rates)
- Subscriber demographics and geographic distribution
- Member engagement data

## 🛠️ Installation

### Prerequisites

- Python 3.7+
- Google Analytics 4 property
- Mailchimp account with API access

### Setup

1. **Clone the repository**

   ```bash
   git clone https://github.com/ajitonelsonn/ETl_GA_mailchimp.git
   cd ETl_GA_mailchimp
   ```

2. **Create virtual environment**

   ```bash
   python -m venv myenv
   source myenv/bin/activate  # On Windows: myenv\Scripts\activate
   ```

3. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Environment Configuration**

   Copy the example environment file and configure your API credentials:

   ```bash
   cp .env.example .env
   ```

   Edit `.env` with your actual credentials:

   ```env
   # Google Analytics Configuration
   GA_PROPERTY_ID=properties/123456789
   GA_CREDENTIALS_PATH=./credentials/ga-service-account-key.json

   # Mailchimp Configuration
   MAILCHIMP_API_KEY=your-mailchimp-api-key-here
   MAILCHIMP_SERVER_PREFIX=us1
   ```

5. **Create directories**
   ```bash
   mkdir -p credentials output
   ```

## 🔑 API Setup

### Google Analytics 4

See [Google Analytics Setup Guide](./Google%20Analytics%20Setup%20Guide.md) for detailed instructions on:

- Creating service account credentials
- Getting your Property ID
- Setting up API access

### Mailchimp

See [Mailchimp API Setup Guide](./Mailchimp%20API%20Setup%20Guide.md) for instructions on:

- Generating API keys
- Finding your server prefix
- Understanding API limits

## 🚀 Usage

### Run Google Analytics ETL

```bash
cd ga_etl
python main.py
```

### Run Mailchimp ETL

```bash
cd Mailchimp_ETL_Pipeline
python main.py
```

### Custom Date Ranges (Google Analytics)

```python
from ga_etl_pipeline import GoogleAnalyticsETL

ga_etl = GoogleAnalyticsETL(property_id, credentials_path)
output_file = ga_etl.run_etl(
    start_date="2024-01-01",
    end_date="2024-03-31",
    output_format="excel"
)
```

### Include Member Data (Mailchimp)

```python
from mailchimp_etl_pipeline import MailchimpETL

mc_etl = MailchimpETL(api_key, server_prefix)
output_file = mc_etl.run_etl(
    include_members=True,
    since_date="2024-01-01",
    output_format="csv"
)
```

## 📁 Output Structure

All generated files are saved in the `output/` directory:

```
output/
├── ga_data_20250730_143022.csv
├── mailchimp_data_lists_20250730_153325.csv
├── mailchimp_data_campaigns_20250730_153325.csv
└── mailchimp_data_members_20250730_153325.csv
```

## 📋 Data Schema

### Google Analytics Output

| Column                 | Description                           |
| ---------------------- | ------------------------------------- |
| date                   | Date of the data                      |
| country                | User's country                        |
| city                   | User's city                           |
| pagePath               | Page URL path                         |
| deviceCategory         | Device type (desktop, mobile, tablet) |
| sessions               | Number of sessions                    |
| totalUsers             | Total users                           |
| screenPageViews        | Page views                            |
| userEngagementDuration | Engagement duration in seconds        |

### Mailchimp Output

**Lists Data:**
| Column | Description |
|--------|-------------|
| list_id | Unique list identifier |
| list_name | Name of the mailing list |
| member_count | Total subscribers |
| open_rate | List average open rate |
| click_rate | List average click rate |

**Campaigns Data:**
| Column | Description |
|--------|-------------|
| campaign_id | Unique campaign identifier |
| campaign_name | Campaign subject line |
| send_time | When campaign was sent |
| emails_sent | Total emails sent |
| open_rate | Campaign open rate |
| click_rate | Campaign click rate |

## ⚙️ Configuration Options

### Google Analytics

- **Date Range**: Specify custom start and end dates
- **Dimensions**: Country, city, page path, device category
- **Metrics**: Sessions, users, page views, engagement duration
- **Output Format**: CSV, Excel, JSON

### Mailchimp

- **Include Members**: Extract detailed subscriber data
- **Date Filtering**: Filter campaigns by send date
- **List Selection**: Process specific mailing lists
- **Output Format**: CSV, Excel, JSON

## 🔧 Advanced Usage

### Custom Dimensions and Metrics

Modify the default dimensions and metrics in the ETL classes:

```python
# Custom GA4 dimensions
dimensions = ["country", "source", "medium", "deviceCategory"]
metrics = ["sessions", "totalUsers", "conversions"]

response = ga_etl.extract_data(
    start_date="2024-01-01",
    end_date="2024-01-31",
    dimensions=dimensions,
    metrics=metrics
)
```

### Error Handling and Logging

The pipeline includes comprehensive logging. Check logs for debugging:

```python
import logging
logging.basicConfig(level=logging.INFO)
```

## 📊 Data Analysis Examples

### Python Analysis

```python
import pandas as pd

# Load Google Analytics data
ga_data = pd.read_csv('output/ga_data_20250730_143022.csv')

# Top countries by sessions
top_countries = ga_data.groupby('country')['sessions'].sum().sort_values(ascending=False).head(10)
print(top_countries)

# Load Mailchimp campaign data
campaigns = pd.read_csv('output/mailchimp_data_campaigns_20250730_153325.csv')

# Campaign performance analysis
avg_open_rate = campaigns['open_rate'].mean()
best_performing = campaigns.nlargest(5, 'open_rate')[['campaign_name', 'open_rate', 'click_rate']]
```

## 🔒 Security Best Practices

- ✅ Store API credentials in environment variables
- ✅ Add `.env` and `credentials/` to `.gitignore`
- ✅ Use service accounts for Google Analytics (not personal accounts)
- ✅ Regularly rotate API keys
- ✅ Restrict API key permissions to minimum required

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Troubleshooting

### Common Issues

1. **"Property not found" (Google Analytics)**

   - Verify your Property ID format: `properties/123456789`
   - Ensure service account has access to the GA4 property

2. **"Invalid API Key" (Mailchimp)**

   - Check your API key is correct and active
   - Verify the server prefix matches your account

3. **"Permission denied"**

   - Ensure service account has proper roles
   - Check API permissions and quotas

4. **"Module not found"**
   - Activate your virtual environment
   - Install requirements: `pip install -r requirements.txt`

### Getting Help

- Check the [Issues](https://github.com/ajitonelsonn/ETl_GA_mailchimp/issues) page
- Read the detailed setup guides for each platform
- Review the example usage in the code

---

**Made with ❤️ for data analysts and marketers who need clean, accessible data.**
