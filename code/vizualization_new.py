import dash
from dash import html, dcc
from dash.dependencies import Input, Output, State
import plotly.express as px
import plotly.graph_objects as go
import json
import pandas as pd
from shapely.geometry import shape
import numpy as np

# Initialize the Dash app with callback exception suppression
app = dash.Dash(__name__, suppress_callback_exceptions=True)

# State colors and mapping
state_colors = {
    'NSW': '#FF3D00',
    'WA': '#2196F3',
    'QLD': '#AA00FF',
    'VIC': '#00E676',
    'SA': '#FFEB3B',
    'TAS': '#FF1744',
    'NT': '#18FFFF',
}

# Mapping between short and long state names
state_name_mapping = {
    'NSW': 'New South Wales',
    'VIC': 'Victoria',
    'QLD': 'Queensland',
    'WA': 'Western Australia',
    'SA': 'South Australia',
    'TAS': 'Tasmania',
    'NT': 'Northern Territory',
    'ACT': 'Australian Capital Territory'
}

reverse_state_mapping = {v: k for k, v in state_name_mapping.items()}

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

def filter_data_by_states(df, selected_states):
    """Helper function to filter data based on selected states"""
    if not selected_states:  # If no states selected, show all data
        return df
    # Convert long state names to short names for filtering
    selected_short_states = [reverse_state_mapping[state] for state in selected_states]
    return df[df['State'].isin(selected_short_states)]

def create_map(selected_states=None, camera_position=None):
    if selected_states is None:
        selected_states = []
        
    if camera_position is None:
        camera_position = {
            'center': {"lat": -28.2744, "lon": 128.7751},
            'zoom': 3.3
        }
    
    # Create base figure
    fig = go.Figure()

    # Add choropleth layer for unselected states (base layer)
    fig.add_trace(go.Choroplethmapbox(
        geojson=australia_states,
        locations=[feat['properties']['STATE_NAME'] for feat in australia_states['features']],
        z=[1] * len(australia_states['features']),
        featureidkey="properties.STATE_NAME",
        colorscale=[[0, 'rgba(255,255,255,0)'], [1, 'rgba(255,255,255,0)']],
        showscale=False,
        hovertemplate=None,
        hoverinfo='none',
        marker_line_width=1,
        marker_line_color='white'
    ))

    # Add choropleth layer for selected states
    if selected_states:
        z_selected = [1 if feat['properties']['STATE_NAME'] in selected_states else 0 
                     for feat in australia_states['features']]
        
        fig.add_trace(go.Choroplethmapbox(
            geojson=australia_states,
            locations=[feat['properties']['STATE_NAME'] for feat in australia_states['features']],
            z=z_selected,
            featureidkey="properties.STATE_NAME",
            colorscale=[[0, 'rgba(101,194,255,0)'], [1, 'rgba(101,194,255,0.2)']],
            showscale=False,
            hovertemplate=None,
            hoverinfo='none',
            marker_line_width=1,
            marker_line_color='white'
        ))

    # Add shark attack points
    for state in df['State'].unique():
        if state in state_colors:
            state_data = df[df['State'] == state]
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

    # Update layout
    fig.update_layout(
        margin={"r": 0, "t": 0, "l": 0, "b": 0},
        paper_bgcolor='#121212',
        plot_bgcolor='#121212',
        mapbox=dict(
            style='carto-darkmatter',
            center=camera_position['center'],
            zoom=camera_position['zoom']
        ),
        showlegend=False
    )
    
    return fig

def create_attacks_by_state(df, selected_states=None):
    filtered_df = filter_data_by_states(df, selected_states)
    attacks_by_state = filtered_df['State'].value_counts()
    
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=attacks_by_state.index,
        y=attacks_by_state.values,
        marker_color=[state_colors.get(state, '#808080') for state in attacks_by_state.index],
        text=attacks_by_state.values,
        textposition='auto',
    ))
    
    fig.update_layout(
        title='Attacks by State',
        paper_bgcolor='#121212',
        plot_bgcolor='#121212',
        font=dict(color='white'),
        margin=dict(l=10, r=10, t=40, b=10),
        height=200,
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=True, gridcolor='#333333')
    )
    return fig

def create_yearly_trend(df, selected_states=None):
    filtered_df = filter_data_by_states(df, selected_states)
    yearly_attacks = filtered_df['Year'].value_counts().sort_index()
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=yearly_attacks.index,
        y=yearly_attacks.values,
        mode='lines+markers',
        line=dict(color='#688ae8'),
        hovertemplate='Year: %{x}<br>Attacks: %{y}<extra></extra>'
    ))
    
    fig.update_layout(
        title='Yearly Trend of Attacks',
        paper_bgcolor='#121212',
        plot_bgcolor='#121212',
        font=dict(color='white'),
        margin=dict(l=10, r=10, t=40, b=10),
        height=200,
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=True, gridcolor='#333333')
    )
    return fig

