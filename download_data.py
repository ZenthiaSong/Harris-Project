"""this file is used to download the data from the website and save it to the data folder"""

import os
from io import StringIO
import pandas as pd
import requests

path = "data"

# Carbon Monitor dataset URL
carbon_monitor_url = (
    "https://datas.carbonmonitor.org/API/downloadFullDataset.php?source=carbon_global"
)

# Temperature List of tuples (url, country_name)
urls_countries = [
    (
        "https://berkeley-earth-temperature.s3.us-west-1.amazonaws.com/Regional/TAVG/china-TAVG-Trend.txt",
        "China",
    ),
    (
        "https://berkeley-earth-temperature.s3.us-west-1.amazonaws.com/Regional/TAVG/united-states-TAVG-Trend.txt",
        "United States",
    ),
    (
        "https://berkeley-earth-temperature.s3.us-west-1.amazonaws.com/Regional/TAVG/india-TAVG-Trend.txt",
        "India",
    ),
    (
        "https://berkeley-earth-temperature.s3.us-west-1.amazonaws.com/Regional/TAVG/united-kingdom-TAVG-Trend.txt",
        "United Kingdom",
    ),
    (
        "https://berkeley-earth-temperature.s3.us-west-1.amazonaws.com/Regional/TAVG/france-TAVG-Trend.txt",
        "France",
    ),
    (
        "https://berkeley-earth-temperature.s3.us-west-1.amazonaws.com/Regional/TAVG/germany-TAVG-Trend.txt",
        "Germany",
    ),
    (
        "https://berkeley-earth-temperature.s3.us-west-1.amazonaws.com/Regional/TAVG/italy-TAVG-Trend.txt",
        "Italy",
    ),
    (
        "https://berkeley-earth-temperature.s3.us-west-1.amazonaws.com/Regional/TAVG/spain-TAVG-Trend.txt",
        "Spain",
    ),
    (
        "https://berkeley-earth-temperature.s3.us-west-1.amazonaws.com/Regional/TAVG/russia-TAVG-Trend.txt",
        "Russia",
    ),
    (
        "https://berkeley-earth-temperature.s3.us-west-1.amazonaws.com/Regional/TAVG/japan-TAVG-Trend.txt",
        "Japan",
    ),
    (
        "https://berkeley-earth-temperature.s3.us-west-1.amazonaws.com/Regional/TAVG/brazil-TAVG-Trend.txt",
        "Brazil",
    ),
    (
        "https://berkeley-earth-temperature.s3.us-west-1.amazonaws.com/Global/Land_and_Ocean_complete.txt",
        "WORLD",
    ),
]

# Download the Carbon Monitor dataset
def download_carbon_monitor_dataset(path, url):
    response = requests.get(url)
    with open(os.path.join(path, "Carbon.csv"), "wb") as file:
        file.write(response.content)

# Download the temperature dataset
def download_temperature_dataset(path, urls_countries):
    all_data = pd.DataFrame()
    for url, country in urls_countries:
        response = requests.get(url)
        if response.status_code == 200:
            data = pd.read_csv(
                StringIO(response.text), comment="%", sep="\s+", header=None
            )
            columns = [
                "Year",
                "Month",
                "Monthly Anomaly",
                "Monthly Uncertainty",
                "Annual Anomaly",
                "Annual Uncertainty",
                "Five-year Anomaly",
                "Five-year Uncertainty",
                "Ten-year Anomaly",
                "Ten-year Uncertainty",
                "Twenty-year Anomaly",
                "Twenty-year Uncertainty",
            ]
            data.columns = columns
            data["Country"] = country

            # Append to the all_data DataFrame
            all_data = pd.concat([all_data, data])
        else:
            print(
                f"Failed to download data for {country}. Status code:",
                response.status_code,
            )
    # Reset index of the final DataFrame
    all_data.reset_index(drop=True, inplace=True)

    # Save the combined DataFrame to a CSV file
    all_data.to_csv(os.path.join(path, "Anomaly_Temp.csv"), index=False)

# Download the Carbon Monitor dataset
download_carbon_monitor_dataset(path, carbon_monitor_url)

# Download the temperature dataset
download_temperature_dataset(path, urls_countries)
