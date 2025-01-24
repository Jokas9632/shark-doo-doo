import dash
from dash import html, dcc
from dash.dependencies import Input, Output, State, ALL
from dash.exceptions import PreventUpdate
from data import DataManager
from visualizations import DashboardVisualizer
from config import LAYOUT_SETTINGS, STYLE_SETTINGS, STATE_NAME_MAPPING, MAP_SETTINGS
import pandas as pd
import json

GRAPH_CATEGORIES = {
    'all': 'All Graphs',
    'geography': 'Geographical',
    'species': 'Shark Species',
    'temporal': 'Temporal',
    'demographics': 'Demographics'
}

CATEGORY_GRAPHS = {
    'geography': ['attacks-by-state'],
    'species': ['shark-species', 'shark-streamgraph'],
    'temporal': ['monthly-distribution', 'day-distribution', 'hourly-distribution'],
    'demographics': ['activity-distribution', 'age-distribution', 'provocation-distribution', 'population-pyramid']
}

data_manager = DataManager()
visualizer = DashboardVisualizer(data_manager)

app = dash.Dash(__name__, suppress_callback_exceptions=True)

app.layout = html.Div([
    dcc.Store(id='selected-states', data=[]),
    dcc.Store(id='camera-position', data={
        'center': {"lat": -28.2744, "lon": 128.7751},
        'zoom': 3.3
    }),
    dcc.Store(id='selected-activities', data=[], storage_type='memory'),
    
    html.Div([
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
                                'cursor': 'pointer',
                                'marginRight': '20px',
                            }),
                html.Button('Reset Filters',
                            id='reset-button',
                            style={
                                'backgroundColor': '#dc3545',
                                'color': 'white',
                                'border': 'none',
                                'padding': '5px 15px',
                                'borderRadius': '5px',
                                'marginRight': '20px'
                            }),
            ], style={
                'display': 'flex',
                'alignItems': 'center',
                'marginBottom': '20px',
                'justifyContent': 'center',
            }),

            html.Div([
                html.Button(
                    value,
                    id={'type': 'category-button', 'index': key},
                    style={
                        'backgroundColor': '#27821D',
                        'color': 'white',
                        'border': 'none',
                        'padding': '5px 15px',
                        'borderRadius': '5px',
                        'cursor': 'pointer',
                        'marginRight': '10px'
                    }
                ) for key, value in GRAPH_CATEGORIES.items()
            ], style={
                'display': 'flex',
                'flexWrap': 'wrap',
                'gap': '10px',
                'justifyContent': 'center',
                'width': '100%'
            }),
        ], style={
            'padding': '20px',
            'backgroundColor': '#121212',
            'position': 'sticky',
            'top': 0,
            'zIndex': 1001,
            'borderBottom': '1px solid #333'
        }),
        
        html.Div([
            html.Div([
                html.Div([
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

                    html.Div([
                        html.Label('Filter by Injury:',
                                 style={'color': '#688ae8', 'fontSize': 16, 'marginBottom': '10px'}),
                        html.Div([
                            dcc.Checklist(
                                id='injury-checklist',
                                options=[
                                    {'label': 'Fatal', 'value': 'fatal'},
                                    {'label': 'Injured', 'value': 'injured'},
                                    {'label': 'Uninjured', 'value': 'uninjured'}
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
            
            html.Div([
                html.Div([
                    dcc.Graph(
                        id='attacks-by-state',
                        config={'displayModeBar': False}
                    )
                ], id={'type': 'graph-container', 'index': 'attacks-by-state'}, style={'marginBottom': '40px'}),
                html.Div([
                    dcc.Graph(
                        id='activity-distribution',
                        config={'displayModeBar': False}
                    )
                ], id={'type': 'graph-container', 'index': 'activity-distribution'}, style={'marginBottom': '40px'}),
                html.Div([
                    dcc.Graph(
                        id='provocation-distribution',
                        config={'displayModeBar': False}
                    )
                ], id={'type': 'graph-container', 'index': 'provocation-distribution'}, style={'marginBottom': '40px'}),
                html.Div([
                    dcc.Graph(
                        id='shark-species',
                        config={'displayModeBar': False}
                    )
                ], id={'type': 'graph-container', 'index': 'shark-species'}, style={'marginBottom': '40px'}),
                html.Div([
                    dcc.Graph(
                        id='shark-streamgraph',
                        config={'displayModeBar': False}
                    )
                ], id={'type': 'graph-container', 'index': 'shark-streamgraph'}, style={'marginBottom': '40px'}),
                html.Div([
                    dcc.Graph(
                        id='age-distribution',
                        config={'displayModeBar': False}
                    )
                ], id={'type': 'graph-container', 'index': 'age-distribution'}, style={'marginBottom': '40px'}),
                html.Div([
                    dcc.Graph(
                        id='population-pyramid',
                        config={'displayModeBar': False}
                    )
                ], id={'type': 'graph-container', 'index': 'population-pyramid'}, style={'marginBottom': '40px'}),
                html.Div([
                    dcc.Graph(
                        id='monthly-distribution',
                        config={'displayModeBar': False}
                    )
                ], id={'type': 'graph-container', 'index': 'monthly-distribution'}, style={'marginBottom': '40px'}),
                html.Div([
                    dcc.Graph(
                        id='day-distribution',
                        config={'displayModeBar': False}
                    )
                ], id={'type': 'graph-container', 'index': 'day-distribution'}, style={'marginBottom': '40px'}),
                html.Div([
                    dcc.Graph(
                        id='hourly-distribution',
                        config={'displayModeBar': False}
                    )
                ], id={'type': 'graph-container', 'index': 'hourly-distribution'}, style={'marginBottom': '40px'})
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

    html.Div([
        html.Div([
            html.Div([
                dcc.Checklist(
                    id='heatmap-toggle',
                    options=[{'label': 'Show as Heatmap', 'value': 'heatmap'}],
                    value=[],
                    style={'color': 'white', 'display': 'flex', 'alignItems': 'center', 'marginRight': '10px'}
                ),
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
                'alignItems': 'center', 
                'position': 'absolute', 
                'top': '10px', 
                'right': '10px', 
                'zIndex': 1001,
                'backgroundColor': 'rgba(18, 18, 18, 0.7)',
                'padding': '10px',
                'borderRadius': '5px'
            })
        ], style={'position': 'relative'}),
        
        dcc.Graph(
            id='australia-map',
            figure=visualizer.create_map(),
            style={'height': '100vh', 'width': '100%'},
            config={'displayModeBar': False, 'scrollZoom': True}
        )
    ], style={
        'marginLeft': LAYOUT_SETTINGS['sidebar_width'],
        'height': '100vh',
        'position': 'relative'
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
            'width': '650px',
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
     Output('camera-position', 'data'),
     Output('selected-activities', 'data'),
     Output('activity-checklist', 'value')],
    [Input('injury-checklist', 'value'),
     Input('australia-map', 'clickData'),
     Input('attacks-by-state', 'clickData'),
     Input('activity-distribution', 'clickData'),
     Input('australia-map', 'relayoutData'),
     Input('recenter-button', 'n_clicks'),
     Input('heatmap-toggle', 'value'),
     Input('age-slider', 'value'),
     Input('year-slider', 'value'),
     Input('day-checklist', 'value'),
     Input('gender-checklist', 'value'),
     Input('month-checklist', 'value'),
     Input('activity-checklist', 'value'),
     Input('time-period-checklist', 'value'),
     Input('shark-checklist', 'value')],
    [State('selected-states', 'data'),
     State('camera-position', 'data'),
     State('selected-activities', 'data')]
)
def update_map_and_camera(selected_injuries, map_click_data, state_bar_click_data,
                         activity_bar_click_data, relayout_data, recenter_clicks,
                         heatmap_toggle, age_range, year_range, selected_days,
                         selected_genders, selected_months, activity_checklist,
                         selected_time_periods, selected_sharks, selected_states,
                         camera_position, selected_activities):
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

    # Handle state bar click
    elif triggered_id == 'attacks-by-state' and state_bar_click_data:
        clicked_state = state_bar_click_data['points'][0]['customdata']
        if clicked_state in selected_states:
            selected_states.remove(clicked_state)
        else:
            selected_states.append(clicked_state)
    
    if selected_activities is None:
        selected_activities = []

    # Handle activity bar click
    if triggered_id == 'activity-distribution' and activity_bar_click_data:
        clicked_activity = activity_bar_click_data['points'][0]['y']
        if clicked_activity in selected_activities:
            selected_activities.remove(clicked_activity)
        else:
            selected_activities.append(clicked_activity)
        activity_checklist = selected_activities
    elif triggered_id == 'activity-checklist':
        selected_activities = activity_checklist if activity_checklist else []
    
    # Handle map click
    elif triggered_prop == 'clickData' and map_click_data:
        clicked_point = map_click_data['points'][0]
        clicked_state = None

        # Handle clicks on choropleth
        if 'location' in clicked_point:
            clicked_state = clicked_point['location']
        elif 'customdata' in clicked_point:
            clicked_state = clicked_point['customdata'][0]

        if clicked_state:
            if clicked_state in selected_states:
                selected_states.remove(clicked_state)
            else:
                selected_states.append(clicked_state)

    show_heatmap = 'heatmap' in (heatmap_toggle or [])

    return selected_states, visualizer.create_map(
        selected_injuries=selected_injuries,
        selected_states=selected_states,
        camera_position=camera_position,
        show_heatmap=show_heatmap,
        age_range=age_range,
        year_range=year_range,
        selected_days=selected_days,
        selected_genders=selected_genders,
        selected_months=selected_months,
        selected_activities=selected_activities,
        selected_time_periods=selected_time_periods,
        selected_sharks=selected_sharks
    ), camera_position, selected_activities, activity_checklist

# Callback for graph updates
@app.callback(
    [Output('attacks-by-state', 'figure'),
     Output('activity-distribution', 'figure'),
     Output('provocation-distribution', 'figure'),
     Output('shark-species', 'figure'),
     Output('shark-streamgraph', 'figure'),
     Output('age-distribution', 'figure'),
     Output('population-pyramid', 'figure'),
     Output('monthly-distribution', 'figure'),
     Output('day-distribution', 'figure'),
     Output('hourly-distribution', 'figure')],
    [Input('injury-checklist', 'value'),
     Input('selected-states', 'data'),
     Input('selected-activities', 'data'),
     Input('age-slider', 'value'),
     Input('year-slider', 'value'),
     Input('day-checklist', 'value'),
     Input('gender-checklist', 'value'),
     Input('month-checklist', 'value'),
     Input('time-period-checklist', 'value'),
     Input('shark-checklist', 'value')]
)
def update_graphs(selected_injuries, selected_states, selected_activities,
                 age_range, year_range, selected_days,
                 selected_genders, selected_months,
                 selected_time_periods, selected_sharks):
    
    return (
        visualizer.create_attacks_by_state(
            selected_injuries=selected_injuries,
            selected_states=selected_states,
            selected_activities=selected_activities,
            age_range=age_range,
            year_range=year_range,
            selected_days=selected_days,
            selected_genders=selected_genders,
            selected_months=selected_months,
            selected_time_periods=selected_time_periods,
            selected_sharks=selected_sharks
        ),
        visualizer.create_activity_distribution(
            selected_injuries=selected_injuries,
            selected_states=selected_states,
            selected_activities=selected_activities,
            age_range=age_range,
            year_range=year_range,
            selected_days=selected_days,
            selected_genders=selected_genders,
            selected_months=selected_months,
            selected_time_periods=selected_time_periods,
            selected_sharks=selected_sharks
        ),
        visualizer.create_provocation_distribution(
            selected_injuries=selected_injuries,
            selected_states=selected_states,
            selected_activities=selected_activities,
            age_range=age_range,
            year_range=year_range,
            selected_days=selected_days,
            selected_genders=selected_genders,
            selected_months=selected_months,
            selected_time_periods=selected_time_periods,
            selected_sharks=selected_sharks
        ),
        visualizer.create_shark_species(
            selected_injuries=selected_injuries,
            selected_states=selected_states,
            selected_activities=selected_activities,
            age_range=age_range,
            year_range=year_range,
            selected_days=selected_days,
            selected_genders=selected_genders,
            selected_months=selected_months,
            selected_time_periods=selected_time_periods,
            selected_sharks=selected_sharks
        ),
        visualizer.create_shark_streamgraph(
            selected_injuries=selected_injuries,
            selected_states=selected_states,
            selected_activities=selected_activities,
            age_range=age_range,
            year_range=year_range,
            selected_days=selected_days,
            selected_genders=selected_genders,
            selected_months=selected_months,
            selected_time_periods=selected_time_periods,
            selected_sharks=selected_sharks
        ),
        visualizer.create_age_distribution(
            selected_injuries=selected_injuries,
            selected_states=selected_states,
            selected_activities=selected_activities,
            age_range=age_range,
            year_range=year_range,
            selected_days=selected_days,
            selected_genders=selected_genders,
            selected_months=selected_months,
            selected_time_periods=selected_time_periods,
            selected_sharks=selected_sharks
        ),
        visualizer.create_population_pyramid(
            selected_injuries=selected_injuries,
            selected_states=selected_states,
            selected_activities=selected_activities,
            age_range=age_range,
            year_range=year_range,
            selected_days=selected_days,
            selected_genders=selected_genders,
            selected_months=selected_months,
            selected_time_periods=selected_time_periods,
            selected_sharks=selected_sharks
        ),
        visualizer.create_monthly_distribution(
            selected_injuries=selected_injuries,
            selected_states=selected_states,
            selected_activities=selected_activities,
            age_range=age_range,
            year_range=year_range,
            selected_days=selected_days,
            selected_genders=selected_genders,
            selected_months=selected_months,
            selected_time_periods=selected_time_periods,
            selected_sharks=selected_sharks
        ),
        visualizer.create_day_distribution(
            selected_injuries=selected_injuries,
            selected_states=selected_states,
            selected_activities=selected_activities,
            age_range=age_range,
            year_range=year_range,
            selected_days=selected_days,
            selected_genders=selected_genders,
            selected_months=selected_months,
            selected_time_periods=selected_time_periods,
            selected_sharks=selected_sharks
        ),
        visualizer.create_hourly_distribution(
            selected_injuries=selected_injuries,
            selected_states=selected_states,
            selected_activities=selected_activities,
            age_range=age_range,
            year_range=year_range,
            selected_days=selected_days,
            selected_genders=selected_genders,
            selected_months=selected_months,
            selected_time_periods=selected_time_periods,
            selected_sharks=selected_sharks
        )
    )

# Reset filters
@app.callback(
    [Output('injury-checklist', 'value'),
     Output('time-period-checklist', 'value'),
     Output('gender-checklist', 'value'),
     Output('shark-checklist', 'value'),
     Output('month-checklist', 'value'),
     Output('activity-checklist', 'value', allow_duplicate=True),
     Output('day-checklist', 'value'),
     Output('year-slider', 'value'),
     Output('age-slider', 'value'),
     Output('selected-states', 'data', allow_duplicate=True),
     Output('selected-activities', 'data', allow_duplicate = True)],
    [Input('reset-button', 'n_clicks')],
    prevent_initial_call=True
)
def reset_filters(n_clicks):
    if n_clicks is None:
        raise PreventUpdate

    return ([], [], [], [], [], [], [], [1900, 2024], [0, 90], [], [])

# Handle graph visibility
@app.callback(
    [Output({'type': 'graph-container', 'index': graph_id}, 'style')
     for graph_id in ['attacks-by-state', 'activity-distribution', 'provocation-distribution',
                      'shark-species', 'shark-streamgraph', 'age-distribution', 'population-pyramid',
                      'monthly-distribution', 'day-distribution', 'hourly-distribution']],
    [Input({'type': 'category-button', 'index': ALL}, 'n_clicks')],
    [State({'type': 'category-button', 'index': ALL}, 'id')]
)
def update_graph_visibility(n_clicks, button_ids):
    ctx = dash.callback_context
    if not ctx.triggered or not any(n_clicks):
        return [{'marginBottom': '40px'} for _ in range(10)]

    triggered_id = ctx.triggered[0]['prop_id']
    if not triggered_id:
        return [{'marginBottom': '40px'} for _ in range(10)]

    clicked_category = json.loads(triggered_id.split('.')[0])['index']

    if clicked_category == 'all':
        return [{'marginBottom': '40px'} for _ in range(10)]

    visible_graphs = CATEGORY_GRAPHS[clicked_category]

    return [
        {'marginBottom': '40px'} if graph_id in visible_graphs else {'display': 'none'}
        for graph_id in ['attacks-by-state', 'activity-distribution', 'provocation-distribution',
                         'shark-species', 'shark-streamgraph', 'age-distribution', 'population-pyramid',
                         'monthly-distribution', 'day-distribution', 'hourly-distribution']
    ]

@app.callback(
    [Output({'type': 'category-button', 'index': ALL}, 'style')],
    [Input({'type': 'category-button', 'index': ALL}, 'n_clicks')],
    [State({'type': 'category-button', 'index': ALL}, 'id')]
)
def update_button_colors(n_clicks, button_ids):
    ctx = dash.callback_context
    if not ctx.triggered:
        return [[{
            'backgroundColor': '#27821D',
            'color': 'white',
            'border': 'none',
            'padding': '5px 15px',
            'borderRadius': '5px',
            'cursor': 'pointer',
            'marginRight': '10px'
        } for _ in button_ids]]

    triggered_id = ctx.triggered[0]['prop_id']
    if not triggered_id:
        return [[{
            'backgroundColor': '#27821D',
            'color': 'white',
            'border': 'none',
            'padding': '5px 15px',
            'borderRadius': '5px',
            'cursor': 'pointer',
            'marginRight': '10px'
        } for _ in button_ids]]

    clicked_category = json.loads(triggered_id.split('.')[0])['index']

    return [[{
        'backgroundColor': '#1b5913' if (button['index'] == clicked_category and button['index'] != 'all') else '#27821D',
        'color': 'white',
        'border': 'none',
        'padding': '5px 15px',
        'borderRadius': '5px',
        'cursor': 'pointer',
        'marginRight': '10px'
    } for button in button_ids]]


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
    app.run_server(debug=False)