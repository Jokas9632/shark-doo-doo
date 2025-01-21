# Colors for different states in the map
STATE_COLORS = {
    'NSW': '#FF3D00',  # Bright orange-red
    'WA': '#2196F3',   # Bright blue
    'QLD': '#AA00FF',  # Bright purple
    'VIC': '#00E676',  # Bright green
    'SA': '#FFEB3B',   # Bright yellow
    'TAS': '#FF1744',  # Bright pink-red
    'NT': '#18FFFF',   # Bright cyan
}

# Mapping between short and long state names
STATE_NAME_MAPPING = {
    'NSW': 'New South Wales',
    'VIC': 'Victoria',
    'QLD': 'Queensland',
    'WA': 'Western Australia',
    'SA': 'South Australia',
    'TAS': 'Tasmania',
    'NT': 'Northern Territory',
    'ACT': 'Australian Capital Territory'
}

# Reverse mapping for convenience
REVERSE_STATE_MAPPING = {v: k for k, v in STATE_NAME_MAPPING.items()}

# Map settings
MAP_SETTINGS = {
    'default_center': {"lat": -28.2744, "lon": 128.7751},
    'default_zoom': 3.3,
    'style': 'carto-darkmatter'
}

# Chart settings
CHART_SETTINGS = {
    'background_color': '#121212',
    'font_color': 'white',
    'grid_color': '#333333',
    'accent_color': '#688ae8',
    'hover_bgcolor': '#121212',
    'hover_bordercolor': '#36def7'
}

# Layout settings
LAYOUT_SETTINGS = {
    'sidebar_width': '500px',
    'chart_heights': {
        'state_chart': 200,
        'yearly_trend': 200,
        'activity_chart': 300,
        'species_chart': 250,
        'hourly_chart': 200,
        'monthly_dist': 300
    }
}

# Data settings
DATA_SETTINGS = {
    'required_columns': [
        'Year', 'State', 'Latitude', 'Longitude', 'SharkName',
        'Activity', 'Injury', 'Gender', 'Age'
    ],
    'top_n_activities': 8,
    'top_n_species': 5
}

# Style settings for the app
STYLE_SETTINGS = {
    'scrollbar_width': '8px',
    'scrollbar_color': '#36def7',
    'scrollbar_hover_color': '#2ba7b9'
}

# Hover text template
HOVER_TEXT_TEMPLATE = """
<b>Year:</b> {year}<br>
<b>Shark Species:</b> {shark}<br>
<b>Activity:</b> {activity}<br>
<b>Injury:</b> {injury}<br>
<b>Gender:</b> {gender}<br>
<b>Age:</b> {age}
"""

# File paths
DATA_PATHS = {
    'csv_file': 'data/cleaned_data.csv',
    'geojson_file': 'data/states.geojson'
}