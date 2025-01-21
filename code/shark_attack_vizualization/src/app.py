import dash
from dash import html, dcc
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
from data import DataManager
from visualizations import DashboardVisualizer
from config import LAYOUT_SETTINGS, STYLE_SETTINGS, STATE_NAME_MAPPING, MAP_SETTINGS
import pandas as pd

# Initialize the data manager and visualizer
data_manager = DataManager()
visualizer = DashboardVisualizer(data_manager)

# Initialize the Dash app
app = dash.Dash(__name__, suppress_callback_exceptions=True)

# Define the app layout
app.layout = html.Div([
    # Store components for state
    dcc.Store(id='selected-states', data=[]),
    dcc.Store(id='camera-position', data={
        'center': {"lat": -28.2744, "lon": 128.7751},
        'zoom': 3.3
    }),
    
    # Left side panel for statistics
    html.Div([
        # Fixed header with filter buttons
        html.Div([
            html.Div([
                html.Button('Filters',
                            id='filter-button',
                            style={
                                'backgroundColor': '#688ae8',
                                'color': 'white',
                                'border': 'none',
                                'padding': '5px 15px',
                                'borderRadius': '5px',
                                'cursor': 'pointer'
                            }),
                html.Button('Reset Filters',
                            id='reset-button',
                            style={
                                'backgroundColor': '#dc3545',
                                'color': 'white',
                                'border': 'none',
                                'padding': '5px 15px',
                                'borderRadius': '5px',
                                'cursor': 'pointer'
                            }),
                html.Button('Recenter Map',
                            id='recenter-button',
                            style={
                                'backgroundColor': '#688ae8',
                                'color': 'white',
                                'border': 'none',
                                'padding': '5px 15px',
                                'borderRadius': '5px',
                                'cursor': 'pointer'
                            }),
            ], style={
                'display': 'flex',
                'gap': '10px',
                'justifyContent': 'flex-end'
            }),
        ], style={
            'display': 'flex',
            'justifyContent': 'flex-end',
            'padding': '20px',
            'backgroundColor': '#121212',
            'position': 'sticky',
            'top': 0,
            'zIndex': 1001,
            'borderBottom': '1px solid #333'
        }),
        
        html.Div([
            # Filter panel - collapsible div
            html.Div([
                # Filter Controls
                html.Div([
                    # Time Period Filter
                    html.Div([
                        html.Label('Filter by Time of Day:', 
                                 style={'color': '#688ae8', 'fontSize': 16, 'marginBottom': '10px'}),
                        html.Div([
                            dcc.Checklist(
                                id='time-period-checklist',
                                options=[
                                    {'label': 'Morning (06:00-12:00)', 'value': 'morning'},
                                    {'label': 'Afternoon (12:00-18:00)', 'value': 'afternoon'},
                                    {'label': 'Evening (18:00-21:00)', 'value': 'evening'},
                                    {'label': 'Night (21:00-06:00)', 'value': 'night'}
                                ],
                                value=[],
                                style={'color': 'white'},
                                className='grid grid-cols-2 gap-2'
                            )
                        ])
                    ], style={
                        'backgroundColor': '#1e1e1e',
                        'padding': '15px',
                        'marginBottom': '20px',
                        'borderRadius': '5px',
                    }),

                    # Gender Filter
                    html.Div([
                        html.Label('Filter by Gender:', 
                                 style={'color': '#688ae8', 'fontSize': 16, 'marginBottom': '10px'}),
                        html.Div([
                            dcc.Checklist(
                                id='gender-checklist',
                                options=[
                                    {'label': 'Female', 'value': 'female'},
                                    {'label': 'Male', 'value': 'male'}
                                ],
                                value=[],
                                style={'color': 'white'},
                                className='grid grid-cols-2 gap-2'
                            )
                        ])
                    ], style={
                        'backgroundColor': '#1e1e1e',
                        'padding': '15px',
                        'marginBottom': '20px',
                        'borderRadius': '5px',
                    }),

                    # Shark Species Filter
                    html.Div([
                        html.Label('Filter by Shark Species:', 
                                 style={'color': '#688ae8', 'fontSize': 16, 'marginBottom': '10px'}),
                        html.Div([
                            dcc.Checklist(
                                id='shark-checklist',
                                options=[
                                    {'label': 'White Shark', 'value': 'white shark'},
                                    {'label': 'Tiger Shark', 'value': 'tiger shark'},
                                    {'label': 'Wobbegong', 'value': 'wobbegong'},
                                    {'label': 'Bull Shark', 'value': 'bull shark'},
                                    {'label': 'Whaler Shark', 'value': 'whaler shark'},
                                    {'label': 'Unknown Species', 'value': 'unknown species'}
                                ],
                                value=[],
                                style={'color': 'white'},
                                className='grid grid-cols-2 gap-2'
                            )
                        ])
                    ], style={
                        'backgroundColor': '#1e1e1e',
                        'padding': '15px',
                        'marginBottom': '20px',
                        'borderRadius': '5px',
                    }),

                    # Month Filter
                    html.Div([
                        html.Label('Filter by Month:', 
                                 style={'color': '#688ae8', 'fontSize': 16, 'marginBottom': '10px'}),
                        html.Div([
                            dcc.Checklist(
                                id='month-checklist',
                                options=[
                                    {'label': 'January', 'value': 1},
                                    {'label': 'February', 'value': 2},
                                    {'label': 'March', 'value': 3},
                                    {'label': 'April', 'value': 4},
                                    {'label': 'May', 'value': 5},
                                    {'label': 'June', 'value': 6},
                                    {'label': 'July', 'value': 7},
                                    {'label': 'August', 'value': 8},
                                    {'label': 'September', 'value': 9},
                                    {'label': 'October', 'value': 10},
                                    {'label': 'November', 'value': 11},
                                    {'label': 'December', 'value': 12}
                                ],
                                value=[],
                                style={'color': 'white'},
                                className='grid grid-cols-3 gap-2'
                            )
                        ])
                    ], style={
                        'backgroundColor': '#1e1e1e',
                        'padding': '15px',
                        'marginBottom': '20px',
                        'borderRadius': '5px',
                    }),

                    # Activity Filter
                    html.Div([
                        html.Label('Filter by Activity:', 
                                 style={'color': '#688ae8', 'fontSize': 16, 'marginBottom': '10px'}),
                        html.Div([
                            dcc.Checklist(
                                id='activity-checklist',
                                options=[
                                    {'label': activity, 'value': activity} 
                                    for activity in sorted(data_manager.df['Activity'].unique())
                                    if pd.notna(activity)
                                ],
                                value=[],
                                style={'color': 'white'},
                                className='grid grid-cols-2 gap-2'
                            )
                        ])
                    ], style={
                        'backgroundColor': '#1e1e1e',
                        'padding': '15px',
                        'marginBottom': '20px',
                        'borderRadius': '5px',
                    }),

                    # Day of Week Filter
                    html.Div([
                        html.Label('Filter by Day of Week:', 
                                 style={'color': '#688ae8', 'fontSize': 16, 'marginBottom': '10px'}),
                        html.Div([
                            dcc.Checklist(
                                id='day-checklist',
                                options=[
                                    {'label': 'Monday', 'value': 'Monday'},
                                    {'label': 'Tuesday', 'value': 'Tuesday'},
                                    {'label': 'Wednesday', 'value': 'Wednesday'},
                                    {'label': 'Thursday', 'value': 'Thursday'},
                                    {'label': 'Friday', 'value': 'Friday'},
                                    {'label': 'Saturday', 'value': 'Saturday'},
                                    {'label': 'Sunday', 'value': 'Sunday'}
                                ],
                                value=[],
                                style={'color': 'white'},
                                className='grid grid-cols-2 gap-2'
                            )
                        ])
                    ], style={
                        'backgroundColor': '#1e1e1e',
                        'padding': '15px',
                        'marginBottom': '20px',
                        'borderRadius': '5px',
                    }),

                    # Year Range Slider
                    html.Div([
                        html.Div([
                            html.Label('Filter by Year:', 
                                     style={'color': '#688ae8', 'fontSize': 16, 'marginBottom': '10px'}),
                            html.Span(id='year-range-display', 
                                    style={'color': 'white', 'float': 'right'})
                        ]),
                        dcc.RangeSlider(
                            id='year-slider',
                            min=1900,
                            max=2024,
                            step=1,
                            value=[1900, 2024],
                            marks={
                                1900: {'label': '1900', 'style': {'color': 'white'}},
                                1925: {'label': '1925', 'style': {'color': 'white'}},
                                1950: {'label': '1950', 'style': {'color': 'white'}},
                                1975: {'label': '1975', 'style': {'color': 'white'}},
                                2000: {'label': '2000', 'style': {'color': 'white'}},
                                2024: {'label': '2024', 'style': {'color': 'white'}}
                            },
                            allowCross=False,
                            tooltip={'always_visible': False, 'placement': 'bottom'}
                        ),
                    ], style={
                        'backgroundColor': '#1e1e1e',
                        'padding': '15px',
                        'marginBottom': '20px',
                        'borderRadius': '5px',
                    }),

                    # Age Range Slider
                    html.Div([
                        html.Div([
                            html.Label('Filter by Age:', 
                                     style={'color': '#688ae8', 'fontSize': 16, 'marginBottom': '10px'}),
                            html.Span(id='age-range-display', 
                                    style={'color': 'white', 'float': 'right'})
                        ]),
                        dcc.RangeSlider(
                            id='age-slider',
                            min=0,
                            max=90,
                            step=1,
                            value=[0, 90],
                            marks={
                                0: {'label': '0', 'style': {'color': 'white'}},
                                20: {'label': '20', 'style': {'color': 'white'}},
                                40: {'label': '40', 'style': {'color': 'white'}},
                                60: {'label': '60', 'style': {'color': 'white'}},
                                80: {'label': '80', 'style': {'color': 'white'}},
                                90: {'label': '90+', 'style': {'color': 'white'}}
                            },
                            allowCross=False,
                            tooltip={'always_visible': False, 'placement': 'bottom'}
                        ),
                    ], style={
                        'backgroundColor': '#1e1e1e',
                        'padding': '15px',
                        'marginBottom': '20px',
                        'borderRadius': '5px',
                    }),
                ], style={'marginBottom': '20px'})
            ], id='filter-panel', style={
                'display': 'none',
                'backgroundColor': 'rgba(18, 18, 18, 0.9)',
                'padding': '15px',
                'borderRadius': '5px',
                'position': 'fixed',
                'top': '70px',
                'left': '10px',
                'width': '460px',
                'maxHeight': '80vh',
                'overflowY': 'auto',
                'zIndex': 1002,
                'boxShadow': '0 4px 6px rgba(0, 0, 0, 0.3)'
            }),
            
            # Graphs section in a container
            html.Div([
                html.Div([
                    dcc.Graph(
                        id='attacks-by-state',
                        config={'displayModeBar': False}
                    )
                ], style={'marginBottom': '40px'}),
                html.Div([
                    dcc.Graph(
                        id='yearly-trend',
                        config={'displayModeBar': False}
                    )
                ], style={'marginBottom': '40px'}),
                html.Div([
                    dcc.Graph(
                        id='activity-distribution',
                        config={'displayModeBar': False}
                    )
                ], style={'marginBottom': '40px'}),
                html.Div([
                    dcc.Graph(
                        id='shark-species',
                        config={'displayModeBar': False}
                    )
                ], style={'marginBottom': '40px'}),
                html.Div([
                    dcc.Graph(
                        id='hourly-distribution',
                        config={'displayModeBar': False}
                    )
                ], style={'marginBottom': '40px'}),
                html.Div([
                    dcc.Graph(
                        id='monthly-distribution',
                        config={'displayModeBar': False}
                    )
                ], style={'marginBottom': '40px'}),
                html.Div(id='quick-facts', style={'padding': '10px', 'color': 'white'})
            ], id='graphs-container', style={'padding': '20px'}),
        ], style={
            'backgroundColor': '#121212',
            'minHeight': 'calc(100vh - 80px)'
        })
    ], style={
        'position': 'fixed',
        'left': '0',
        'top': '0',
        'width': LAYOUT_SETTINGS['sidebar_width'],
        'height': '100vh',
        'backgroundColor': '#121212',
        'overflowY': 'auto',
        'zIndex': '1000'
    }),

    # Main map container
    html.Div([
        dcc.Graph(
            id='australia-map',
            figure=visualizer.create_map(),
            style={'height': '100vh', 'width': '100%'},
            config={'displayModeBar': False, 'scrollZoom': True}
        )
    ], style={
        'marginLeft': LAYOUT_SETTINGS['sidebar_width'],
        'height': '100vh'
    })
])

