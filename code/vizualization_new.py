import dash
from dash import html, dcc
import plotly.express as px
import plotly.graph_objects as go
import json
import pandas as pd
from shapely.geometry import shape
import numpy as np

# Initialize the Dash app
app = dash.Dash(__name__)

# State colors for points
state_colors = {
    'NSW': '#FF3D00',     # Bright orange-red
    'WA': '#2196F3',      # Bright blue
    'QLD': '#AA00FF',     # Bright purple
    'VIC': '#00E676',     # Bright green
    'SA': '#FFEB3B',      # Bright yellow
    'TAS': '#FF1744',     # Bright pink-red
    'NT': '#18FFFF',      # Bright cyan
}

# Read and clean the data
df = pd.read_csv('cleaned_data.csv')

def clean_coordinate(coord):
    if pd.isna(coord):
        return None
    try:
        coord_str = str(coord)
        cleaned = ''.join(c for c in coord_str if c.isdigit() or c in '.-')
        return float(cleaned)
    except Exception:
        return None

df['Latitude'] = df['Latitude'].apply(clean_coordinate)
df['Longitude'] = df['Longitude'].apply(clean_coordinate)
df = df.dropna(subset=['Latitude', 'Longitude'])

# Create hover text
df['hover_text'] = df.apply(lambda row: f"""
<b>Year:</b> {int(row['Year']) if pd.notnull(row['Year']) else 'Unknown'}<br>
<b>Shark Species:</b> {row['SharkName'] if pd.notnull(row['SharkName']) else 'Unknown'}<br>
<b>Activity:</b> {row['Activity'] if pd.notnull(row['Activity']) else 'Unknown'}<br>
<b>Injury:</b> {row['Injury'] if pd.notnull(row['Injury']) else 'Unknown'}<br>
<b>Gender:</b> {row['Gender'] if pd.notnull(row['Gender']) else 'Unknown'}<br>
<b>Age:</b> {int(row['Age']) if pd.notnull(row['Age']) else 'Unknown'}
""", axis=1)

# Read the GeoJSON file
with open('states.geojson') as f:
    australia_states = json.load(f)

# Calculate centroids for state labels
state_centroids = {}
for feature in australia_states['features']:
    state_name = feature['properties']['STATE_NAME']
    geometry = shape(feature['geometry'])
    centroid = geometry.centroid
    state_centroids[state_name] = {'lat': centroid.y, 'lon': centroid.x}

# Create the base map
fig = px.choropleth_mapbox(
    geojson=australia_states,
    #locations=[feat['properties']['STATE_NAME'] for feat in australia_states['features']],
    featureidkey="properties.STATE_NAME",
    center={"lat": -28.2744, "lon": 128.7751},
    mapbox_style="carto-darkmatter",
    zoom=3.7,
    opacity=0,
    hover_data=None
)

# Initialize empty layers list
mapbox_layers = [{
    'sourcetype': 'geojson',
    'source': australia_states,
    'type': 'line',
    'below': "traces",
    'line': {'width': 1},
    'color': '#FFFFFF',
    'opacity': 0.5
}]

# Add shark attack points by state with hover information
for state in df['State'].unique():
    state_data = df[df['State'] == state]
    if state in state_colors:
        fig.add_scattermapbox(
            lat=state_data['Latitude'],
            lon=state_data['Longitude'],
            mode='markers',
            marker=dict(
                size=8,
                color=state_colors[state],
                symbol='circle',
                opacity=0.8
            ),
            name=state,
            text=state_data['hover_text'],
            hoverinfo='text',
            hoverlabel=dict(
                bgcolor='#121212',
                bordercolor='#36def7',
                font=dict(color='white', size=12)
            ),
            showlegend=False
        )

# Add state labels
for state, centroid in state_centroids.items():
    fig.add_scattermapbox(
        lat=[centroid['lat']],
        lon=[centroid['lon']],
        mode='text',
        text=[state],
        textfont=dict(size=12, color='white'),
        hoverinfo='none',
        showlegend=False
    )

# Update the map layout
fig.update_layout(
    margin={"r": 0, "t": 0, "l": 0, "b": 0},
    paper_bgcolor='#121212',
    plot_bgcolor='#121212',
    mapbox=dict(
        zoom=3.3,
        style='carto-darkmatter',
        layers=mapbox_layers
    ),
    showlegend=False
)

# Create statistics figures (keeping the same as in original code)
def create_attacks_by_state():
    attacks_by_state = df['State'].value_counts()
    stats_fig = go.Figure()
    stats_fig.add_trace(go.Bar(
        x=attacks_by_state.index,
        y=attacks_by_state.values,
        marker_color=[state_colors.get(state, '#808080') for state in attacks_by_state.index]
    ))
    stats_fig.update_layout(
        title='Attacks by State',
        paper_bgcolor='#121212',
        plot_bgcolor='#121212',
        font=dict(color='white'),
        margin=dict(l=10, r=10, t=40, b=10),
        height=200,
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=True, gridcolor='#333333')
    )
    return stats_fig

