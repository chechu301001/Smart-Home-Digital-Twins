import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.graph_objects as go
import pandas as pd
import json
import time
import numpy as np
from statsmodels.tsa.arima.model import ARIMA
import matplotlib.pyplot as plt
from flask import Flask  

df = pd.read_excel('./assests/datadump.xlsx')
server = Flask(__name__)  # Initialize Flask app

# Define Dash app
app = dash.Dash(__name__, server=server)  # Connect Dash to Flask app

app.layout = html.Div([
    html.H1("Forecasting Dashboard"),
    
    # Graph: Forecast for AC Power Consumption
    html.Div([
        html.H3("Forecast for AC Power Consumption:"),
        dcc.Graph(id='ac_power_forecast')
    ]),
    
    # Graph: Forecast for Temperature
    html.Div([
        html.H3("Temperature Forecast:"),
        dcc.Graph(id='temperature_forecast')
    ]),
    
    # Graph: Forecast for Energy Cost
    html.Div([
        html.H3("Forecast for Energy Cost:"),
        dcc.Graph(id='energy_cost_forecast')
    ]),
    
    # Interval component to trigger updates
    dcc.Interval(
        id='interval-component',
        interval=10000,  # in milliseconds (10 seconds)
        n_intervals=0
    )
])

# Define function to extract 'powerConsumed' values
def extract_power_consumed(init_data):
    try:
        init_data_dict = json.loads(init_data)
        return init_data_dict.get('powerConsumed', np.nan)
    except json.JSONDecodeError:
        return np.nan

# Define function to extract temperature values
def extract_temperature(init_data):
    try:
        init_data_dict = json.loads(init_data)
        return init_data_dict.get('temperature', np.nan)
    except json.JSONDecodeError:
        return np.nan

# Apply function to extract 'powerConsumed' values
df['powerConsumed'] = df['Init Data'].apply(extract_power_consumed)

# Apply function to extract temperature values
df['temperature'] = df['Init Data'].apply(extract_temperature)

# Extract data for the AC device
ac_df = df[df['ModelID'] == 'dtmi:example:Room;1'].copy()

# Parse 'Init Data' column to extract 'powerConsumed' values
ac_df['powerConsumed'] = ac_df['Init Data'].apply(lambda x: json.loads(x)['powerConsumed'])

# Create a new DataFrame with index and 'powerConsumed' values for AC
ac_power_df = pd.DataFrame(ac_df['powerConsumed'].values, columns=['AC_Power_Consumption'])

# Set the index starting from 1
ac_power_df.index = ac_power_df.index + 1

# Define ARIMA model for AC power consumption
ac_model = ARIMA(ac_power_df['AC_Power_Consumption'], order=(2, 2, 2))

# Fit the ARIMA model
ac_model_fit = ac_model.fit()

# Forecast next 10 values for AC power consumption
ac_forecast = ac_model_fit.forecast(steps=10)

# Define ARIMA model for temperature
temperature_model = ARIMA(df['temperature'], order=(2, 2, 2))

# Fit the ARIMA model
temperature_model_fit = temperature_model.fit()

# Forecast next 10 values for temperature
temperature_forecast = temperature_model_fit.forecast(steps=10)

# Define ARIMA model for AC power consumption (for energy cost)
ac_energy_cost_model = ARIMA(ac_power_df['AC_Power_Consumption'], order=(2, 2, 2))

# Fit the ARIMA model
ac_energy_cost_model_fit = ac_energy_cost_model.fit()

# Forecast next 10 values for AC power consumption (for energy cost)
ac_energy_cost_forecast = ac_energy_cost_model_fit.forecast(steps=10)

# Calculate energy cost forecast assuming a rate of $0.2 per unit of power consumption
energy_cost_forecast = ac_energy_cost_forecast * 0.2

# Define callback to update forecast graphs
@app.callback(
    Output('ac_power_forecast', 'figure'),
    Output('temperature_forecast', 'figure'),
    Output('energy_cost_forecast', 'figure'),
    Input('interval-component', 'n_intervals')
)
def update_forecast(n):
    # Plot AC power consumption forecast
    ac_fig = go.Figure()
    ac_fig.add_trace(go.Scatter(x=ac_power_df.index, y=ac_power_df['AC_Power_Consumption'], mode='lines', name='Original Data'))
    ac_fig.add_trace(go.Scatter(x=np.arange(ac_power_df.index[-1] + 1, ac_power_df.index[-1] + 11), y=ac_forecast, mode='markers+lines', name='Forecast', line=dict(color='red')))
    ac_fig.update_layout(title='Forecast for AC Power Consumption', xaxis_title='Index', yaxis_title='AC Power Consumption')

    # Plot temperature forecast
    temperature_fig = go.Figure()
    temperature_fig.add_trace(go.Scatter(x=df.index, y=df['temperature'], mode='lines', name='Original Data'))
    temperature_fig.add_trace(go.Scatter(x=np.arange(df.index[-1] + 1, df.index[-1] + 11), y=temperature_forecast, mode='markers+lines', name='Forecast', line=dict(color='red')))
    temperature_fig.update_layout(title='Temperature Forecast', xaxis_title='Index', yaxis_title='Temperature')

    # Plot energy cost forecast
    energy_cost_fig = go.Figure()
    energy_cost_fig.add_trace(go.Scatter(x=np.arange(ac_power_df.index[-1] + 1, ac_power_df.index[-1] + 11), y=energy_cost_forecast, mode='markers+lines', name='Energy Cost Forecast', line=dict(color='green')))
    energy_cost_fig.update_layout(title='Forecast for Energy Cost', xaxis_title='Index', yaxis_title='Energy Cost')

    return ac_fig, temperature_fig, energy_cost_fig

if __name__ == '__main__':
    server.run(debug=True, port=8000)  
