import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import pandas as pd
import json
import time
import plotly.graph_objects as go

df = pd.read_excel('./assests/datadump.xlsx')
app = dash.Dash(__name__)

# Define app layout
app.layout = html.Div([
    html.H1("Live Analytics"),
    
    # Graph: Live AC Power Consumption
    dcc.Graph(id='live-ac-power-consumption'),
    
    # Interval component to trigger updates
    dcc.Interval(
        id='interval-component',
        interval=10000,  # in milliseconds (10 seconds)
        n_intervals=0
    )
])

# Define callback to update the live graph
@app.callback(
    Output('live-ac-power-consumption', 'figure'),
    Input('interval-component', 'n_intervals')
)
def update_live_graph(n):

    df = pd.read_excel('./assests/datadump.xlsx')

    ac_df = df[df['ModelID'] == 'dtmi:example:AC;1'].copy()
    
    # Parse 'Init Data' column to extract 'powerConsumed' values
    ac_df['powerConsumed'] = ac_df['Init Data'].apply(lambda x: json.loads(x)['powerConsumed'])
    
    # Create a new DataFrame with index and 'powerConsumed' values for AC
    ac_power_df = pd.DataFrame(ac_df['powerConsumed'].values, columns=['AC_Power_Consumption'])
    ac_power_df.index = ac_power_df.index + 1
    
    # Plot the live graph using Plotly
    live_graph = go.Figure()
    live_graph.add_trace(go.Scatter(x=ac_power_df.index, y=ac_power_df['AC_Power_Consumption'], mode='lines', name='Original Data'))
    live_graph.update_layout(title='Live AC Power Consumption',
                             xaxis_title='Index',
                             yaxis_title='AC Power Consumption')
    
    return live_graph

if __name__ == '__main__':
    app.run_server(debug=True, port=5000)