def create_yearly_trend():
    yearly_attacks = df['Year'].value_counts().sort_index()
    stats_fig = go.Figure()
    stats_fig.add_trace(go.Scatter(
        x=yearly_attacks.index,
        y=yearly_attacks.values,
        mode='lines+markers',
        line=dict(color='#688ae8')
    ))
    stats_fig.update_layout(
        title='Yearly Trend of Attacks',
        paper_bgcolor='#121212',
        plot_bgcolor='#121212',
        font=dict(color='white'),
        margin=dict(l=10, r=10, t=40, b=10),
        height=200,
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=True, gridcolor='#333333')
    )
    return stats_fig

def create_activity_distribution():
    top_activities = df['Activity'].value_counts().head(8)
    stats_fig = go.Figure()
    stats_fig.add_trace(go.Bar(
        x=top_activities.values,
        y=top_activities.index,
        orientation='h',
        marker_color='#688ae8'
    ))
    stats_fig.update_layout(
        title='Most Common Activities',
        paper_bgcolor='#121212',
        plot_bgcolor='#121212',
        font=dict(color='white'),
        margin=dict(l=10, r=10, t=40, b=10),
        height=300,
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=False)
    )
    return stats_fig

def create_shark_species():
    top_sharks = df['SharkName'].value_counts().head(5)
    stats_fig = go.Figure()
    stats_fig.add_trace(go.Pie(
        labels=top_sharks.index,
        values=top_sharks.values,
        hole=0.4,
        marker=dict(colors=px.colors.sequential.Plasma)
    ))
    stats_fig.update_layout(
        title='Top Shark Species',
        paper_bgcolor='#121212',
        plot_bgcolor='#121212',
        font=dict(color='white'),
        margin=dict(l=10, r=10, t=40, b=10),
        height=250,
        showlegend=False
    )
    return stats_fig

# Define the app layout
app.layout = html.Div([
    # Left side panel for statistics (fixed)
    html.Div([
        html.Div([
            html.Div(style={'height': '20px'}),
            dcc.Graph(figure=create_attacks_by_state(), 
                     config={'displayModeBar': False}),
            dcc.Graph(figure=create_yearly_trend(), 
                     config={'displayModeBar': False}),
            dcc.Graph(figure=create_activity_distribution(), 
                     config={'displayModeBar': False}),
            dcc.Graph(figure=create_shark_species(), 
                     config={'displayModeBar': False}),
            html.Div([
                html.H3('Quick Facts', 
                       style={'color': '#688ae8', 'marginTop': '20px'}),
                html.P(f"Total recorded attacks: {len(df)}", 
                      style={'color': 'white'}),
                html.P(f"Year range: {df['Year'].min()} - {df['Year'].max()}", 
                      style={'color': 'white'}),
                html.P(f"Most dangerous state: {df['State'].mode().iloc[0]}", 
                      style={'color': 'white'}),
                html.P(f"Most common shark: {df['SharkName'].mode().iloc[0]}", 
                      style={'color': 'white'}),
            ], style={'padding': '10px'})
        ], style={
            'overflowY': 'auto',
            'height': '100vh',
            'margin': '20px',
            'width': 'calc(100% - 40px)'
        })
    ], style={
        'position': 'fixed',
        'left': '0',
        'top': '0',
        'width': '500px',
        'height': '100vh',
        'backgroundColor': '#121212',
        'overflowY': 'auto',
        'zIndex': '1000'
    }),

    # Main map
    html.Div([
        dcc.Graph(
            figure=fig,
            style={'height': '100vh', 'width': '100%'},
            config={'displayModeBar': False, 'scrollZoom': True}
        )
    ], style={
        'marginLeft': '500px',
        'height': '100vh'
    })
])

# Add CSS
app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>Australian Shark Attack Analysis</title>
        {%favicon%}
        {%css%}
        <style>
            body {
                margin: 0;
                padding: 0;
                overflow: hidden;
                background-color: #121212;
            }
            .mapboxgl-canvas {
                position: absolute;
                top: 0;
                bottom: 0;
                left: 0;
                right: 0;
                pointer-events: auto !important;
            }
            ::-webkit-scrollbar {
                width: 8px;
            }
            ::-webkit-scrollbar-track {
                background: #121212;
            }
            ::-webkit-scrollbar-thumb {
                background: #36def7;
                border-radius: 4px;
            }
            ::-webkit-scrollbar-thumb:hover {
                background: #2ba7b9;
            }
        </style>
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
'''

if __name__ == '__main__':
    app.run_server(debug=True)