# Callback for filter panel toggle
@app.callback(
    [Output('filter-panel', 'style')],
    [Input('filter-button', 'n_clicks')],
    [State('filter-panel', 'style')]
)
def toggle_filter_panel(n_clicks, filter_style):
    if n_clicks is None:
        return [{
            'display': 'none',
            'backgroundColor': 'rgba(18, 18, 18, 0.9)',
            'padding': '15px',
            'borderRadius': '5px',
            'position': 'fixed',
            'top': '70px',
            'left': '10px',
            'width':'460px',
            'maxHeight': '80vh',
            'overflowY': 'auto',
            'zIndex': 1002,
            'boxShadow': '0 4px 6px rgba(0, 0, 0, 0.3)'
        }]
    
    if filter_style.get('display') == 'none':
        filter_style['display'] = 'block'
    else:
        filter_style['display'] = 'none'
    
    return [filter_style]

# Callbacks for range displays
@app.callback(
    Output('year-range-display', 'children'),
    [Input('year-slider', 'value')]
)
def update_year_range_text(value):
    return f"Year: {value[0]} - {value[1]}"

@app.callback(
    Output('age-range-display', 'children'),
    [Input('age-slider', 'value')]
)
def update_age_range_text(value):
    return f"Age: {value[0]} - {value[1]}+ years"