def create_activity_distribution(df, selected_states=None):
    filtered_df = filter_data_by_states(df, selected_states)
    top_activities = filtered_df['Activity'].value_counts().head(8)
    
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=top_activities.values,
        y=top_activities.index,
        orientation='h',
        marker_color='#688ae8',
        text=top_activities.values,
        textposition='auto',
    ))
    
    fig.update_layout(
        title='Most Common Activities',
        paper_bgcolor='#121212',
        plot_bgcolor='#121212',
        font=dict(color='white'),
        margin=dict(l=10, r=10, t=40, b=10),
        height=300,
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=False)
    )
    return fig

def create_shark_species(df, selected_states=None):
    filtered_df = filter_data_by_states(df, selected_states)
    top_sharks = filtered_df['SharkName'].value_counts().head(5)
    
    fig = go.Figure()
    fig.add_trace(go.Pie(
        labels=top_sharks.index,
        values=top_sharks.values,
        hole=0.4,
        marker=dict(colors=px.colors.sequential.Plasma),
        textinfo='label+percent',
        hoverinfo='label+value'
    ))
    
    fig.update_layout(
        title='Top Shark Species',
        paper_bgcolor='#121212',
        plot_bgcolor='#121212',
        font=dict(color='white'),
        margin=dict(l=10, r=10, t=40, b=10),
        height=250,
        showlegend=False
    )
    return fig

def get_quick_facts(df, selected_states=None):
    filtered_df = filter_data_by_states(df, selected_states)
    
    return {
        'total_attacks': len(filtered_df),
        'year_range': f"{filtered_df['Year'].min()} - {filtered_df['Year'].max()}",
        'most_dangerous_state': filtered_df['State'].mode().iloc[0] if not filtered_df.empty else 'N/A',
        'most_common_shark': filtered_df['SharkName'].mode().iloc[0] if not filtered_df.empty else 'N/A'
    }

# Define the app layout
app.layout = html.Div([
    # Store components
    dcc.Store(id='selected-states', data=[]),
    dcc.Store(id='camera-position', data={
        'center': {"lat": -28.2744, "lon": 128.7751},
        'zoom': 3.3
    }),
    
    # Left side panel for statistics
    html.Div([
        html.Div([
            html.H3('Australian Shark Attacks', 
                   style={'color': '#688ae8', 'marginBottom': '20px'}),
            dcc.Graph(
                id='attacks-by-state',
                config={'displayModeBar': False}
            ),
            dcc.Graph(
                id='yearly-trend',
                config={'displayModeBar': False}
            ),
            dcc.Graph(
                id='activity-distribution',
                config={'displayModeBar': False}
            ),
            dcc.Graph(
                id='shark-species',
                config={'displayModeBar': False}
            ),
            html.Div(id='quick-facts', style={'padding': '10px', 'color': 'white'})
        ], style={
            'padding': '20px',
            'backgroundColor': '#121212'
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
            id='australia-map',
            figure=create_map(),
            style={'height': '100vh', 'width': '100%'},
            config={'displayModeBar': False, 'scrollZoom': True}
        )
    ], style={
        'marginLeft': '500px',
        'height': '100vh'
    })
])

# Map callback
@app.callback(
    Output('selected-states', 'data'),
    Output('australia-map', 'figure'),
    Output('camera-position', 'data'),
    Input('australia-map', 'clickData'),
    Input('australia-map', 'relayoutData'),
    State('selected-states', 'data'),
    State('camera-position', 'data')
)
def update_selected_states(click_data, relayout_data, selected_states, camera_position):
    ctx = dash.callback_context
    triggered_id = ctx.triggered[0]['prop_id'].split('.')[1] if ctx.triggered else None
    
    if not selected_states:
        selected_states = []
    
    # Update camera position if the map was moved/zoomed
    if triggered_id == 'relayoutData' and relayout_data:
        if 'mapbox.center' in relayout_data:
            camera_position['center'] = relayout_data['mapbox.center']
        if 'mapbox.zoom' in relayout_data:
            camera_position['zoom'] = relayout_data['mapbox.zoom']
        return selected_states, create_map(selected_states, camera_position), camera_position

    # Handle state selection
    if click_data:
        clicked_point = click_data['points'][0]
        if 'location' in clicked_point:
            clicked_state = clicked_point['location']
            if clicked_state in selected_states:
                selected_states.remove(clicked_state)
            else:
                selected_states.append(clicked_state)
    
    return selected_states, create_map(selected_states, camera_position), camera_position

# Graphs callback
@app.callback(
    [Output('attacks-by-state', 'figure'),
     Output('yearly-trend', 'figure'),
     Output('activity-distribution', 'figure'),
     Output('shark-species', 'figure'),
     Output('quick-facts', 'children')],
    [Input('selected-states', 'data')]
)
def update_graphs(selected_states):
    facts = get_quick_facts(df, selected_states)
    
    quick_facts_html = [
        html.H3('Quick Facts', style={'color': '#688ae8', 'marginTop': '20px'}),
        html.P(f"Total recorded attacks: {facts['total_attacks']}"),
        html.P(f"Year range: {facts['year_range']}"),
        html.P(f"Most dangerous state: {facts['most_dangerous_state']}"),
        html.P(f"Most common shark: {facts['most_common_shark']}")
    ]
    
    return (
        create_attacks_by_state(df, selected_states),
        create_yearly_trend(df, selected_states),
        create_activity_distribution(df, selected_states),
        create_shark_species(df, selected_states),
        quick_facts_html
    )

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