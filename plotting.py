import geopandas as gpd
import os
import numpy as np
import matplotlib.pyplot as plt
from wordcloud import WordCloud, STOPWORDS
from analysis import Analysis
from const import DATA_PATH, SPECIFIED_COUNTRIES, IMAGES_PATH
from data_process import (
    process_Carbon_data,
    process_Reddit_data,
    process_Temperature_data,
    process_Disaster_data
)

def plot_word_cloud():
    # Process Reddit data
    reddit_data = process_Reddit_data(DATA_PATH)
    comments = reddit_data["Comment"].dropna().tolist()  # Ensure no NaN values

    # Define keywords related to climate change
    climate_keywords = [
        "climate", "global warming", "emission", "carbon", "greenhouse", "environment",
        "sustainability", "pollution", "renewable", "ecology", "conservation", "biodiversity",
        "fossil fuels", "deforestation", "recycling", "solar", "wind energy", "eco-friendly"
    ]
    # Filter comments to include only those with climate change keywords
    filtered_comments = []
    for comment in comments:
        if any(keyword in comment.lower() for keyword in climate_keywords):
            filtered_comments.append(comment)

    # Combine filtered comments into a single string
    text = " ".join(filtered_comments)
    # Define a set of stop words to be excluded from the word cloud
    custom_stopwords = set(STOPWORDS)
    additional_stopwords = {"will", "one", "now", "use", "also", "like", "say", "make", "https", "due",
                            "get", "go", "going", "know", "see", "want", "think", "take", "need", "look"} 
    custom_stopwords.update(additional_stopwords)

    # Create a word cloud instance with your custom configurations
    wordcloud = WordCloud(
        width=800, 
        height=600, 
        stopwords=custom_stopwords,
        background_color="white",
    ).generate(text)

    # Display the word cloud using matplotlib
    plt.figure(figsize=(10, 8))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis("off")
    plt.savefig(os.path.join(IMAGES_PATH, 'word_cloud.png'))


def plot_monthly_temperature_anomalies(year: int):
    df_Temperature = process_Temperature_data(DATA_PATH)
    year_data = df_Temperature[df_Temperature["Year"] == year]
    year_data = year_data[year_data["Country"].isin(SPECIFIED_COUNTRIES)]
    fig, ax = plt.subplots(figsize=(20, 8))

    # Plotting for each country
    for country in SPECIFIED_COUNTRIES:
        country_data = year_data[year_data["Country"] == country]
        ax.plot(country_data["Month"], country_data["Monthly Anomaly"], label=country)

    # Calculate 2-year rolling average and 95% uncertainty
    year_data_grouped = year_data.groupby('Month').agg({'Monthly Anomaly': 'mean', 'Monthly Uncertainty': 'mean'})
    year_data_grouped['Rolling Avg'] = year_data_grouped['Monthly Anomaly'].rolling(window=2, min_periods=1).mean()
    year_data_grouped['Upper Bound'] = year_data_grouped['Rolling Avg'] + 1.96 * year_data_grouped['Monthly Uncertainty']
    year_data_grouped['Lower Bound'] = year_data_grouped['Rolling Avg'] - 1.96 * year_data_grouped['Monthly Uncertainty']

    # Plot the 2-year rolling average
    ax.plot(year_data_grouped.index, year_data_grouped['Rolling Avg'], label='2-Year Avg', color='black', linestyle='--')

    # Plot the 95% uncertainty range
    ax.fill_between(year_data_grouped.index, year_data_grouped['Lower Bound'], year_data_grouped['Upper Bound'], color='gray', alpha=0.3)
    ax.set_xticks(range(1, 13))
    ax.set_xticklabels(['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'])
    ax.set_xlabel("Month")
    ax.set_ylabel("Temperature Anomalies")
    ax.legend(bbox_to_anchor=(1.02, 1))
    ax.set_title(f"Monthly Temperature Anomalies in {year}")
    plt.savefig(os.path.join(IMAGES_PATH, f'temperature_anomalies_{year}.png'))

    return fig

def plot_monthly_carbon_emissions(year: int):
    df_Carbon = process_Carbon_data(DATA_PATH)
    year_data = df_Carbon[df_Carbon["Year"] == year]
    year_data = year_data[year_data["Country"].isin(SPECIFIED_COUNTRIES)]

    # Aggregate emissions across all sectors for each country and month
    aggregated_data = year_data.groupby(["Month", "Country"])["Value"].sum().reset_index()

    # Determine the number of countries and create a bar width
    num_countries = len(SPECIFIED_COUNTRIES)
    bar_width = 0.8 / num_countries  # The width of the bars

    # Set position of bar on X axis
    r = np.arange(1, 13)
    positions = [r + i*bar_width for i in range(num_countries)]

    fig, ax = plt.subplots(figsize=(20, 8))
    
    for idx, country in enumerate(SPECIFIED_COUNTRIES):
        country_data = aggregated_data[aggregated_data["Country"] == country]
        ax.bar(positions[idx], country_data["Value"], width=bar_width, label=country, align='center')

    # Add xticks on the middle of the group bars
    ax.set_xlabel('Month', fontweight='bold')
    ax.set_xticks(r + bar_width * (num_countries / 2 - 0.5))
    ax.set_xticklabels(['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'])
    ax.set_ylabel('Carbon Emissions')
    ax.legend()

    # Create labels
    ax.set_title(f'Total Monthly Carbon Emissions for {year}')

    # Show the figure
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(os.path.join(IMAGES_PATH, f'carbon_emissions_{year}.png'))
    return fig

