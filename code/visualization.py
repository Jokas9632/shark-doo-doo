import dash
from dash import dcc, html
import plotly.graph_objects as go
from dash.dependencies import Input, Output
import pandas as pd

app = dash.Dash(__name__)

# Color dictionary based on scientific shark names
scientific_name_to_color = {
    'Carcharodon carcharias': '#FF6347',  # Tomato Red
    'Galeocerdo cuvier': '#FF4500',  # Orange Red
    'Carcharhinus leucas': '#32CD32',  # Lime Green
    'Unknown species': '#FFD700',  # Gold
    'Carcharhinidae': '#8A2BE2',  # Blue Violet
    'Orectolobidae': '#00FFFF',  # Aqua
    'Notorynchus cepedianus': '#DC143C',  # Crimson
    'Carcharhinus obscurus': '#FF1493',  # Deep Pink
    'Carcharhinus brachyurus': '#8B008B',  # Dark Magenta
    'Squalidae': '#FF8C00',  # Dark Orange
    'Isurus oxyrinchus': '#4682B4',  # Steel Blue
    'Galeorhinus galeus': '#00FA9A',  # Medium Spring Green
    'Carcharhinus amblyrhynchos': '#D2691E',  # Chocolate
    'Triaenodon obesus': '#FFB6C1',  # Light Pink
    'Sphyrnidae': '#008B8B',  # Dark Cyan
    'Carcharius taurus': '#B22222',  # Firebrick
    'Carcharhinus galapagensis': '#3CB371',  # Medium Sea Green
    'Carcharhinus albimarginatus': '#FFD700',  # Gold (used earlier)
    'Brachaelurus waddi': '#8B0000',  # Dark Red
    'Carcharhinus melanopterus': '#ADFF2F',  # Green Yellow
    'unknown': '#FF6347',  # Tomato Red (used earlier)
    'Heterodontus portusjacksoni': '#7FFF00',  # Chartreuse
    'Negaprion brevirostris': '#FF00FF'  # Fuchsia
}

df = pd.read_csv('cleaned_data.csv')

# Create the map figure
fig = go.Figure()

# Adding initial map plotting (unchanged)
for _, row in df.iterrows():
    lat = row['Latitude']
    lon = row['Longitude']
    shark_scientific = row['SharkScientific']

    marker_color = scientific_name_to_color.get(shark_scientific, '#808080')  # Default to grey if not found

    fig.add_trace(
        go.Scattergeo(
            lon=[lon],
            lat=[lat],
            mode='markers',
            marker=dict(size=6, color=marker_color),
            name=f"Shark Attack {row.name}",
            text=[f"Shark Attack {row.name}"],
            hoverinfo="text",
            customdata=[row.to_dict()],
            selected=dict(marker=dict(opacity=1)),
            unselected=dict(marker=dict(opacity=1))
        )
    )

fig.update_layout(
    geo=dict(
        projection_type='natural earth',
        landcolor='#a3723c',
        showocean=True,
        oceancolor='#487edb',
        coastlinecolor='#000000',
        lonaxis=dict(range=[110, 155]),
        lataxis=dict(range=[-45, -10]),
    ),
    clickmode='event+select',
    showlegend=False
)

# Define layout of the Dash app
app.layout = html.Div(
    [
        # Configuration window for the date filter (added)
        html.Div(
            [
                # Date range filter using a two-sided slider
                dcc.RangeSlider(
                    id='date-range-slider',  # Unique ID for the slider
                    min=df['Year'].min(),  # Set minimum year from your data
                    max=df['Year'].max(),  # Set maximum year from your data
                    step=1,  # Step size, set to 1 year for granular control
                    marks={year: str(year) for year in range(df['Year'].min(), df['Year'].max() + 1, 2)},
                    # Marks for every 2 years
                    value=[df['Year'].min(), df['Year'].max()],  # Initial range is the full dataset's range
                    tooltip={'placement': 'bottom', 'always_visible': True},  # Tooltip display on hover
                ),
                html.Div(id='date-output-container')  # Container to display selected date range
            ],
            style={'position': 'absolute', 'top': '10%', 'left': '10%', 'padding': '10px', 'backgroundColor': '#fff',
                   'borderRadius': '8px', 'zIndex': 10}
        ),

        # Map display
        dcc.Graph(
            id='map',
            figure=fig,
            style={'height': '80%', 'width': '100%'}
        ),
        html.Div(
            id='popup',
            style={
                'position': 'absolute',
                'top': '10%',
                'left': '10%',
                'width': '250px',
                'background-color': 'white',
                'padding': '10px',
                'border-radius': '5px',
                'display': 'none',
                'box-shadow': '2px 2px 10px rgba(0,0,0,0.3)',
            }
        )
    ],
    style={'height': '100vh', 'width': '100vw', 'margin': '0', 'padding': '0'}
)


# Callback for updating the map based on the date filter (added)
@app.callback(
    [Output('map', 'figure'),  # Update the map figure based on selected date range
     Output('date-output-container', 'children')],  # Display the selected date range
    [Input('date-range-slider', 'value')]  # Trigger when slider value changes
)
def update_map(selected_range):
    start_date, end_date = selected_range
    filtered_df = df[(df['Year'] >= start_date) & (df['Year'] <= end_date)]  # Filter data based on the date range

    # Recreate the map with the filtered data
    fig = go.Figure()
    for _, row in filtered_df.iterrows():
        lat = row['Latitude']
        lon = row['Longitude']
        shark_scientific = row['SharkScientific']
        marker_color = scientific_name_to_color.get(shark_scientific, '#808080')  # Default to grey if not found

        fig.add_trace(
            go.Scattergeo(
                lon=[lon],
                lat=[lat],
                mode='markers',
                marker=dict(size=6, color=marker_color),
                name=f"Shark Attack {row.name}",
                text=[f"Shark Attack {row.name}"],
                hoverinfo="text",
                customdata=[row.to_dict()],
                selected=dict(marker=dict(opacity=1)),
                unselected=dict(marker=dict(opacity=1))
            )
        )

    fig.update_layout(
        geo=dict(
            projection_type='natural earth',
            landcolor='#a3723c',
            showocean=True,
            oceancolor='#487edb',
            coastlinecolor='#000000',
            lonaxis=dict(range=[110, 155]),
            lataxis=dict(range=[-45, -10]),
        ),
        clickmode='event+select',
        showlegend=False
    )

    # Return updated map figure and display the selected date range
    return fig, f'Selected Date Range: {start_date} - {end_date}'


# Callback for displaying the popup window (unchanged)
@app.callback(
    [Output('popup', 'children'),
     Output('popup', 'style')],
    [Input('map', 'clickData')]
)
def display_popup(clickData):
    if clickData is None:
        return '', {'display': 'none'}

    custom_data = clickData['points'][0]['customdata']

    info = html.Div([
        html.Div(f"{key}: {value}") for key, value in custom_data.items()
    ])

    return info, {'display': 'block', 'position': 'absolute', 'top': '10%', 'left': '10%', 'width': '250px',
                  'background-color': 'white', 'padding': '10px', 'border-radius': '5px',
                  'box-shadow': '2px 2px 10px rgba(0,0,0,0.3)'}


if __name__ == '__main__':
    app.run_server(debug=True)