# Callback for map updates and recentering
@app.callback(
    [Output('selected-states', 'data'),
     Output('australia-map', 'figure'),
     Output('camera-position', 'data')],
    [Input('australia-map', 'clickData'),
     Input('australia-map', 'relayoutData'),
     Input('recenter-button', 'n_clicks'),
     Input('age-slider', 'value'),
     Input('year-slider', 'value'),
     Input('day-checklist', 'value'),
     Input('gender-checklist', 'value'),
     Input('month-checklist', 'value'),
     Input('activity-checklist', 'value'),
     Input('time-period-checklist', 'value'),
     Input('shark-checklist', 'value')],
    [State('selected-states', 'data'),
     State('camera-position', 'data')]
)
def update_map_and_camera(click_data, relayout_data, recenter_clicks,
                          age_range, year_range, selected_days,
                          selected_genders, selected_months,
                          selected_activities, selected_time_periods,
                          selected_sharks, selected_states, camera_position):
    ctx = dash.callback_context
    triggered_id = ctx.triggered[0]['prop_id'].split('.')[0] if ctx.triggered else None
    triggered_prop = ctx.triggered[0]['prop_id'].split('.')[1] if ctx.triggered else None

    if not selected_states:
        selected_states = []

    # Handle recenter button click
    if triggered_id == 'recenter-button':
        camera_position = {
            'center': MAP_SETTINGS['default_center'],
            'zoom': MAP_SETTINGS['default_zoom']
        }
    # Handle map movement
    elif triggered_prop == 'relayoutData' and relayout_data:
        if 'mapbox.center' in relayout_data:
            camera_position['center'] = relayout_data['mapbox.center']
        if 'mapbox.zoom' in relayout_data:
            camera_position['zoom'] = relayout_data['mapbox.zoom']

    # Handle state selection
    elif triggered_prop == 'clickData' and click_data:
        clicked_point = click_data['points'][0]
        clicked_state = None

        # Handle clicks on choropleth
        if 'location' in clicked_point:
            clicked_state = clicked_point['location']
        # Handle clicks on invisible clickable areas for small states
        elif 'customdata' in clicked_point:
            clicked_state = clicked_point['customdata'][0]

        if clicked_state:
            if clicked_state in selected_states:
                selected_states.remove(clicked_state)
            else:
                selected_states.append(clicked_state)

    return selected_states, visualizer.create_map(
        selected_states=selected_states,
        camera_position=camera_position,
        age_range=age_range,
        year_range=year_range,
        selected_days=selected_days,
        selected_genders=selected_genders,
        selected_months=selected_months,
        selected_activities=selected_activities,
        selected_time_periods=selected_time_periods,
        selected_sharks=selected_sharks
    ), camera_position

