import pandas as pd
import statsmodels.api as sm
from const import DATA_PATH, SPECIFIED_COUNTRIES
from data_process import (
    process_Carbon_data,
    process_Disaster_data,
    process_Temperature_data,
)

class Analysis:
    def __init__(self, path=DATA_PATH):
        self.df_Carbon = process_Carbon_data(path)
        self.df_Temperature = process_Temperature_data(path)
        self.df_Disaster = process_Disaster_data(
            DATA_PATH, SPECIFIED_COUNTRIES, "ROW", "WORLD"
        )

    def prepare_data_for_analysis(self):
        # Filter for 'WORLD' country
        df_Disaster_World = self.df_Disaster[self.df_Disaster["Country"] != "WORLD"]
        df_Carbon_World = self.df_Carbon[self.df_Carbon["Country"] == "WORLD"]
        df_Temperature_World = self.df_Temperature[
            self.df_Temperature["Country"] == "WORLD"
        ]

        # Count the number of disasters per month for each year
        df_Disaster_Count = (
            df_Disaster_World.groupby(["Year", "Month"])
            .size()
            .reset_index(name="Disaster Count")
        )
        df_Carbon_Count = (
            df_Carbon_World.groupby(["Year", "Month"])
            .agg({"Value": "sum"})
            .reset_index()
        )
        df_Temperature_Count = (
            df_Temperature_World.groupby(["Year", "Month"])
            .agg({"Monthly Anomaly": "mean"})
            .reset_index()
        )

        return df_Disaster_Count, df_Carbon_Count, df_Temperature_Count

    # Utility function to extract and format regression results
    @staticmethod
    def format_regression_results(model):
        results_df = pd.DataFrame({
            "Coefficient": model.params.round(4),
            "Std Error": model.bse.round(4),
            "t Value": model.tvalues.round(4),
            "P>|t|": model.pvalues.round(4)
        })
        results_df['Significance'] = results_df['P>|t|'].apply(lambda x: '*' if x < 0.05 else '')
        return results_df
    
    # Linear Regression Analysis for Monthly Carbon Emissions and Temperature Anomalies
    @staticmethod
    def perform_monthly_regression_analysis(df_Carbon_Count, df_Temperature_Count):
        results = {}

        merged_data = pd.merge(df_Carbon_Count, df_Temperature_Count, on=["Year", "Month"])

        for year in [2019, 2020]:
            yearly_data = merged_data[merged_data["Year"] == year]

            X = yearly_data["Value"]  # CO2 Emissions
            y = yearly_data["Monthly Anomaly"]  # Temperature Anomalies
            X = sm.add_constant(X)
            model = sm.OLS(y, X).fit()

            results[year] = Analysis.format_regression_results(model)

        return results

    # Linear Regression Analysis for Monthly Carbon Emissions and Disaster Count
    @staticmethod
    def perform_disaster_co2_regression_analysis(df_Disaster_Count, df_Carbon_Count):
        results = {}

        merged_data = pd.merge(df_Disaster_Count, df_Carbon_Count, on=["Year", "Month"])

        for year in [2019, 2020]:
            yearly_data = merged_data[merged_data["Year"] == year]

            X = yearly_data["Disaster Count"]  # Number of Disasters
            y = yearly_data["Value"]  # CO2 Emissions
            X = sm.add_constant(X)
            model = sm.OLS(y, X).fit()

            results[year] = Analysis.format_regression_results(model)

        return results

    # Multiple Linear Regression Analysis for Monthly Carbon Emissions, Temperature Anomalies, and Disaster Count
    @staticmethod
    def perform_multiple_regression_analysis(df_Disaster_Count, df_Carbon_Count, df_Temperature_Count):
        results = {}

        merged_data = pd.merge(df_Disaster_Count, df_Carbon_Count, on=["Year", "Month"])
        merged_data = pd.merge(merged_data, df_Temperature_Count, on=["Year", "Month"])

        for year in [2019, 2020]:
            yearly_data = merged_data[merged_data["Year"] == year]

            X = yearly_data[["Disaster Count", "Monthly Anomaly"]]  # Number of Disasters and Temperature Anomalies
            y = yearly_data["Value"]  # CO2 Emissions
            X = sm.add_constant(X)
            model = sm.OLS(y, X).fit()

            results[year] = Analysis.format_regression_results(model)

        return results


if __name__ == "__main__":
    analysis = Analysis(DATA_PATH)
    (
        df_Disaster_Count,
        df_Carbon_Count,
        df_Temperature_Count,
    ) = analysis.prepare_data_for_analysis()

    # Perform regression analysis and print formatted results for 2019 and 2020
    regression_results = analysis.perform_monthly_regression_analysis(
        df_Carbon_Count, df_Temperature_Count
    )
    for year, result in regression_results.items():
        print(f"Monthly Regression Results for the Year {year}:\n", result, "\n")

    # Perform and print regression results for Disaster and CO2
    regression_results = analysis.perform_disaster_co2_regression_analysis(
        df_Disaster_Count, df_Carbon_Count
    )
    for year, result in regression_results.items():
        print(f"Disaster-CO2 Regression Results for the Year {year}:\n", result, "\n")

    # Perform and print multiple regression results
    regression_results = analysis.perform_multiple_regression_analysis(
        df_Disaster_Count, df_Carbon_Count, df_Temperature_Count
    )
    for year, result in regression_results.items():
        print(f"Multiple Regression Results for the Year {year}:\n", result, "\n")
