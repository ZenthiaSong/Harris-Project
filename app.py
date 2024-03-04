from shiny import App, render, ui
from plotting import (
    plot_monthly_temperature_anomalies, 
    plot_monthly_carbon_emissions, 
    plot_disaster_frequency, 
    plot_sentiment_disaster_comparison)

app_ui = ui.page_fluid(
    ui.tags.header(
        ui.tags.img(src="https://harris.uchicago.edu/files/harris_wide.png", style="width: 450px;"),
        ui.tags.h1("Analyzing Climate Change Impacts and Public Perception", style="text-align: center; font-size: 30px;"),
        style="display: flex; align-items: baseline; margin: 10px 0px 0px 10px"
    ),
    ui.layout_sidebar(
        ui.panel_sidebar(

            ui.markdown("**Name:** Zenthia Song and Shuyi Zhang"),
            ui.markdown("**Program:** MACSS"),
            ui.markdown("**Quarter:** Fall 2023"),
            ui.markdown("**Course:** PPHA 30538: Data and Programming for Public Policy II"),
            ui.markdown("**Assignment:** Final Project"),

            ui.input_radio_buttons("year", "Year", [2019, 2020]),
        ),
        ui.navset_tab(
            ui.nav("Temperature Anomalies", ui.output_plot(id="monthly_temperature_anomalies")),
            ui.nav("Carbon Emissions", ui.output_plot(id="monthly_carbon_emissions")),
            ui.nav("Disaster Frequency", ui.output_plot(id="disaster_frequency")),
            ui.nav("Sentiment Comparison", ui.output_plot(id="sentiment_disaster_comparison")),
        )
    )
)

def server(input, output, session):
    @output
    @render.plot
    def monthly_temperature_anomalies():
        year = int(input.year())
        plot_monthly_temperature_anomalies(year)

    @output
    @render.plot
    def monthly_carbon_emissions():
        year = int(input.year())
        plot_monthly_carbon_emissions(year)

    @output
    @render.plot
    def disaster_frequency():
        year = int(input.year())
        plot_disaster_frequency(year)

    @output
    @render.plot
    def sentiment_disaster_comparison():
        year = int(input.year())
        plot_sentiment_disaster_comparison(year)

app = App(app_ui, server)