# Callback for graph updates
@app.callback(
    [Output('attacks-by-state', 'figure'),
     Output('yearly-trend', 'figure'),
     Output('activity-distribution', 'figure'),
     Output('shark-species', 'figure'),
     Output('monthly-distribution', 'figure'),
     Output('hourly-distribution', 'figure'),
     Output('quick-facts', 'children')],
    [Input('selected-states', 'data'),
     Input('age-slider', 'value'),
     Input('year-slider', 'value'),
     Input('day-checklist', 'value'),
     Input('gender-checklist', 'value'),
     Input('month-checklist', 'value'),
     Input('activity-checklist', 'value'),
     Input('time-period-checklist', 'value'),
     Input('shark-checklist', 'value')]
)
def update_graphs(selected_states, age_range, year_range, selected_days, 
                 selected_genders, selected_months, selected_activities, 
                 selected_time_periods, selected_sharks):
    
    facts = data_manager.get_quick_facts(
        selected_states=selected_states,
        age_range=age_range,
        year_range=year_range,
        selected_days=selected_days,
        selected_genders=selected_genders,
        selected_months=selected_months,
        selected_activities=selected_activities,
        selected_time_periods=selected_time_periods,
        selected_sharks=selected_sharks
    )
    
    quick_facts_html = [
        html.H3('Quick Facts', style={'color': '#688ae8', 'marginTop': '20px'}),
        html.P(f"Total recorded attacks: {facts['total_attacks']}"),
        html.P(f"Year range: {facts['year_range']}"),
        html.P(f"Most dangerous state: {facts['most_dangerous_state']}"),
        html.P(f"Most common shark: {facts['most_common_shark']}"),
        html.P(f"Most common time period: {facts['most_common_time']}")
    ]
    
    return (
        visualizer.create_attacks_by_state(
            selected_states=selected_states,
            age_range=age_range,
            year_range=year_range,
            selected_days=selected_days,
            selected_genders=selected_genders,
            selected_months=selected_months,
            selected_activities=selected_activities,
            selected_time_periods=selected_time_periods,
            selected_sharks=selected_sharks
        ),
        visualizer.create_yearly_trend(
            selected_states=selected_states,
            age_range=age_range,
            year_range=year_range,
            selected_days=selected_days,
            selected_genders=selected_genders,
            selected_months=selected_months,
            selected_activities=selected_activities,
            selected_time_periods=selected_time_periods,
            selected_sharks=selected_sharks
        ),
        visualizer.create_activity_distribution(
            selected_states=selected_states,
            age_range=age_range,
            year_range=year_range,
            selected_days=selected_days,
            selected_genders=selected_genders,
            selected_months=selected_months,
            selected_activities=selected_activities,
            selected_time_periods=selected_time_periods,
            selected_sharks=selected_sharks
        ),
        visualizer.create_shark_species(
            selected_states=selected_states,
            age_range=age_range,
            year_range=year_range,
            selected_days=selected_days,
            selected_genders=selected_genders,
            selected_months=selected_months,
            selected_activities=selected_activities,
            selected_time_periods=selected_time_periods,
            selected_sharks=selected_sharks
        ),
        visualizer.create_hourly_distribution(
            selected_states=selected_states,
            age_range=age_range,
            year_range=year_range,
            selected_days=selected_days,
            selected_genders=selected_genders,
            selected_months=selected_months,
            selected_activities=selected_activities,
            selected_time_periods=selected_time_periods,
            selected_sharks=selected_sharks
        ),
        visualizer.create_monthly_distribution(
            selected_states=selected_states,
            age_range=age_range,
            year_range=year_range,
            selected_days=selected_days,
            selected_genders=selected_genders,
            selected_months=selected_months,
            selected_activities=selected_activities,
            selected_time_periods=selected_time_periods,
            selected_sharks=selected_sharks
        ),
        quick_facts_html
    )


