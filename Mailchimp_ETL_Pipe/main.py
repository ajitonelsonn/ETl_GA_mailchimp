import pandas as pd
import requests
import json
import logging
from datetime import datetime, timedelta
import time
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class MailchimpETL:
    def __init__(self, api_key, server_prefix):
        """
        Initialize Mailchimp ETL pipeline
        
        Args:
            api_key (str): Mailchimp API key
            server_prefix (str): Server prefix (e.g., 'us1', 'us2', etc.)
        """
        self.api_key = api_key
        self.server_prefix = server_prefix
        self.base_url = f"https://{server_prefix}.api.mailchimp.com/3.0"
        self.headers = {
            'Authorization': f'apikey {api_key}',
            'Content-Type': 'application/json'
        }
        
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
    
    def _make_request(self, endpoint, params=None):
        """
        Make authenticated request to Mailchimp API
        
        Args:
            endpoint (str): API endpoint
            params (dict): Query parameters
            
        Returns:
            dict: API response
        """
        url = f"{self.base_url}/{endpoint}"
        
        try:
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            
            # Handle rate limiting
            if response.status_code == 429:
                self.logger.warning("Rate limit reached, waiting 60 seconds...")
                time.sleep(60)
                return self._make_request(endpoint, params)
            
            return response.json()
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"API request failed: {str(e)}")
            raise
    
    def extract_lists(self):
        """Extract all mailing lists"""
        try:
            self.logger.info("Extracting mailing lists...")
            response = self._make_request("lists", params={'count': 1000})
            
            lists_data = []
            for list_item in response.get('lists', []):
                lists_data.append({
                    'list_id': list_item['id'],
                    'list_name': list_item['name'],
                    'member_count': list_item['stats']['member_count'],
                    'unsubscribe_count': list_item['stats']['unsubscribe_count'],
                    'open_rate': list_item['stats']['open_rate'],
                    'click_rate': list_item['stats']['click_rate'],
                    'date_created': list_item['date_created'],
                    'visibility': list_item.get('visibility', 'private')
                })
            
            self.logger.info(f"Extracted {len(lists_data)} mailing lists")
            return lists_data
            
        except Exception as e:
            self.logger.error(f"Failed to extract lists: {str(e)}")
            raise
    
    def extract_campaigns(self, since_date=None):
        """
        Extract campaign data
        
        Args:
            since_date (str): Date in YYYY-MM-DD format to filter campaigns
            
        Returns:
            list: Campaign data
        """
        try:
            self.logger.info("Extracting campaigns...")
            params = {'count': 1000, 'status': 'sent'}
            
            if since_date:
                params['since_send_time'] = since_date
            
            response = self._make_request("campaigns", params=params)
            
            campaigns_data = []
            for campaign in response.get('campaigns', []):
                # Get detailed campaign stats
                campaign_id = campaign['id']
                stats = self._make_request(f"campaigns/{campaign_id}")
                
                campaigns_data.append({
                    'campaign_id': campaign_id,
                    'campaign_name': campaign.get('settings', {}).get('subject_line', 'Unknown'),
                    'list_id': campaign.get('recipients', {}).get('list_id'),
                    'send_time': campaign.get('send_time'),
                    'emails_sent': stats.get('emails_sent', 0),
                    'opens': stats.get('opens', {}).get('opens_total', 0),
                    'unique_opens': stats.get('opens', {}).get('unique_opens', 0),
                    'open_rate': stats.get('opens', {}).get('open_rate', 0),
                    'clicks': stats.get('clicks', {}).get('clicks_total', 0),
                    'unique_clicks': stats.get('clicks', {}).get('unique_clicks', 0),
                    'click_rate': stats.get('clicks', {}).get('click_rate', 0),
                    'unsubscribes': stats.get('unsubscribed', {}).get('unsubscribes', 0),
                    'bounces': stats.get('bounces', {}).get('hard_bounces', 0) + stats.get('bounces', {}).get('soft_bounces', 0),
                    'campaign_type': campaign.get('type', 'regular'),
                    'status': campaign.get('status')
                })
                
                # Add small delay to respect rate limits
                time.sleep(0.1)
            
            self.logger.info(f"Extracted {len(campaigns_data)} campaigns")
            return campaigns_data
            
        except Exception as e:
            self.logger.error(f"Failed to extract campaigns: {str(e)}")
            raise
    
    def extract_members(self, list_id, status='subscribed'):
        """
        Extract member data for a specific list
        
        Args:
            list_id (str): Mailchimp list ID
            status (str): Member status filter
            
        Returns:
            list: Member data
        """
        try:
            self.logger.info(f"Extracting members for list {list_id}...")
            
            members_data = []
            offset = 0
            count = 1000
            
            while True:
                params = {
                    'count': count,
                    'offset': offset,
                    'status': status
                }
                
                response = self._make_request(f"lists/{list_id}/members", params=params)
                members = response.get('members', [])
                
                if not members:
                    break
                
                for member in members:
                    # Extract location data (important for human rights monitoring)
                    location = member.get('location', {})
                    
                    members_data.append({
                        'member_id': member['id'],
                        'email': member['email_address'],
                        'status': member['status'],
                        'list_id': list_id,
                        'timestamp_signup': member.get('timestamp_signup'),
                        'timestamp_opt': member.get('timestamp_opt'),
                        'country_code': location.get('country_code'),
                        'timezone': location.get('timezone'),
                        'latitude': location.get('latitude'),
                        'longitude': location.get('longitude'),
                        'ip_signup': member.get('ip_signup'),
                        'ip_opt': member.get('ip_opt'),
                        'language': member.get('language'),
                        'member_rating': member.get('member_rating', 0),
                        'email_client': member.get('email_client'),
                        'tags_count': member.get('tags_count', 0)
                    })
                
                offset += count
                time.sleep(0.1)  # Rate limiting
            
            self.logger.info(f"Extracted {len(members_data)} members for list {list_id}")
            return members_data
            
        except Exception as e:
            self.logger.error(f"Failed to extract members: {str(e)}")
            raise
    
    def transform_data(self, data_type, raw_data):
        """
        Transform raw Mailchimp data into structured DataFrame
        
        Args:
            data_type (str): Type of data ('lists', 'campaigns', 'members')
            raw_data (list): Raw data from API
            
        Returns:
            pandas.DataFrame: Cleaned and structured data
        """
        try:
            df = pd.DataFrame(raw_data)
            
            if df.empty:
                self.logger.warning(f"No data to transform for {data_type}")
                return df
            
            # Common transformations
            if data_type == 'campaigns':
                # Convert datetime columns and remove timezone info for Excel compatibility
                if 'send_time' in df.columns:
                    df['send_time'] = pd.to_datetime(df['send_time'])
                    # Remove timezone info if present
                    if df['send_time'].dt.tz is not None:
                        df['send_time'] = df['send_time'].dt.tz_localize(None)
                    df['send_date'] = df['send_time'].dt.date
                    df['send_hour'] = df['send_time'].dt.hour
                
                # Calculate engagement rates
                df['engagement_rate'] = (df['unique_opens'] + df['unique_clicks']) / df['emails_sent'] * 100
                df['engagement_rate'] = df['engagement_rate'].fillna(0)
                
                # Add performance categories for human rights reporting
                df['performance_category'] = pd.cut(
                    df['open_rate'] * 100,
                    bins=[0, 15, 25, 35, 100],
                    labels=['Low', 'Medium', 'High', 'Excellent']
                )
            
            elif data_type == 'members':
                # Convert datetime columns and remove timezone info for Excel compatibility
                datetime_cols = ['timestamp_signup', 'timestamp_opt']
                for col in datetime_cols:
                    if col in df.columns:
                        df[col] = pd.to_datetime(df[col])
                        # Remove timezone info if present
                        if df[col].dt.tz is not None:
                            df[col] = df[col].dt.tz_localize(None)
                
                # Add geographic insights (important for human rights context)
                if 'country_code' in df.columns:
                    country_mapping = {
                        'UA': 'Ukraine', 'RU': 'Russia', 'US': 'United States',
                        'GB': 'United Kingdom', 'DE': 'Germany', 'FR': 'France'
                    }
                    df['country_name'] = df['country_code'].map(country_mapping)
                    df['country_name'] = df['country_name'].fillna(df['country_code'])
                
                # Calculate member tenure
                if 'timestamp_signup' in df.columns:
                    df['days_since_signup'] = (datetime.now() - df['timestamp_signup']).dt.days
            
            elif data_type == 'lists':
                # Convert datetime columns and remove timezone info for Excel compatibility
                if 'date_created' in df.columns:
                    df['date_created'] = pd.to_datetime(df['date_created'])
                    # Remove timezone info if present
                    if df['date_created'].dt.tz is not None:
                        df['date_created'] = df['date_created'].dt.tz_localize(None)
                
                # Calculate list health metrics
                df['unsubscribe_rate'] = (df['unsubscribe_count'] / df['member_count']) * 100
                df['unsubscribe_rate'] = df['unsubscribe_rate'].fillna(0)
            
            # Add extraction metadata
            df['extracted_at'] = datetime.now()
            df['data_source'] = 'mailchimp'
            
            self.logger.info(f"Successfully transformed {data_type} data: {len(df)} rows")
            return df
            
        except Exception as e:
            self.logger.error(f"Data transformation failed for {data_type}: {str(e)}")
            raise
    
    def load_data(self, dataframes_dict, output_format='excel', output_path='mailchimp_data'):
        """
        Load transformed data to specified format
        
        Args:
            dataframes_dict (dict): Dictionary of DataFrames {data_type: df}
            output_format (str): 'csv', 'excel', or 'json'
            output_path (str): Output file path
        """
        try:
            # Create output directory if it doesn't exist
            output_dir = 'output'
            os.makedirs(output_dir, exist_ok=True)
            
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            
            if output_format.lower() == 'excel':
                filename = os.path.join(output_dir, f"{output_path}_{timestamp}.xlsx")
                
                with pd.ExcelWriter(filename, engine='openpyxl') as writer:
                    for data_type, df in dataframes_dict.items():
                        if not df.empty:
                            sheet_name = data_type.capitalize()[:31]  # Excel sheet name limit
                            df.to_excel(writer, sheet_name=sheet_name, index=False)
                    
                    # Add summary dashboard
                    summary_df = self._create_summary_dashboard(dataframes_dict)
                    if not summary_df.empty:
                        summary_df.to_excel(writer, sheet_name='Dashboard', index=False)
            
            elif output_format.lower() == 'csv':
                filenames = []
                for data_type, df in dataframes_dict.items():
                    if not df.empty:
                        filename = os.path.join(output_dir, f"{output_path}_{data_type}_{timestamp}.csv")
                        df.to_csv(filename, index=False)
                        filenames.append(filename)
                filename = filenames
            
            elif output_format.lower() == 'json':
                filename = os.path.join(output_dir, f"{output_path}_{timestamp}.json")
                combined_data = {}
                for data_type, df in dataframes_dict.items():
                    if not df.empty:
                        combined_data[data_type] = df.to_dict('records')
                
                with open(filename, 'w') as f:
                    json.dump(combined_data, f, indent=2, default=str)
            
            self.logger.info(f"Successfully loaded data to {filename}")
            return filename
            
        except Exception as e:
            self.logger.error(f"Data loading failed: {str(e)}")
            raise
    
    def _create_summary_dashboard(self, dataframes_dict):
        """Create summary dashboard for human rights reporting"""
        summary_data = []
        
        # Campaign performance summary
        if 'campaigns' in dataframes_dict and not dataframes_dict['campaigns'].empty:
            campaigns_df = dataframes_dict['campaigns']
            summary_data.extend([
                {'Metric': 'Total Campaigns', 'Value': len(campaigns_df)},
                {'Metric': 'Avg Open Rate (%)', 'Value': f"{campaigns_df['open_rate'].mean() * 100:.2f}"},
                {'Metric': 'Avg Click Rate (%)', 'Value': f"{campaigns_df['click_rate'].mean() * 100:.2f}"},
                {'Metric': 'Total Emails Sent', 'Value': campaigns_df['emails_sent'].sum()}
            ])
        
        # Lists summary
        if 'lists' in dataframes_dict and not dataframes_dict['lists'].empty:
            lists_df = dataframes_dict['lists']
            summary_data.extend([
                {'Metric': 'Total Lists', 'Value': len(lists_df)},
                {'Metric': 'Total Subscribers', 'Value': lists_df['member_count'].sum()},
                {'Metric': 'Total Unsubscribes', 'Value': lists_df['unsubscribe_count'].sum()}
            ])
        
        # Geographic distribution (if members data available)
        if 'members' in dataframes_dict and not dataframes_dict['members'].empty:
            members_df = dataframes_dict['members']
            if 'country_name' in members_df.columns:
                top_countries = members_df['country_name'].value_counts().head(5)
                for country, count in top_countries.items():
                    summary_data.append({
                        'Metric': f'Subscribers in {country}',
                        'Value': count
                    })
        
        return pd.DataFrame(summary_data)
    
    def run_etl(self, include_members=False, specific_list_ids=None, since_date=None, output_format='csv'):
        """
        Run complete ETL pipeline
        
        Args:
            include_members (bool): Whether to extract member data
            specific_list_ids (list): Specific list IDs to process
            since_date (str): Date filter for campaigns
            output_format (str): Output format
            
        Returns:
            str: Output filename
        """
        self.logger.info("Starting Mailchimp ETL process...")
        
        dataframes = {}
        
        # Extract and transform lists
        lists_data = self.extract_lists()
        dataframes['lists'] = self.transform_data('lists', lists_data)
        
        # Extract and transform campaigns
        campaigns_data = self.extract_campaigns(since_date)
        dataframes['campaigns'] = self.transform_data('campaigns', campaigns_data)
        
        # Extract and transform members if requested
        if include_members:
            all_members_data = []
            
            # Get list IDs to process
            if specific_list_ids:
                list_ids = specific_list_ids
            else:
                list_ids = [item['list_id'] for item in lists_data[:3]]  # Limit to first 3 lists for demo
            
            for list_id in list_ids:
                members_data = self.extract_members(list_id)
                all_members_data.extend(members_data)
            
            if all_members_data:
                dataframes['members'] = self.transform_data('members', all_members_data)
        
        # Load data
        filename = self.load_data(dataframes, output_format)
        
        self.logger.info("Mailchimp ETL process completed successfully")
        return filename

# Example usage
if __name__ == "__main__":
    # Configuration from environment variables
    API_KEY = os.getenv('MAILCHIMP_API_KEY')
    SERVER_PREFIX = os.getenv('MAILCHIMP_SERVER_PREFIX', 'us1')  # Default to 'us1' if not set
    
    if not API_KEY:
        raise ValueError("MAILCHIMP_API_KEY not found in environment variables. Please check your .env file.")
    
    # Initialize ETL pipeline
    mailchimp_etl = MailchimpETL(API_KEY, SERVER_PREFIX)
    
    # Run ETL process
    try:
        output_file = mailchimp_etl.run_etl(
            include_members=True,
            since_date="2024-01-01",
            output_format="csv"
        )
        print(f"ETL completed successfully. Output file: {output_file}")
        
    except Exception as e:
        print(f"ETL process failed: {str(e)}")