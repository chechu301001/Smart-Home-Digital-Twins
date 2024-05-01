import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd
import json
import numpy as np
import time
import seaborn as sns
import matplotlib.pyplot as plt
from statsmodels.tsa.arima.model import ARIMA
import plotly.graph_objects as go

df = pd.read_excel('./assests/datadump.xlsx')
app = dash.Dash(__name__)

# Define app layout
app.layout = html.Div([
    html.H1("Analytics Dashboard"),
    
    # Metric: Total power consumed in Room
    html.Div([
        html.H3("Total power consumed in Room:"),
        html.Div(id='total_power_consumed_room')
    ]),
    
    # Metric: Total power consumed per device
    html.Div([
        html.H3("Total power consumed per device:"),
        html.Div(id='total_power_per_device')
    ]),
    
    # Metric: Average power consumed in Room
    html.Div([
        html.H3("Average power consumed in Room:"),
        html.Div(id='average_power_room')
    ]),
    
    # Metric: Average power consumed per device
    html.Div([
        html.H3("Average power consumed per device:"),
        html.Div(id='average_power_per_device')
    ]),
    
    # Graph: Trends of Power Consumption Across Devices
    html.Div([
        html.H3("Trends of Power Consumption Across Devices:"),
        dcc.Graph(id='power_consumption_trends')
    ]),
    
    # Graph: Power Consumption Outliers
    html.Div([
        html.H3("Power Consumption Outliers:"),
        dcc.Graph(id='power_consumption_outliers')
    ]),
    
    # Graph: Peak Power Consumption Times
    html.Div([
        html.H3("Peak Power Consumption Times:"),
        dcc.Graph(id='peak_power_times')
    ]),
    
    # Graph: Device Utilization Ratio
    html.Div([
        html.H3("Device Utilization Ratio:"),
        dcc.Graph(id='device_utilization_ratio')
    ]),
    
    # Graph: Correlation between Device Parameters
    html.Div([
        html.H3("Correlation between Device Parameters:"),
        dcc.Graph(id='device_parameters_correlation')
    ]),
    
    # Graph: Energy Efficiency Analysis
    html.Div([
        html.H3("Energy Efficiency Analysis:"),
        dcc.Graph(id='energy_efficiency_analysis')
    ]),
    
    # Graph: Power Consumption When Devices were Off
    html.Div([
        html.H3("Power Consumption When Devices were Off:"),
        dcc.Graph(id='power_consumption_when_off')
    ]),
    
    # Graph: Power Consumption in Room When Devices were Off
    html.Div([
        html.H3("Power Consumption in Room When Devices were Off:"),
        dcc.Graph(id='power_consumption_room_when_off')
    ]),

    # Interval component to trigger updates
    dcc.Interval(
        id='interval-component',
        interval=10000,  # in milliseconds (10 seconds)
        n_intervals=0
    )
])

