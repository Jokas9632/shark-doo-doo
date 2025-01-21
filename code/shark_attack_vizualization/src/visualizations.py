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
                   year_range: Optional[List[int]] = None,
                   selected_days: Optional[List[str]] = None,
                   selected_genders: Optional[List[str]] = None,
                   selected_months: Optional[List[int]] = None,
                   selected_activities: Optional[List[str]] = None,
                   selected_time_periods: Optional[List[str]] = None,
                   selected_sharks: Optional[List[str]] = None) -> go.Figure:
        """Create the main map visualization with improved state selection."""
        if selected_states is None:
            selected_states = []

        if camera_position is None:
            camera_position = {
                'center': MAP_SETTINGS['default_center'],
                'zoom': MAP_SETTINGS['default_zoom']
            }

        # Create base figure
        fig = go.Figure()

        # Add choropleth layer for all states with improved interaction
        fig.add_trace(go.Choroplethmapbox(
            geojson=self.data_manager.geojson_data,
            locations=[feat['properties']['STATE_NAME']
                       for feat in self.data_manager.geojson_data['features']],
            z=[1 if feat['properties']['STATE_NAME'] in selected_states else 0
               for feat in self.data_manager.geojson_data['features']] if selected_states else [0] * len(
                self.data_manager.geojson_data['features']),
            featureidkey="properties.STATE_NAME",
            colorscale=[[0, 'rgba(255,255,255,0)'], [1, 'rgba(101,194,255,0.4)']],
            showscale=False,
            hoverinfo='none',
            marker=dict(
                line=dict(
                    width=2,  # Increased line width
                    color='white'
                ),
                opacity=0.8  # Increased opacity
            ),
            selected=dict(
                marker=dict(
                    opacity=1
                )
            ),
            unselected=dict(
                marker=dict(
                    opacity=0.3
                )
            )
        ))

        # Add invisible larger clickable areas for small states
        for feature in self.data_manager.geojson_data['features']:
            state_name = feature['properties']['STATE_NAME']
            # Add a slightly larger transparent area for better clickability
            if state_name in ['Tasmania', 'Victoria', 'Australian Capital Territory']:
                centroid = self.data_manager.state_centroids[state_name]
                fig.add_trace(go.Scattermapbox(
                    lat=[centroid['lat']],
                    lon=[centroid['lon']],
                    mode='markers',
                    marker=dict(
                        size=20,  # Larger clickable area
                        opacity=0,  # Invisible
                    ),
                    name=state_name,
                    hovertemplate=f"Click to select {state_name}<extra></extra>",
                    showlegend=False,
                    customdata=[state_name]
                ))

        # Add shark attack points with filtering
        filtered_df = self.data_manager.filter_data(
            selected_states=selected_states,
            age_range=age_range,
            month_range=month_range,
            day_range=day_range,
            year_range=year_range,
            selected_days=selected_days,
            selected_genders=selected_genders,
            selected_months=selected_months,
            selected_activities=selected_activities,
            selected_time_periods=selected_time_periods,
            selected_sharks=selected_sharks
        )

        # Add shark attack points with reduced size and opacity
        for state in filtered_df['State'].unique():
            if state in STATE_COLORS:
                state_data = filtered_df[filtered_df['State'] == state]
                fig.add_scattermapbox(
                    lat=state_data['Latitude'],
                    lon=state_data['Longitude'],
                    mode='markers',
                    marker=dict(
                        size=6,  # Reduced size
                        color=STATE_COLORS[state],
                        symbol='circle',
                        opacity=0.8  # Reduced opacity
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

        # Add state labels with improved visibility
        for state, centroid in self.data_manager.state_centroids.items():
            fig.add_scattermapbox(
                lat=[centroid['lat']],
                lon=[centroid['lon']],
                mode='text',
                text=[state],
                textfont=dict(
                    size=14,  # Increased font size
                    color=CHART_SETTINGS['font_color'],
                    weight='bold'  # Added bold weight
                ),
                hoverinfo='none',
                showlegend=False
            )

        # Update layout with improved interaction settings
        fig.update_layout(
            margin={"r": 0, "t": 0, "l": 0, "b": 0},
            paper_bgcolor=CHART_SETTINGS['background_color'],
            plot_bgcolor=CHART_SETTINGS['background_color'],
            mapbox=dict(
                style=MAP_SETTINGS['style'],
                center=camera_position['center'],
                zoom=camera_position['zoom'],
                bearing=0,
                pitch=0
            ),
            showlegend=False,
            clickmode='event+select',  # Enable both click events and selection
            dragmode='zoom',  # Set default drag mode to zoom
            hoverdistance=5,  # Reduce hover distance for more precise selection
            spikedistance=5  # Reduce spike distance for more precise selection
        )

        return fig

    def create_attacks_by_state(self, selected_states: Optional[List[str]] = None,
                              age_range: Optional[List[float]] = None,
                              month_range: Optional[List[int]] = None,
                              day_range: Optional[List[int]] = None,
                              year_range: Optional[List[int]] = None,
                              selected_days: Optional[List[str]] = None,
                              selected_genders: Optional[List[str]] = None,
                              selected_months: Optional[List[int]] = None,
                              selected_activities: Optional[List[str]] = None,
                              selected_time_periods: Optional[List[str]] = None,
                              selected_sharks: Optional[List[str]] = None) -> go.Figure:
        """Create attacks by state bar chart."""
        attacks_by_state = self.data_manager.get_attacks_by_state(
            selected_states=selected_states,
            age_range=age_range,
            month_range=month_range,
            day_range=day_range,
            year_range=year_range,
            selected_days=selected_days,
            selected_genders=selected_genders,
            selected_months=selected_months,
            selected_activities=selected_activities,
            selected_time_periods=selected_time_periods,
            selected_sharks=selected_sharks
        )

        # Calculate percentages
        total_attacks = attacks_by_state.sum()
        percentages = (attacks_by_state / total_attacks * 100).round(1)

        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=percentages.index,
            y=percentages.values,
            marker_color=[STATE_COLORS.get(state, '#808080') for state in percentages.index],
            text=[f'{val}%' for val in percentages.values],
            textposition='auto',
        ))
        
        fig.update_layout(
            title='Percentage of Attacks by State',
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
                          year_range: Optional[List[int]] = None,
                          selected_days: Optional[List[str]] = None,
                          selected_genders: Optional[List[str]] = None,
                          selected_months: Optional[List[int]] = None,
                          selected_activities: Optional[List[str]] = None,
                          selected_time_periods: Optional[List[str]] = None,
                          selected_sharks: Optional[List[str]] = None) -> go.Figure:
        """Create yearly trend line chart."""
        yearly_attacks = self.data_manager.get_yearly_trend(
            selected_states=selected_states,
            age_range=age_range,
            month_range=month_range,
            day_range=day_range,
            year_range=year_range,
            selected_days=selected_days,
            selected_genders=selected_genders,
            selected_months=selected_months,
            selected_activities=selected_activities,
            selected_time_periods=selected_time_periods,
            selected_sharks=selected_sharks
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
                                   year_range: Optional[List[int]] = None,
                                   selected_days: Optional[List[str]] = None,
                                   selected_genders: Optional[List[str]] = None,
                                   selected_months: Optional[List[int]] = None,
                                   selected_activities: Optional[List[str]] = None,
                                   selected_time_periods: Optional[List[str]] = None,
                                   selected_sharks: Optional[List[str]] = None) -> go.Figure:
        """Create activity distribution bar chart."""
        top_activities = self.data_manager.get_activity_distribution(
            selected_states=selected_states,
            age_range=age_range,
            month_range=month_range,
            day_range=day_range,
            year_range=year_range,
            selected_days=selected_days,
            selected_genders=selected_genders,
            selected_months=selected_months,
            selected_activities=selected_activities,
            selected_time_periods=selected_time_periods,
            selected_sharks=selected_sharks
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
                           year_range: Optional[List[int]] = None,
                           selected_days: Optional[List[str]] = None,
                           selected_genders: Optional[List[str]] = None,
                           selected_months: Optional[List[int]] = None,
                           selected_activities: Optional[List[str]] = None,
                           selected_time_periods: Optional[List[str]] = None,
                           selected_sharks: Optional[List[str]] = None) -> go.Figure:
        """Create shark species distribution pie chart."""
        top_sharks = self.data_manager.get_shark_species_distribution(
            selected_states=selected_states,
            age_range=age_range,
            month_range=month_range,
            day_range=day_range,
            year_range=year_range,
            selected_days=selected_days,
            selected_genders=selected_genders,
            selected_months=selected_months,
            selected_activities=selected_activities,
            selected_time_periods=selected_time_periods,
            selected_sharks=selected_sharks
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

    def create_hourly_distribution(self, selected_states: Optional[List[str]] = None,
                                   age_range: Optional[List[float]] = None,
                                   month_range: Optional[List[int]] = None,
                                   day_range: Optional[List[int]] = None,
                                   year_range: Optional[List[int]] = None,
                                   selected_days: Optional[List[str]] = None,
                                   selected_genders: Optional[List[str]] = None,
                                   selected_months: Optional[List[int]] = None,
                                   selected_activities: Optional[List[str]] = None,
                                   selected_time_periods: Optional[List[str]] = None,
                                   selected_sharks: Optional[List[str]] = None) -> go.Figure:
        """Create hourly distribution bar chart."""
        df_filtered = self.data_manager.filter_data(
            selected_states=selected_states,
            age_range=age_range,
            month_range=month_range,
            day_range=day_range,
            year_range=year_range,
            selected_days=selected_days,
            selected_genders=selected_genders,
            selected_months=selected_months,
            selected_activities=selected_activities,
            selected_time_periods=selected_time_periods,
            selected_sharks=selected_sharks
        )

        # Create hourly bins
        hourly_counts = [0] * 24

        # Count incidents per hour
        for time_str in df_filtered['IncidentTime'].dropna():
            try:
                hour = int(time_str.split(':')[0])
                if 0 <= hour < 24:
                    hourly_counts[hour] += 1
            except (ValueError, IndexError):
                continue

        # Create x-axis labels
        hours = [f"{str(i).zfill(2)}:00" for i in range(24)]

        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=hours,
            y=hourly_counts,
            marker_color=CHART_SETTINGS['accent_color'],
            text=hourly_counts,
            textposition='auto',
        ))

        fig.update_layout(
            title='Attacks by Hour of Day',
            paper_bgcolor=CHART_SETTINGS['background_color'],
            plot_bgcolor=CHART_SETTINGS['background_color'],
            font=dict(color=CHART_SETTINGS['font_color']),
            margin=dict(l=10, r=10, t=40, b=10),
            height=LAYOUT_SETTINGS['chart_heights']['state_chart'],
            xaxis=dict(
                showgrid=False,
                tickangle=-45,
                title='Hour of Day'
            ),
            yaxis=dict(
                showgrid=True,
                gridcolor=CHART_SETTINGS['grid_color'],
                title='Number of Attacks'
            )
        )

        return fig

    def create_monthly_distribution(self, selected_states: Optional[List[str]] = None,
                                    age_range: Optional[List[float]] = None,
                                    month_range: Optional[List[int]] = None,
                                    day_range: Optional[List[int]] = None,
                                    year_range: Optional[List[int]] = None,
                                    selected_days: Optional[List[str]] = None,
                                    selected_genders: Optional[List[str]] = None,
                                    selected_months: Optional[List[int]] = None,
                                    selected_activities: Optional[List[str]] = None,
                                    selected_time_periods: Optional[List[str]] = None,
                                    selected_sharks: Optional[List[str]] = None) -> go.Figure:
        """Create monthly distribution bar chart."""
        monthly_dist = self.data_manager.get_monthly_distribution(
            selected_states=selected_states,
            age_range=age_range,
            month_range=month_range,
            day_range=day_range,
            year_range=year_range,
            selected_days=selected_days,
            selected_genders=selected_genders,
            selected_months=selected_months,
            selected_activities=selected_activities,
            selected_time_periods=selected_time_periods,
            selected_sharks=selected_sharks
        )

        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=monthly_dist.index,
            y=monthly_dist.values,
            marker_color=CHART_SETTINGS['accent_color'],
            text=[f'{val:.1f}%' for val in monthly_dist.values],
            textposition='auto',
        ))

        fig.update_layout(
            title='Monthly Distribution of Attacks',
            paper_bgcolor=CHART_SETTINGS['background_color'],
            plot_bgcolor=CHART_SETTINGS['background_color'],
            font=dict(color=CHART_SETTINGS['font_color']),
            margin=dict(l=10, r=10, t=40, b=10),
            height=LAYOUT_SETTINGS['chart_heights']['monthly_dist'],
            xaxis=dict(
                showgrid=False,
                tickangle=45
            ),
            yaxis=dict(
                showgrid=True,
                gridcolor=CHART_SETTINGS['grid_color'],
                title='Percentage of Attacks'
            )
        )
        return fig

    def create_age_distribution(self, selected_states: Optional[List[str]] = None,
                                age_range: Optional[List[float]] = None,
                                month_range: Optional[List[int]] = None,
                                day_range: Optional[List[int]] = None,
                                year_range: Optional[List[int]] = None,
                                selected_days: Optional[List[str]] = None,
                                selected_genders: Optional[List[str]] = None,
                                selected_months: Optional[List[int]] = None,
                                selected_activities: Optional[List[str]] = None,
                                selected_time_periods: Optional[List[str]] = None,
                                selected_sharks: Optional[List[str]] = None) -> go.Figure:
        """Create age distribution bar chart."""
        age_dist = self.data_manager.get_age_distribution(
            selected_states=selected_states,
            age_range=age_range,
            month_range=month_range,
            day_range=day_range,
            year_range=year_range,
            selected_days=selected_days,
            selected_genders=selected_genders,
            selected_months=selected_months,
            selected_activities=selected_activities,
            selected_time_periods=selected_time_periods,
            selected_sharks=selected_sharks
        )

        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=age_dist.index,
            y=age_dist.values,
            marker_color=CHART_SETTINGS['accent_color'],
            text=age_dist.values,
            textposition='auto',
        ))

        fig.update_layout(
            title='Age Distribution of Attacks',
            paper_bgcolor=CHART_SETTINGS['background_color'],
            plot_bgcolor=CHART_SETTINGS['background_color'],
            font=dict(color=CHART_SETTINGS['font_color']),
            margin=dict(l=10, r=10, t=40, b=10),
            height=200,
            xaxis=dict(
                showgrid=False,
                title='Age Groups'
            ),
            yaxis=dict(
                showgrid=True,
                gridcolor=CHART_SETTINGS['grid_color'],
                title='Number of Attacks'
            )
        )
        return fig
