import dash
from dash import dcc, html
import plotly.graph_objects as go
from dash.dependencies import Input, Output, State
import pandas as pd
import warnings


warnings.filterwarnings("ignore", category=pd.errors.SettingWithCopyWarning)
app = dash.Dash(__name__, suppress_callback_exceptions=True)

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
            children=[
                html.Button('X', id='close-popup',
                            style={'position': 'absolute', 'top': '5px', 'right': '5px', 'font-size': '20px'})
            ],
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
        ),
        # New pie chart for gender distribution
        html.Div(
            dcc.Graph(id='gender-pie-chart'),
            style={'position': 'absolute', 'top': '10%', 'left': '10%', 'width': '20%', 'height': '10%'}
        ),

        html.Div(
            dcc.Graph(id='age-histogram'),
            style={'position': 'absolute', 'top': '55%', 'left': '8%', 'width': '20%', 'height': '10%'}
        ),

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

    return fig, f'Selected Date Range: {start_date} - {end_date}'


# Callback for displaying the popup window (unchanged)
@app.callback(
    [Output('popup', 'children'),
     Output('popup', 'style')],
    [Input('map', 'clickData'),
     Input('close-popup', 'n_clicks')],
    [State('popup', 'style')]
)
def display_popup(clickData, n_clicks, current_style):
    if n_clicks or clickData is None:
        return '', {'display': 'none'}

    custom_data = clickData['points'][0]['customdata']

    # Combine Year, Month, and Day into a single Date field
    date = f"{custom_data['Year']}-{str(custom_data['Month']).zfill(2)}-{str(custom_data['Day']).zfill(2)}"

    # Prepare the desired fields in the specified order
    popup_content = [
        html.Div(f"Date: {date}"),
        html.Div(f"Provocation: {custom_data['Provocation'].title()}"),
        html.Div(f"Activity: {custom_data['Activity'].title()}"),
        html.Div(f"Injury: {custom_data['Injury'].title()}"),
        html.Div(f"State: {custom_data['State']}"),
        html.Div(f"InjuryLocation: {custom_data['InjuryLocation']}"),
        html.Div(f"Gender: {custom_data['Gender'].title()}"),
        html.Div(f"Age: {custom_data['Age']}"),
        html.Div(f"SharkName: {custom_data['SharkName'].title()}"),
        html.Div(f"SharkLength: {custom_data['SharkLength']:.2f}".rstrip('0').rstrip('.') + 'm'),
        html.Div(f"SharkScientific: {custom_data['SharkScientific'].title()}")
    ]

    return (html.Div([
        html.Button('X', id='close-popup',
                    style={'position': 'absolute', 'top': '5px', 'right': '5px', 'font-size': '20px'}),
        *popup_content
    ]), {
                'display': 'block',
                'position': 'absolute',
                'top': '10%',
                'right': '10%',
                'width': '250px',
                'background-color': 'white',
                'padding': '10px',
                'border-radius': '5px',
                'box-shadow': '2px 2px 10px rgba(0,0,0,0.3)'
            })


# Callback to update the pie chart based on the selected date range
@app.callback(
    Output('gender-pie-chart', 'figure'),
    [Input('date-range-slider', 'value')]  # Trigger when the date range slider is changed
)
def update_gender_pie(selected_range):
    start_date, end_date = selected_range
    filtered_df = df[(df['Year'] >= start_date) & (df['Year'] <= end_date)]  # Filter data by selected range

    gender_counts = filtered_df['Gender'].value_counts()  # Count gender distribution
    pie_fig = go.Figure(data=[go.Pie(labels=gender_counts.index, values=gender_counts.values)])

    pie_fig.update_layout(
        showlegend=True
    )

    return pie_fig


@app.callback(
    Output('age-histogram', 'figure'),
    [Input('date-range-slider', 'value')]  # Trigger on date range change
)
def update_age_histogram(selected_range):
    start_date, end_date = selected_range
    filtered_df = df[(df['Year'] >= start_date) & (df['Year'] <= end_date)]  # Filter data by selected range

    # Convert age to numeric, handle non-numeric or missing values
    filtered_df['Age'] = pd.to_numeric(filtered_df['Age'], errors='coerce')
    filtered_df = filtered_df.dropna(subset=['Age'])  # Remove rows with missing ages

    # Create histogram
    hist_fig = go.Figure(
        data=[go.Histogram(
            x=filtered_df['Age'],
            xbins=dict(start=0, end=100, size=10),  # Bin size of 10 years
            marker=dict(color='#1f77b4'),  # Customize bar color
            name='Age Distribution'
        )]
    )

    hist_fig.update_layout(
        autosize=False,
        width=400,
        height=300,
        xaxis=dict(
            title='Age Group (Years)',
            titlefont=dict(size=12)
        ),
        yaxis=dict(
            title='Number of Attacks',
            titlefont=dict(size=12)
        ),
        showlegend=False,
        margin=dict(l=0, r=0, t=0, b=0)
    )

    return hist_fig


if __name__ == '__main__':
    app.run_server(debug=True)