# Reset filters
@app.callback(
    [Output('time-period-checklist', 'value'),
     Output('gender-checklist', 'value'),
     Output('shark-checklist', 'value'),
     Output('month-checklist', 'value'),
     Output('activity-checklist', 'value'),
     Output('day-checklist', 'value'),
     Output('year-slider', 'value'),
     Output('age-slider', 'value'),
     Output('selected-states', 'data', allow_duplicate=True)],
    [Input('reset-button', 'n_clicks')],
    prevent_initial_call=True  # Added prevent_initial_call
)
def reset_filters(n_clicks):
    if n_clicks is None:
        raise dash.exceptions.PreventUpdate

    return (
        [],  # time-period-checklist
        [],  # gender-checklist
        [],  # shark-checklist
        [],  # month-checklist
        [],  # activity-checklist
        [],  # day-checklist
        [1900, 2024],  # year-slider
        [0, 90],  # age-slider
        []  # selected-states - empty list to clear all selections
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
                width: ''' + STYLE_SETTINGS['scrollbar_width'] + ''';
            }
            ::-webkit-scrollbar-track {
                background: #121212;
            }
            ::-webkit-scrollbar-thumb {
                background: ''' + STYLE_SETTINGS['scrollbar_color'] + ''';
                border-radius: 4px;
            }
            ::-webkit-scrollbar-thumb:hover {
                background: ''' + STYLE_SETTINGS['scrollbar_hover_color'] + ''';
            }
            /* Range Slider styling */
            .rc-slider {
                margin-top: 15px;
            }
            .rc-slider-track {
                background-color: #688ae8;
            }
            .rc-slider-handle {
                border: solid 2px #688ae8;
                background-color: #121212;
                opacity: 1;
            }
            .rc-slider-handle:hover {
                border-color: #36def7;
            }
            .rc-slider-handle-active:active {
                border-color: #36def7;
            }
            .rc-slider-rail {
                background-color: #333333;
            }
            .rc-slider-mark-text {
                color: white;
            }
            /* Checkbox styling */
            input[type="checkbox"] {
                accent-color: #688ae8;
                width: 16px;
                height: 16px;
                margin-right: 8px;
            }
            .grid-cols-2 {
                display: grid;
                grid-template-columns: repeat(2, 1fr);
                gap: 0.5rem;
            }
            .grid-cols-3 {
                display: grid;
                grid-template-columns: repeat(3, 1fr);
                gap: 0.5rem;
            }
            /* Focus styles for accessibility */
            input[type="checkbox"]:focus {
                outline: 2px solid #36def7;
                outline-offset: 2px;
            }
            button:focus {
                outline: 2px solid #36def7;
                outline-offset: 2px;
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