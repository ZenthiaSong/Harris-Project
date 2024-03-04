import os
import pandas as pd
from const import DATA_PATH, SPECIFIED_COUNTRIES
from sentiment_topic import analyze_sentiment, analyze_title_topics

def process_Disaster_data(path, specific_countries, rest_of_world, world):
    df_Disaster = pd.read_csv(os.path.join(path, "Disasters.csv"))
    df_Disaster["start_date"] = pd.to_datetime(
        df_Disaster["start_date"], errors="coerce"
    )
    df_Disaster["Year"] = df_Disaster["start_date"].dt.year
    df_Disaster["Month"] = df_Disaster["start_date"].dt.month
    
    df_Disaster["Country"] = df_Disaster["Country"].replace({
        "Russian Federation (the)": "Russian",
        "United States of America (the)": "United States"
    })

    df_Disaster = df_Disaster[
        ["Disaster Type", "Country", "Year", "Month", "Total Deaths"]
    ]
    df_Disaster = df_Disaster[df_Disaster["Year"].isin([2019, 2020])]
    df_Disaster.fillna(0, inplace=True)

    # Grouping all data by 'Year', 'Month', and 'Disaster Type' and summing 'Total Deaths' for "WORLD"
    df_world_grouped = (
        df_Disaster.groupby(["Year", "Month", "Disaster Type"])
        .agg({"Total Deaths": "sum"})
        .reset_index()
    )
    df_world_grouped["Country"] = world

    # Separating specified countries and 'Rest of the World'
    df_specific = df_Disaster[df_Disaster["Country"].isin(specific_countries)]
    df_rest = df_Disaster[~df_Disaster["Country"].isin(specific_countries)]
    df_rest["Country"] = rest_of_world

    # Grouping 'Rest of the World' data by 'Year' and 'Month' and summing 'Total Deaths'
    df_rest_grouped = (
        df_rest.groupby(["Year", "Month", "Disaster Type"])
        .agg({"Total Deaths": "sum"})
        .reset_index()
    )
    df_rest_grouped["Country"] = rest_of_world

    # Combining the specific countries data with the 'Rest of the World' data
    df_combined = pd.concat(
        [df_specific, df_rest_grouped, df_world_grouped], ignore_index=True
    )

    return df_combined

def process_Carbon_data(path):
    df_Carbon = pd.read_csv(os.path.join(path, "Carbon.csv"))
    df_Carbon["date"] = pd.to_datetime(df_Carbon["date"], errors="coerce")
    df_Carbon["Year"] = df_Carbon["date"].dt.year
    df_Carbon["Month"] = df_Carbon["date"].dt.month
    df_Carbon = df_Carbon[["country", "Year", "Month", "sector", "value"]]
    df_Carbon = df_Carbon[df_Carbon["Year"].isin([2019, 2020])]
    df_Carbon.fillna(0, inplace=True)
    df_Carbon.rename(
        columns={"country": "Country", "sector": "Sector", "value": "Value"},
        inplace=True,
    )
    df_Carbon = df_Carbon[df_Carbon["Country"] != "EU27 & UK"]
    df_Carbon["Value"] = df_Carbon["Value"].round(3)

    return df_Carbon

def process_Reddit_data(path):
    df_Reddit = pd.read_csv(os.path.join(path, "Reddit.csv"))
    df_Reddit["post_created_time"] = pd.to_datetime(
        df_Reddit["post_created_time"], errors="coerce"
    )
    df_Reddit["Year"] = df_Reddit["post_created_time"].dt.year
    df_Reddit["Month"] = df_Reddit["post_created_time"].dt.month
    df_Reddit = df_Reddit[
        ["post_self_text", "Year", "Month", "post_title", "self_text"]
    ]
    df_Reddit = df_Reddit[df_Reddit["Year"].isin([2019, 2020])]
    df_Reddit.rename(
        columns={
            "post_self_text": "Post",
            "post_title": "Title",
            "self_text": "Comment",
        },
        inplace=True,
    )

    # Apply sentiment analysis on the 'Comment' column
    df_Reddit["Comment_Sentiment"] = df_Reddit["Comment"].apply(analyze_sentiment)
    # Apply topics in post titles and add a Topic column
    df_Reddit["Topic"] = df_Reddit["Title"].apply(analyze_title_topics)

    return df_Reddit

def process_Temperature_data(path):
    df_Temperature = pd.read_csv(os.path.join(path, "Anomaly_Temp.csv"))
    df_Temperature = df_Temperature[
        ["Year", "Month", "Monthly Anomaly", "Monthly Uncertainty", "Country"]
    ]
    df_Temperature = df_Temperature[df_Temperature["Year"].isin([2019, 2020])]

    return df_Temperature

def process_main():
    df_Carbon = process_Carbon_data(DATA_PATH)
    df_Reddit = process_Reddit_data(DATA_PATH)
    df_Disaster = process_Disaster_data(DATA_PATH, SPECIFIED_COUNTRIES, "ROW", "WORLD")
    df_Temperature = process_Temperature_data(DATA_PATH)

    # Saving the dataframes to new CSV files
    df_Carbon.to_csv(os.path.join(DATA_PATH, "Processed_Carbon.csv"), index=False)
    df_Reddit.to_csv(os.path.join(DATA_PATH, "Processed_Reddit.csv"), index=False)
    df_Disaster.to_csv(os.path.join(DATA_PATH, "Processed_Disaster.csv"), index=False)
    df_Temperature.to_csv(os.path.join(DATA_PATH, "Processed_Temperature.csv"), index=False)

    return df_Carbon, df_Reddit, df_Disaster, df_Temperature

df_Carbon, df_Reddit, df_Disaster, df_Temperature = process_main()