# Define callbacks to update dashboard components
@app.callback(
    Output('total_power_consumed_room', 'children'),
    Output('total_power_per_device', 'children'),
    Output('average_power_room', 'children'),
    Output('average_power_per_device', 'children'),
    Output('power_consumption_trends', 'figure'),
    Output('power_consumption_outliers', 'figure'),
    Output('peak_power_times', 'figure'),
    Output('device_utilization_ratio', 'figure'),
    Output('device_parameters_correlation', 'figure'),
    Output('energy_efficiency_analysis', 'figure'),
    Output('power_consumption_when_off', 'figure'),
    Output('power_consumption_room_when_off', 'figure'),
    Input('interval-component', 'n_intervals')
)
def update_metrics_and_graphs(n):
    # Step 4: Extract 'powerConsumed' values from 'Init Data' column
    def extract_power_consumed(init_data):
        try:
            init_data_dict = json.loads(init_data)
            return init_data_dict.get('powerConsumed', np.nan)
        except json.JSONDecodeError:
            return np.nan
    
    def extract_onOff(init_data):
        try:
            init_data_dict = json.loads(init_data)
            return init_data_dict.get('onOff', np.nan)
        except json.JSONDecodeError:
            return np.nan
    
    def extract_humidity(init_data):
        try:
            init_data_dict = json.loads(init_data)
            return init_data_dict.get('humidity', np.nan)
        except json.JSONDecodeError:
            return np.nan
    
    def extract_temperature(init_data):
        try:
            init_data_dict = json.loads(init_data)
            return init_data_dict.get('temperature', np.nan)
        except json.JSONDecodeError:
            return np.nan
    
    def extract_brightness(init_data):
        try:
            init_data_dict = json.loads(init_data)
            return init_data_dict.get('brightness', np.nan)
        except json.JSONDecodeError:
            return np.nan
    
    df['powerConsumed'] = df['Init Data'].apply(extract_power_consumed)
    df['onOff'] = df['Init Data'].apply(extract_onOff)
    df['humidity'] = df['Init Data'].apply(extract_humidity)
    df['temperature'] = df['Init Data'].apply(extract_temperature)
    df['brightness'] = df['Init Data'].apply(extract_brightness)
    
    # Metric: Total power consumed in Room
    total_power_room = df['powerConsumed'].sum()
    
    # Metric: Total power consumed per device
    total_power_per_device = df.groupby('ModelID')['powerConsumed'].sum().to_dict()
    
    # Metric: Average power consumed in Room
    average_power_room = df['powerConsumed'].mean()
    
    # Metric: Average power consumed per device
    average_power_per_device = df.groupby('ModelID')['powerConsumed'].mean().to_dict()
    
    # Graph: Trends of Power Consumption Across Devices
    fig_power_consumption_trends = px.line(df, x='Time', y='powerConsumed', color='ModelID', title='Trends of Power Consumption Across Devices')
    
    # Graph: Power Consumption Outliers
    fig_power_consumption_outliers = px.box(df, y='powerConsumed', title='Power Consumption Outliers')
    
    # Graph: Peak Power Consumption Times
    df['Time'] = pd.to_datetime(df['Time'])
    df['Hour'] = df['Time'].dt.hour
    peak_power_times = df.groupby('Hour')['powerConsumed'].sum().reset_index()
    fig_peak_power_times = px.bar(peak_power_times, x='Hour', y='powerConsumed', title='Peak Power Consumption Times')
    
    # Graph: Device Utilization Ratio
    device_utilization = df.groupby('ID (must be unique)')['onOff'].mean().sort_values(ascending=False)
    fig_device_utilization_ratio = px.bar(device_utilization, title='Device Utilization Ratio')
    
    # Graph: Correlation between Device Parameters
    device_parameters = ['temperature', 'humidity', 'brightness']
    device_corr = df[device_parameters].corr()
    fig_device_parameters_correlation = px.imshow(device_corr, title='Correlation between Device Parameters')
    
    # Graph: Energy Efficiency Analysis
    energy_efficiency = df.groupby('ID (must be unique)')['powerConsumed'].mean().sort_values(ascending=False)
    fig_energy_efficiency_analysis = px.bar(energy_efficiency, title='Energy Efficiency Analysis')
    
    # Graph: Power Consumption When Devices were Off
    off_devices = df[df['onOff'] == False]
    fig_power_consumption_when_off = px.histogram(off_devices, x='powerConsumed', title='Power Consumption When Devices were Off')
    
    # Graph: Power Consumption in Room When Devices were Off
    room_power_off = off_devices.groupby(['Date', 'Time'])['powerConsumed'].sum().reset_index()
    fig_power_consumption_room_when_off = px.line(room_power_off, x='Time', y='powerConsumed', title='Power Consumption in Room When Devices were Off')
    
    return (
        total_power_room,
        json.dumps(total_power_per_device, indent=4),
        average_power_room,
        json.dumps(average_power_per_device, indent=4),
        fig_power_consumption_trends,
        fig_power_consumption_outliers,
        fig_peak_power_times,
        fig_device_utilization_ratio,
        fig_device_parameters_correlation,
        fig_energy_efficiency_analysis,
        fig_power_consumption_when_off,
        fig_power_consumption_room_when_off
    )

if __name__ == '__main__':
    app.run_server(debug=True)
