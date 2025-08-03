
import os
import requests
import pandas as pd
from langchain import LangChain
from mcp import MCP  # Assuming MCP is a library or tool you have access to

class SullyGnomeScraper:
    def __init__(self, creator_name, data_directory="data"):
        """
        Initialize the SullyGnomeScraper with the content creator's name.
        
        :param creator_name: Name of the content creator
        :param data_directory: Directory to save the CSV files
        """
        self.creator_name = creator_name
        self.data_directory = data_directory
        os.makedirs(self.data_directory, exist_ok=True)  # Create data directory if it doesn't exist
        self.langchain = LangChain()
        self.mcp = MCP()

    def download_csv(self):
        """
        Download the CSV file from SullyGnome for the specified content creator.
        """
        url = f"https://sullygnome.com/channel/{self.creator_name}/stats/csv"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
        }
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            csv_file_path = os.path.join(self.data_directory, f"{self.creator_name}_stats.csv")
            with open(csv_file_path, 'wb') as file:
                file.write(response.content)
            print(f"CSV file downloaded and saved to {csv_file_path}")
            return csv_file_path
        else:
            print(f"Failed to download CSV file. Status code: {response.status_code}")
            return None

    def load_csv(self, csv_file_path):
        """
        Load the CSV file into a pandas DataFrame.
        
        :param csv_file_path: Path to the CSV file
        :return: pandas DataFrame
        """
        if os.path.exists(csv_file_path):
            df = pd.read_csv(csv_file_path)
            print(f"CSV file loaded from {csv_file_path}")
            return df
        else:
            print(f"CSV file not found at {csv_file_path}")
            return None

    def process_data(self, df):
        """
        Perform any necessary data processing on the DataFrame.
        
        :param df: pandas DataFrame
        :return: Processed DataFrame
        """
        if df is not None:
            # Example processing: Calculate Variability Ratio (Peak / Average)
            df["Variability Ratio"] = df["Peak viewers"] / df["Avg viewers"]
            # Calculate Peak Deviation Index ((Peak - Average) / Average)
            df["Peak Deviation Index"] = (df["Peak viewers"] - df["Avg viewers"]) / df["Avg viewers"]
            print("Data processed successfully.")
            return df
        else:
            print("No data to process.")
            return None

    def run(self):
        """
        Run the entire scraping and processing pipeline.
        """
        # High-level coordination with LangChain
        self.langchain.start_pipeline()

        # Download the CSV file using MCP
        csv_file_path = self.mcp.run_task(self.download_csv)
        if csv_file_path:
            # Load the CSV file into a DataFrame using MCP
            df = self.mcp.run_task(lambda: self.load_csv(csv_file_path))
            if df is not None:
                # Process the data using MCP
                processed_df = self.mcp.run_task(lambda: self.process_data(df))
                if processed_df is not None:
                    # Print the first few rows of the processed DataFrame
                    print(processed_df.head())

        # End the pipeline
        self.langchain.end_pipeline()