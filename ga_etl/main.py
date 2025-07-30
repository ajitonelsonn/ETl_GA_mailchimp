import pandas as pd
import requests
from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import (
    DateRange,
    Dimension,
    Metric,
    RunReportRequest,
)
from google.oauth2.service_account import Credentials
import json
import logging
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class GoogleAnalyticsETL:
    def __init__(self, property_id, credentials_path):
        """
        Initialize Google Analytics ETL pipeline
        
        Args:
            property_id (str): GA property ID (format: properties/XXXXXX)
            credentials_path (str): Path to service account JSON file
        """
        self.property_id = property_id
        self.credentials_path = credentials_path
        self.client = None
        
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
    def _authenticate(self):
        """Authenticate with Google Analytics API"""
        try:
            credentials = Credentials.from_service_account_file(
                self.credentials_path,
                scopes=["https://www.googleapis.com/auth/analytics.readonly"]
            )
            self.client = BetaAnalyticsDataClient(credentials=credentials)
            self.logger.info("Successfully authenticated with Google Analytics API")
        except Exception as e:
            self.logger.error(f"Authentication failed: {str(e)}")
            raise
    
    def extract_data(self, start_date, end_date, dimensions=None, metrics=None):
        """
        Extract data from Google Analytics
        
        Args:
            start_date (str): Start date in YYYY-MM-DD format
            end_date (str): End date in YYYY-MM-DD format
            dimensions (list): List of dimension names
            metrics (list): List of metric names
            
        Returns:
            dict: Raw response from GA API
        """
        if not self.client:
            self._authenticate()
        
        # Default dimensions and metrics for human rights monitoring
        if dimensions is None:
            dimensions = ["country", "city", "date", "pagePath", "deviceCategory"]
        
        if metrics is None:
            metrics = ["sessions", "totalUsers", "screenPageViews", "userEngagementDuration"]
        
        try:
            request = RunReportRequest(
                property=self.property_id,
                dimensions=[Dimension(name=dim) for dim in dimensions],
                metrics=[Metric(name=met) for met in metrics],
                date_ranges=[DateRange(start_date=start_date, end_date=end_date)],
            )
            
            response = self.client.run_report(request=request)
            self.logger.info(f"Successfully extracted {len(response.rows)} rows from GA")
            return response
            
        except Exception as e:
            self.logger.error(f"Data extraction failed: {str(e)}")
            raise
    
    def transform_data(self, response):
        """
        Transform GA response into structured DataFrame
        
        Args:
            response: GA API response object
            
        Returns:
            pandas.DataFrame: Cleaned and structured data
        """
        try:
            # Extract dimension and metric names
            dimension_names = [dim.name for dim in response.dimension_headers]
            metric_names = [met.name for met in response.metric_headers]
            
            # Process rows
            data = []
            for row in response.rows:
                row_data = {}
                
                # Add dimensions
                for i, dim_value in enumerate(row.dimension_values):
                    row_data[dimension_names[i]] = dim_value.value
                
                # Add metrics (convert to appropriate types)
                for i, met_value in enumerate(row.metric_values):
                    metric_name = metric_names[i]
                    value = met_value.value
                    
                    # Convert metrics to appropriate data types
                    if metric_name in ['sessions', 'totalUsers', 'screenPageViews']:
                        row_data[metric_name] = int(value) if value != '0' else 0
                    elif metric_name in ['userEngagementDuration']:
                        row_data[metric_name] = float(value) if value != '0.0' else 0.0
                    else:
                        row_data[metric_name] = value
                
                data.append(row_data)
            
            df = pd.DataFrame(data)
            
            # Data cleaning and transformation
            if 'date' in df.columns:
                df['date'] = pd.to_datetime(df['date'])
            
            # Clean country names (important for human rights monitoring)
            if 'country' in df.columns:
                df['country'] = df['country'].str.strip().str.title()
                # Handle special cases for human rights context
                df['country'] = df['country'].replace({
                    'Russian Federation': 'Russia',
                    'United States': 'USA'
                })
            
            # Add derived metrics
            if 'userEngagementDuration' in df.columns and 'sessions' in df.columns:
                df['avg_engagement_duration'] = df['userEngagementDuration'] / df['sessions']
                df['avg_engagement_duration'] = df['avg_engagement_duration'].fillna(0)
            
            # Add extraction timestamp
            df['extracted_at'] = datetime.now()
            
            self.logger.info(f"Successfully transformed data: {len(df)} rows, {len(df.columns)} columns")
            return df
            
        except Exception as e:
            self.logger.error(f"Data transformation failed: {str(e)}")
            raise
    
    def load_data(self, df, output_format='csv', output_path='ga_data'):
        """
        Load transformed data to specified format
        
        Args:
            df (pandas.DataFrame): Transformed data
            output_format (str): 'csv', 'excel', or 'json'
            output_path (str): Output file path (without extension)
        """
        try:
            # Create output directory if it doesn't exist
            output_dir = 'output'
            os.makedirs(output_dir, exist_ok=True)
            
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            
            if output_format.lower() == 'csv':
                filename = os.path.join(output_dir, f"{output_path}_{timestamp}.csv")
                df.to_csv(filename, index=False)
                
            elif output_format.lower() == 'excel':
                filename = os.path.join(output_dir, f"{output_path}_{timestamp}.xlsx")
                with pd.ExcelWriter(filename, engine='openpyxl') as writer:
                    df.to_excel(writer, sheet_name='GA_Data', index=False)
                    
                    # Add summary sheet for human rights reporting
                    summary = self._create_summary(df)
                    summary.to_excel(writer, sheet_name='Summary', index=False)
                    
            elif output_format.lower() == 'json':
                filename = os.path.join(output_dir, f"{output_path}_{timestamp}.json")
                df.to_json(filename, orient='records', date_format='iso')
            
            self.logger.info(f"Successfully loaded data to {filename}")
            return filename
            
        except Exception as e:
            self.logger.error(f"Data loading failed: {str(e)}")
            raise
    
    def _create_summary(self, df):
        """Create summary statistics for human rights reporting"""
        summary_data = []
        
        if 'country' in df.columns:
            top_countries = df.groupby('country').agg({
                'sessions': 'sum',
                'totalUsers': 'sum',
                'screenPageViews': 'sum'
            }).sort_values('sessions', ascending=False).head(10)
            
            for country, row in top_countries.iterrows():
                summary_data.append({
                    'metric': f'Top Country: {country}',
                    'sessions': row['sessions'],
                    'totalUsers': row['totalUsers'],
                    'screenPageViews': row['screenPageViews']
                })
        
        return pd.DataFrame(summary_data)
    
    def run_etl(self, start_date=None, end_date=None, output_format='csv'):
        """
        Run complete ETL pipeline
        
        Args:
            start_date (str): Start date (defaults to 30 days ago)
            end_date (str): End date (defaults to yesterday)
            output_format (str): Output format
            
        Returns:
            str: Output filename
        """
        # Set default dates if not provided
        if not end_date:
            end_date = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
        if not start_date:
            start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
        
        self.logger.info(f"Starting ETL process for date range: {start_date} to {end_date}")
        
        # Extract
        response = self.extract_data(start_date, end_date)
        
        # Transform
        df = self.transform_data(response)
        
        # Load
        filename = self.load_data(df, output_format)
        
        self.logger.info("ETL process completed successfully")
        return filename

# Example usage
if __name__ == "__main__":
    # Configuration from environment variables
    PROPERTY_ID = os.getenv('GA_PROPERTY_ID')
    CREDENTIALS_PATH = os.getenv('GA_CREDENTIALS_PATH')
    
    if not PROPERTY_ID:
        raise ValueError("GA_PROPERTY_ID not found in environment variables. Please check your .env file.")
    
    if not CREDENTIALS_PATH:
        raise ValueError("GA_CREDENTIALS_PATH not found in environment variables. Please check your .env file.")
    
    # Initialize ETL pipeline
    ga_etl = GoogleAnalyticsETL(PROPERTY_ID, CREDENTIALS_PATH)
    
    # Run ETL process
    try:
        output_file = ga_etl.run_etl(
            start_date="2024-01-01",
            end_date="2024-01-31",
            output_format="csv"
        )
        print(f"ETL completed successfully. Output file: {output_file}")
        
    except Exception as e:
        print(f"ETL process failed: {str(e)}")