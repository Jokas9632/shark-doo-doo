import dash
from dash import html, dcc
from dash.dependencies import Input, Output, State
from data import DataManager
from visualizations import DashboardVisualizer
from config import LAYOUT_SETTINGS, STYLE_SETTINGS

# Note: Run the app in terminal from directory code/shark_attack_vizualization

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
        html.Div([
            # Header with title and filter button
            html.Div([
                html.H3('Australian Shark Attacks', 
                       style={'color': '#688ae8', 'marginBottom': '20px', 'display': 'inline-block'}),
                html.Button('Filters', 
                          id='filter-button',
                          style={
                              'marginLeft': '20px',
                              'backgroundColor': '#688ae8',
                              'color': 'white',
                              'border': 'none',
                              'padding': '5px 15px',
                              'borderRadius': '5px',
                              'cursor': 'pointer'
                          }),
            ], style={'display': 'flex', 'alignItems': 'center', 'marginBottom': '20px'}),

            # Filter panel - collapsible div
            html.Div([
                # Filter Controls
                html.Div([
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
                            step=5,
                            value=[1900, 2024],
                            marks={
                                1900: {'label': '1900', 'style': {'color': 'white'}},
                                1940: {'label': '1940', 'style': {'color': 'white'}},
                                1980: {'label': '1980', 'style': {'color': 'white'}},
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

                    # Month Range Slider
                    html.Div([
                        html.Div([
                            html.Label('Filter by Month:', 
                                     style={'color': '#688ae8', 'fontSize': 16, 'marginBottom': '10px'}),
                            html.Span(id='month-range-display', 
                                    style={'color': 'white', 'float': 'right'})
                        ]),
                        dcc.RangeSlider(
                            id='month-slider',
                            min=1,
                            max=12,
                            step=1,
                            value=[1, 12],
                            marks={
                                1: {'label': 'Jan', 'style': {'color': 'white'}},
                                3: {'label': 'Mar', 'style': {'color': 'white'}},
                                6: {'label': 'Jun', 'style': {'color': 'white'}},
                                9: {'label': 'Sep', 'style': {'color': 'white'}},
                                12: {'label': 'Dec', 'style': {'color': 'white'}}
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

                    # Day Range Slider
                    html.Div([
                        html.Div([
                            html.Label('Filter by Day:', 
                                     style={'color': '#688ae8', 'fontSize': 16, 'marginBottom': '10px'}),
                            html.Span(id='day-range-display', 
                                    style={'color': 'white', 'float': 'right'})
                        ]),
                        dcc.RangeSlider(
                            id='day-slider',
                            min=1,
                            max=31,
                            step=1,
                            value=[1, 31],
                            marks={
                                1: {'label': '1', 'style': {'color': 'white'}},
                                10: {'label': '10', 'style': {'color': 'white'}},
                                20: {'label': '20', 'style': {'color': 'white'}},
                                31: {'label': '31', 'style': {'color': 'white'}}
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
                            step=5,
                            value=[0, 90],
                            marks={
                                0: {'label': '0', 'style': {'color': 'white'}},
                                30: {'label': '30', 'style': {'color': 'white'}},
                                60: {'label': '60', 'style': {'color': 'white'}},
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
                'backgroundColor': 'rgba(18, 18, 18, 0.95)',
                'padding': '20px',
                'marginBottom': '20px',
                'borderRadius': '5px',
                'maxHeight': '80vh',
                'overflowY': 'auto'
            }),
            
            # Graphs section in a container
            html.Div([
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
            ], id='graphs-container'),
        ], style={
            'padding': '20px',
            'backgroundColor': '#121212'
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

    # Main map
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
    [Output('filter-panel', 'style'),
     Output('graphs-container', 'style')],
    [Input('filter-button', 'n_clicks')],
    [State('filter-panel', 'style'),
     State('graphs-container', 'style')]
)
def toggle_filter_panel(n_clicks, filter_style, graphs_style):
    if n_clicks is None:
        return [
            {
                'display': 'none',
                'backgroundColor': 'rgba(18, 18, 18, 0.95)',
                'padding': '20px',
                'marginBottom': '20px',
                'borderRadius': '5px',
                'maxHeight': '80vh',
                'overflowY': 'auto'
            },
            {}
        ]
    
    if filter_style.get('display') == 'none':
        filter_style['display'] = 'block'
        graphs_style = {'marginTop': '20px'}  # Add space between filters and graphs
    else:
        filter_style['display'] = 'none'
        graphs_style = {}
    
    return filter_style, graphs_style

# Rest of the callbacks remain the same
@app.callback(
    Output('year-range-display', 'children'),
    [Input('year-slider', 'value')]
)
def update_year_range_text(value):
    return f"Year: {value[0]} - {value[1]}"

@app.callback(
    Output('month-range-display', 'children'),
    [Input('month-slider', 'value')]
)
def update_month_range_text(value):
    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    return f"Month: {months[value[0]-1]} - {months[value[1]-1]}"

@app.callback(
    Output('day-range-display', 'children'),
    [Input('day-slider', 'value')]
)
def update_day_range_text(value):
    return f"Day: {value[0]} - {value[1]}"

@app.callback(
    Output('age-range-display', 'children'),
    [Input('age-slider', 'value')]
)
def update_age_range_text(value):
    return f"Age: {value[0]} - {value[1]}+ years"

# Map callback
@app.callback(
    Output('selected-states', 'data'),
    Output('australia-map', 'figure'),
    Output('camera-position', 'data'),
    Input('australia-map', 'clickData'),
    Input('australia-map', 'relayoutData'),
    Input('age-slider', 'value'),
    Input('year-slider', 'value'),
    Input('month-slider', 'value'),
    Input('day-slider', 'value'),
    State('selected-states', 'data'),
    State('camera-position', 'data')
)
def update_selected_states(click_data, relayout_data, age_range, year_range, month_range, day_range, selected_states, camera_position):
    ctx = dash.callback_context
    triggered_id = ctx.triggered[0]['prop_id'].split('.')[1] if ctx.triggered else None
    
    if not selected_states:
        selected_states = []
    
    if triggered_id == 'relayoutData' and relayout_data:
        if 'mapbox.center' in relayout_data:
            camera_position['center'] = relayout_data['mapbox.center']
        if 'mapbox.zoom' in relayout_data:
            camera_position['zoom'] = relayout_data['mapbox.zoom']
    
    if triggered_id == 'clickData' and click_data:
        clicked_point = click_data['points'][0]
        if 'location' in clicked_point:
            clicked_state = clicked_point['location']
            if clicked_state in selected_states:
                selected_states.remove(clicked_state)
            else:
                selected_states.append(clicked_state)
    
    return selected_states, visualizer.create_map(selected_states, camera_position, age_range, month_range, day_range, year_range), camera_position

# Graphs callback
@app.callback(
    [Output('attacks-by-state', 'figure'),
     Output('yearly-trend', 'figure'),
     Output('activity-distribution', 'figure'),
     Output('shark-species', 'figure'),
     Output('quick-facts', 'children')],
    [Input('selected-states', 'data'),
     Input('age-slider', 'value'),
     Input('year-slider', 'value'),
     Input('month-slider', 'value'),
     Input('day-slider', 'value')]
)
def update_graphs(selected_states, age_range, year_range, month_range, day_range):
    facts = data_manager.get_quick_facts(selected_states, age_range, month_range, day_range, year_range)
    
    quick_facts_html = [
        html.H3('Quick Facts', style={'color': '#688ae8', 'marginTop': '20px'}),
        html.P(f"Total recorded attacks: {facts['total_attacks']}"),
        html.P(f"Year range: {facts['year_range']}"),
        html.P(f"Most dangerous state: {facts['most_dangerous_state']}"),
        html.P(f"Most common shark: {facts['most_common_shark']}")
    ]
    
    return (
        visualizer.create_attacks_by_state(selected_states, age_range, month_range, day_range, year_range),
        visualizer.create_yearly_trend(selected_states, age_range, month_range, day_range, year_range),
    visualizer.create_activity_distribution(selected_states, age_range, month_range, day_range, year_range),
        visualizer.create_shark_species(selected_states, age_range, month_range, day_range, year_range),
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