import plotly.graph_objects as go
import plotly.express as px
from typing import Dict, List, Optional
from config import (
    STATE_COLORS,
    MAP_SETTINGS,
    CHART_SETTINGS,
    LAYOUT_SETTINGS
)

class DashboardVisualizer:
    def __init__(self, data_manager):
        """Initialize visualizer with data manager."""
        self.data_manager = data_manager

    def create_map(self, selected_states: Optional[List[str]] = None,
                  camera_position: Optional[Dict] = None,
                  age_range: Optional[List[float]] = None,
                  month_range: Optional[List[int]] = None,
                  day_range: Optional[List[int]] = None,
                  year_range: Optional[List[int]] = None) -> go.Figure:
        """Create the main map visualization."""
        if selected_states is None:
            selected_states = []
        
        if camera_position is None:
            camera_position = {
                'center': MAP_SETTINGS['default_center'],
                'zoom': MAP_SETTINGS['default_zoom']
            }
        
        # Create base figure
        fig = go.Figure()

        # Add choropleth layer for unselected states
        fig.add_trace(go.Choroplethmapbox(
            geojson=self.data_manager.geojson_data,
            locations=[feat['properties']['STATE_NAME'] 
                      for feat in self.data_manager.geojson_data['features']],
            z=[1] * len(self.data_manager.geojson_data['features']),
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
                         for feat in self.data_manager.geojson_data['features']]
            
            fig.add_trace(go.Choroplethmapbox(
                geojson=self.data_manager.geojson_data,
                locations=[feat['properties']['STATE_NAME'] 
                          for feat in self.data_manager.geojson_data['features']],
                z=z_selected,
                featureidkey="properties.STATE_NAME",
                colorscale=[[0, 'rgba(101,194,255,0)'], [1, 'rgba(101,194,255,0.2)']],
                showscale=False,
                hovertemplate=None,
                hoverinfo='none',
                marker_line_width=1,
                marker_line_color='white'
            ))

        # Add shark attack points with filtering
        filtered_df = self.data_manager.filter_data(
            selected_states=selected_states,
            age_range=age_range,
            month_range=month_range,
            day_range=day_range,
            year_range=year_range
        )
        
        for state in filtered_df['State'].unique():
            if state in STATE_COLORS:
                state_data = filtered_df[filtered_df['State'] == state]
                fig.add_scattermapbox(
                    lat=state_data['Latitude'],
                    lon=state_data['Longitude'],
                    mode='markers',
                    marker=dict(
                        size=8,
                        color=STATE_COLORS[state],
                        symbol='circle',
                        opacity=0.8
                    ),
                    name=state,
                    text=state_data['hover_text'],
                    hoverinfo='text',
                    hoverlabel=dict(
                        bgcolor=CHART_SETTINGS['hover_bgcolor'],
                        bordercolor=CHART_SETTINGS['hover_bordercolor'],
                        font=dict(color=CHART_SETTINGS['font_color'], size=12)
                    ),
                    showlegend=False
                )

        # Add state labels
        for state, centroid in self.data_manager.state_centroids.items():
            fig.add_scattermapbox(
                lat=[centroid['lat']],
                lon=[centroid['lon']],
                mode='text',
                text=[state],
                textfont=dict(size=12, color=CHART_SETTINGS['font_color']),
                hoverinfo='none',
                showlegend=False
            )

        # Update layout
        fig.update_layout(
            margin={"r": 0, "t": 0, "l": 0, "b": 0},
            paper_bgcolor=CHART_SETTINGS['background_color'],
            plot_bgcolor=CHART_SETTINGS['background_color'],
            mapbox=dict(
                style=MAP_SETTINGS['style'],
                center=camera_position['center'],
                zoom=camera_position['zoom']
            ),
            showlegend=False
        )
        
        return fig

    def create_attacks_by_state(self, selected_states: Optional[List[str]] = None,
                              age_range: Optional[List[float]] = None,
                              month_range: Optional[List[int]] = None,
                              day_range: Optional[List[int]] = None,
                              year_range: Optional[List[int]] = None) -> go.Figure:
        """Create attacks by state bar chart."""
        attacks_by_state = self.data_manager.get_attacks_by_state(
            selected_states, age_range, month_range, day_range, year_range
        )
        
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=attacks_by_state.index,
            y=attacks_by_state.values,
            marker_color=[STATE_COLORS.get(state, '#808080') for state in attacks_by_state.index],
            text=attacks_by_state.values,
            textposition='auto',
        ))
        
        fig.update_layout(
            title='Attacks by State',
            paper_bgcolor=CHART_SETTINGS['background_color'],
            plot_bgcolor=CHART_SETTINGS['background_color'],
            font=dict(color=CHART_SETTINGS['font_color']),
            margin=dict(l=10, r=10, t=40, b=10),
            height=LAYOUT_SETTINGS['chart_heights']['state_chart'],
            xaxis=dict(showgrid=False),
            yaxis=dict(showgrid=True, gridcolor=CHART_SETTINGS['grid_color'])
        )
        return fig

    def create_yearly_trend(self, selected_states: Optional[List[str]] = None,
                          age_range: Optional[List[float]] = None,
                          month_range: Optional[List[int]] = None,
                          day_range: Optional[List[int]] = None,
                          year_range: Optional[List[int]] = None) -> go.Figure:
        """Create yearly trend line chart."""
        yearly_attacks = self.data_manager.get_yearly_trend(
            selected_states, age_range, month_range, day_range, year_range
        )
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=yearly_attacks.index,
            y=yearly_attacks.values,
            mode='lines+markers',
            line=dict(color=CHART_SETTINGS['accent_color']),
            hovertemplate='Year: %{x}<br>Attacks: %{y}<extra></extra>'
        ))
        
        fig.update_layout(
            title='Yearly Trend of Attacks',
            paper_bgcolor=CHART_SETTINGS['background_color'],
            plot_bgcolor=CHART_SETTINGS['background_color'],
            font=dict(color=CHART_SETTINGS['font_color']),
            margin=dict(l=10, r=10, t=40, b=10),
            height=LAYOUT_SETTINGS['chart_heights']['yearly_trend'],
            xaxis=dict(showgrid=False),
            yaxis=dict(showgrid=True, gridcolor=CHART_SETTINGS['grid_color'])
        )
        return fig

    def create_activity_distribution(self, selected_states: Optional[List[str]] = None,
                                   age_range: Optional[List[float]] = None,
                                   month_range: Optional[List[int]] = None,
                                   day_range: Optional[List[int]] = None,
                                   year_range: Optional[List[int]] = None) -> go.Figure:
        """Create activity distribution bar chart."""
        top_activities = self.data_manager.get_activity_distribution(
            selected_states, age_range, month_range, day_range, year_range
        )
        
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=top_activities.values,
            y=top_activities.index,
            orientation='h',
            marker_color=CHART_SETTINGS['accent_color'],
            text=top_activities.values,
            textposition='auto',
        ))
        
        fig.update_layout(
            title='Most Common Activities',
            paper_bgcolor=CHART_SETTINGS['background_color'],
            plot_bgcolor=CHART_SETTINGS['background_color'],
            font=dict(color=CHART_SETTINGS['font_color']),
            margin=dict(l=10, r=10, t=40, b=10),
            height=LAYOUT_SETTINGS['chart_heights']['activity_chart'],
            xaxis=dict(showgrid=False),
            yaxis=dict(showgrid=False)
        )
        return fig

    def create_shark_species(self, selected_states: Optional[List[str]] = None,
                           age_range: Optional[List[float]] = None,
                           month_range: Optional[List[int]] = None,
                           day_range: Optional[List[int]] = None,
                           year_range: Optional[List[int]] = None) -> go.Figure:
        """Create shark species distribution pie chart."""
        top_sharks = self.data_manager.get_shark_species_distribution(
            selected_states, age_range, month_range, day_range, year_range
        )
        
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
            paper_bgcolor=CHART_SETTINGS['background_color'],
            plot_bgcolor=CHART_SETTINGS['background_color'],
            font=dict(color=CHART_SETTINGS['font_color']),
            margin=dict(l=10, r=10, t=40, b=10),
            height=LAYOUT_SETTINGS['chart_heights']['species_chart'],
            showlegend=False
        )
        return fig