def plot_disaster_frequency(year: int):
    df_Disaster = process_Disaster_data(DATA_PATH, SPECIFIED_COUNTRIES, 'ROW', 'WORLD')

    # Filter the disaster data for the specified year
    yearly_data = df_Disaster[df_Disaster['Year'] == year]
    # Group the data by country and count the frequency of disasters
    disaster_frequency = yearly_data.groupby('Country').size().reset_index(name='Frequency')

    world = gpd.read_file(gpd.datasets.get_path('naturalearth_lowres'))
    
    # renaming of "United States of America" to "United States" and "Russian Federation" to "Russia"
    world['name'] = world['name'].replace({'United States of America': 'United States', 
                                            'Russian Federation': 'Russia'})

    # Merge the world GeoDataFrame with the disaster frequency DataFrame
    merged_gdf = world.merge(disaster_frequency, how='left', left_on='name', right_on='Country')
    merged_gdf['Frequency'] = merged_gdf['Frequency'].fillna(0)
    fig, ax = plt.subplots(1, 1, figsize=(22, 8))

    # Plot countries with frequency data
    merged_gdf[merged_gdf['Frequency'] > 0].plot(column='Frequency', ax=ax, legend=True,
                    legend_kwds={'label': "Frequency of Disasters by Country",
                                 'orientation': "vertical"})
    
    # Plot countries without frequency data in white (or any color of your choice)
    merged_gdf[merged_gdf['Frequency'] == 0].plot(ax=ax, color='white')
    # Outline all countries
    merged_gdf.boundary.plot(ax=ax, linewidth=1, color='black')

    ax.set_title(f'Frequency of Disasters in {year} the specific country', fontsize=25)
    ax.set_axis_off()
    plt.savefig(os.path.join(IMAGES_PATH, f'disaster_frequency_{year}.png'))
    return fig

def plot_sentiment_disaster_comparison(year: int):
    df_Reddit = process_Reddit_data(DATA_PATH)
    reddit_year_data = df_Reddit[df_Reddit['Year'] == year]
    sentiment_monthly = reddit_year_data.groupby(['Month', 'Comment_Sentiment']).size().unstack(fill_value=0).reindex()
    
    df_Disaster = process_Disaster_data(DATA_PATH, SPECIFIED_COUNTRIES, 'ROW', 'WORLD')
    disaster_year_data = df_Disaster[df_Disaster['Year'] == year]
    disaster_frequency_monthly = disaster_year_data.groupby('Month').size().reindex()

    fig, ax1 = plt.subplots(figsize=(14, 7))
    
    # Plot Reddit sentiment analysis results
    sentiment_monthly[['Positive', 'Negative']].plot(kind='bar', ax=ax1, width=0.4, position=1, color=['green', 'red'])
    ax1.set_xticks(range(len(sentiment_monthly))) 
    # Set the x-axis labels to the month names
    ax1.set_xticklabels(['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'])
    # Plot disaster frequency on the secondary axis
    ax2 = ax1.twinx()
    ax2.plot(ax1.get_xticks(), disaster_frequency_monthly, color='blue', marker='o', linewidth=2)

    # Set labels and titles
    ax1.set_xlabel('Month')
    ax1.set_ylabel('Reddit Sentiment Counts')
    ax2.set_ylabel('Disaster Frequency')
    plt.title(f'Sentiment Analysis vs Disaster Frequency in {year}')

    ax1.legend(['Positive Sentiment', 'Negative Sentiment'], loc='upper left')
    ax2.legend(['Disaster Frequency'], loc='upper right')
    plt.savefig(os.path.join(IMAGES_PATH, f'sentiment_disaster_comparison_{year}.png'))

    return fig

def main ():
    plot_word_cloud()
    plot_monthly_temperature_anomalies(2019)
    plot_monthly_temperature_anomalies(2020)
    plot_monthly_carbon_emissions(2019)
    plot_monthly_carbon_emissions(2020)
    plot_disaster_frequency(2019)
    plot_disaster_frequency(2020)
    plot_sentiment_disaster_comparison(2019)
    plot_sentiment_disaster_comparison(2020)

if __name__ == "__main__":
    main()