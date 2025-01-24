import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
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

    def create_map(self, selected_injuries: Optional[List[str]] = None,
                   selected_states: Optional[List[str]] = None,
                   camera_position: Optional[Dict] = None,
                   show_heatmap: bool = False,
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

        fig = go.Figure()

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
                    width=2, 
                    color='white'
                ),
                opacity=0.8 
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

        for feature in self.data_manager.geojson_data['features']:
            state_name = feature['properties']['STATE_NAME']
            if state_name in ['Tasmania', 'Victoria', 'Australian Capital Territory']:
                centroid = self.data_manager.state_centroids[state_name]
                fig.add_trace(go.Scattermapbox(
                    lat=[centroid['lat']],
                    lon=[centroid['lon']],
                    mode='markers',
                    marker=dict(
                        size=20,  
                        opacity=0, 
                    ),
                    name=state_name,
                    hovertemplate=f"Click to select {state_name}<extra></extra>",
                    showlegend=False,
                    customdata=[state_name]
                ))

        filtered_df = self.data_manager.filter_data(
            selected_injuries=selected_injuries,
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

        if show_heatmap:
            valid_coords = filtered_df.dropna(subset=['Latitude', 'Longitude'])
            fig.add_densitymapbox(
                lat=valid_coords['Latitude'],
                lon=valid_coords['Longitude'],
                z=valid_coords['Latitude'] * 0 + 1,  
                radius=20,
                colorscale=[
                    [0, 'rgba(0,0,255,0)'], 
                    [0.1, 'rgba(0,0,255,0.2)'], 
                    [0.3, 'rgba(0,255,255,0.4)'],
                    [0.5, 'rgba(0,255,0,0.6)'],
                    [0.7, 'rgba(255,255,0,0.8)'],
                    [1, 'rgba(255,0,0,1)']
                ],
                opacity=0.8,
                hoverinfo='none',
                showscale=False
            )
        else:
            for state in filtered_df['State'].unique():
                if state in STATE_COLORS:
                    state_data = filtered_df[
                        (filtered_df['State'] == state) &
                        filtered_df['Latitude'].notna() &
                        filtered_df['Longitude'].notna()
                        ]
                    if not state_data.empty:
                        fig.add_scattermapbox(
                            lat=state_data['Latitude'],
                            lon=state_data['Longitude'],
                            mode='markers',
                            marker=dict(
                                size=max(6 * (1.1 ** (camera_position['zoom'] - MAP_SETTINGS['default_zoom'])), 4),
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

        for state in filtered_df['State'].unique():
            if state in STATE_COLORS:
                state_data = filtered_df[filtered_df['State'] == state]
                fig.add_scattermapbox(
                    lat=state_data['Latitude'],
                    lon=state_data['Longitude'],
                    mode='markers',
                    marker=dict(
                        size=max(6 * (1.1 ** (camera_position['zoom'] - MAP_SETTINGS['default_zoom'])), 4),
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

        for state, centroid in self.data_manager.state_centroids.items():
            fig.add_scattermapbox(
                lat=[centroid['lat']],
                lon=[centroid['lon']],
                mode='text',
                text=[state],
                textfont=dict(
                    size=14,  
                    color=CHART_SETTINGS['font_color'],
                    weight='bold'  
                ),
                hoverinfo='none',
                showlegend=False
            )

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
            clickmode='event+select', 
            dragmode='zoom', 
            hoverdistance=5, 
            spikedistance=5
        )

        return fig

    def create_attacks_by_state(self, selected_injuries: Optional[List[str]] = None,
                            selected_states: Optional[List[str]] = None,
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
        """Create attacks by state bar chart with clickable bars."""
        attacks_by_state = self.data_manager.get_attacks_by_state(
            selected_injuries=selected_injuries,
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

        total_attacks = attacks_by_state.sum()
        percentages = (attacks_by_state / total_attacks * 100).round(1)

        colors = [
            STATE_COLORS.get(state, '#808080') if selected_states is None or state not in selected_states
            else '#36def7'
            for state in percentages.index
        ]

        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=percentages.index,
            y=percentages.values,
            marker_color=colors,
            text=[f'{val}%' for val in percentages.values],
            textposition='auto',
            customdata=percentages.index,
            hovertemplate='%{x}<br>%{y}% of attacks<extra></extra>',
        ))
        
        fig.update_layout(
            title='Percentage of Attacks by State',
            paper_bgcolor=CHART_SETTINGS['background_color'],
            plot_bgcolor=CHART_SETTINGS['background_color'],
            font=dict(color=CHART_SETTINGS['font_color']),
            margin=dict(l=10, r=10, t=40, b=10),
            height=LAYOUT_SETTINGS['chart_heights']['state_chart'],
            xaxis=dict(showgrid=False),
            yaxis=dict(showgrid=True, gridcolor=CHART_SETTINGS['grid_color']),
            clickmode='event+select'
        )
        return fig
    def create_activity_distribution(self, selected_injuries: Optional[List[str]] = None,
                                selected_states: Optional[List[str]] = None,
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
            selected_injuries=selected_injuries,
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

        colors = [
            '#36def7' if activity in (selected_activities or [])
            else CHART_SETTINGS['accent_color']
            for activity in top_activities.index
        ]

        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=top_activities.values,
            y=top_activities.index,
            orientation='h',
            marker_color=colors,
            text=[f"{val:.1f}%" for val in top_activities.values],
            textposition='auto',
            hovertemplate='%{y}: %{x:.1f}%<extra></extra>'
        ))

        fig.update_layout(
            title='Activity Distribution',
            paper_bgcolor=CHART_SETTINGS['background_color'],
            plot_bgcolor=CHART_SETTINGS['background_color'],
            font=dict(color=CHART_SETTINGS['font_color']),
            margin=dict(l=10, r=10, t=40, b=10),
            height=LAYOUT_SETTINGS['chart_heights']['activity_chart'],
            xaxis=dict(
                showgrid=True,
                gridcolor=CHART_SETTINGS['grid_color'],
                title='Percentage of Total Activities',
                range=[0, max(top_activities.values) * 1.1]
            ),
            yaxis=dict(showgrid=False),
            clickmode='event+select'
        )
        return fig
    def create_shark_species(self, selected_injuries: Optional[List[str]] = None,
                           selected_states: Optional[List[str]] = None,
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
            selected_injuries=selected_injuries,
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

    def create_hourly_distribution(self, selected_injuries: Optional[List[str]] = None,
                                   selected_states: Optional[List[str]] = None,
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
        """Create hourly distribution bar chart with percentages."""
        df_filtered = self.data_manager.filter_data(
            selected_injuries=selected_injuries,
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

        hourly_counts = [0] * 24

        for time_str in df_filtered['IncidentTime'].dropna():
            try:
                hour = int(time_str.split(':')[0])
                if 0 <= hour < 24:
                    hourly_counts[hour] += 1
            except (ValueError, IndexError):
                continue

        total_attacks = sum(hourly_counts)
        hourly_percentages = [(count / total_attacks * 100) if total_attacks > 0 else 0 for count in hourly_counts]

        hours = [f"{str(i).zfill(2)}:00" for i in range(24)]

        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=hours,
            y=hourly_percentages,
            marker_color=CHART_SETTINGS['accent_color'],
            text=[f'{val:.1f}%' for val in hourly_percentages],
            textposition='auto',
        ))

        fig.update_layout(
            title='Hourly Distribution of Attacks',
            paper_bgcolor=CHART_SETTINGS['background_color'],
            plot_bgcolor=CHART_SETTINGS['background_color'],
            font=dict(color=CHART_SETTINGS['font_color']),
            margin=dict(l=10, r=10, t=40, b=10),
            height=LAYOUT_SETTINGS['chart_heights']['state_chart'],
            xaxis=dict(
                showgrid=False,
                tickangle=-45,
            ),
            yaxis=dict(
                showgrid=True,
                gridcolor=CHART_SETTINGS['grid_color'],
                title='Percentage of Attacks'
            )
        )
        return fig

    def create_day_distribution(self, selected_injuries: Optional[List[str]] = None,
                                selected_states: Optional[List[str]] = None,
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
        """Create day of week distribution bar chart."""
        daily_dist = self.data_manager.get_day_distribution(
            selected_injuries=selected_injuries,
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
            x=daily_dist.index,
            y=daily_dist.values,
            marker_color=CHART_SETTINGS['accent_color'],
            text=[f'{val:.1f}%' for val in daily_dist.values],
            textposition='auto',
        ))

        fig.update_layout(
            title='Daily Distribution of Attacks',
            paper_bgcolor=CHART_SETTINGS['background_color'],
            plot_bgcolor=CHART_SETTINGS['background_color'],
            font=dict(color=CHART_SETTINGS['font_color']),
            margin=dict(l=10, r=10, t=40, b=10),
            height=LAYOUT_SETTINGS['chart_heights']['monthly_dist'],
            xaxis=dict(
                showgrid=False,
                tickangle=0
            ),
            yaxis=dict(
                showgrid=True,
                gridcolor=CHART_SETTINGS['grid_color'],
                title='Percentage of Attacks'
            )
        )
        return fig

    def create_monthly_distribution(self, selected_injuries: Optional[List[str]] = None,
                                    selected_states: Optional[List[str]] = None,
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
            selected_injuries=selected_injuries,
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

    def create_age_distribution(self, selected_injuries: Optional[List[str]] = None,
                                selected_states: Optional[List[str]] = None,
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
        """Create age distribution bar chart with percentages."""
        age_dist = self.data_manager.get_age_distribution(
            selected_injuries=selected_injuries,
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
            text=[f'{val:.1f}%' for val in age_dist.values],
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
                title='Percentage of Attacks'
            )
        )
        return fig

    def create_shark_streamgraph(self, selected_injuries: Optional[List[str]] = None,
                                 selected_states: Optional[List[str]] = None,
                                 age_range: Optional[List[float]] = None,
                                 year_range: Optional[List[int]] = None,
                                 selected_days: Optional[List[str]] = None,
                                 selected_genders: Optional[List[str]] = None,
                                 selected_months: Optional[List[int]] = None,
                                 selected_activities: Optional[List[str]] = None,
                                 selected_time_periods: Optional[List[str]] = None,
                                 selected_sharks: Optional[List[str]] = None) -> go.Figure:
        """Create streamgraph of shark attacks over time by species."""
        # Get filtered data
        df_filtered = self.data_manager.filter_data(
            selected_injuries=selected_injuries,
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

        yearly_species = df_filtered.groupby(['Year', 'SharkName']).size().reset_index(name='Attacks')

        top_sharks = df_filtered['SharkName'].value_counts().nlargest(6).index

        yearly_species = yearly_species[yearly_species['SharkName'].isin(top_sharks)]

        pivot_data = yearly_species.pivot(index='Year', columns='SharkName', values='Attacks').fillna(0)

        pivot_data['sum'] = pivot_data.sum(axis=1)
        pivot_data['baseline'] = -pivot_data['sum'] / 2
        y_offsets = pivot_data['baseline'].cumsum()

        fig = go.Figure()

        y_cumulative = pivot_data['baseline']
        for shark in pivot_data.columns[:-2]: 
            shark_colors = {
                'white shark': '#004D40',
                'tiger shark': '#1E88E5',
                'bull shark': '#6C6509',
                'whaler shark': '#826252',
                'wobbegong': '#D81B60',
                'bronze whaler shark': '#FFC107'
            }

            fig.add_trace(go.Scatter(
                x=pivot_data.index,
                y=y_cumulative + pivot_data[shark],
                name=shark,
                mode='lines',
                fill='tonexty',
                fillcolor=shark_colors.get(shark, '#808080'),
                line=dict(width=0.5, color=shark_colors.get(shark, '#808080')),
                hovertemplate="Attacks: %{customdata}<extra>%{fullData.name}</extra>",
                customdata=[abs(value) for value in pivot_data[shark]],
            ))
            y_cumulative += pivot_data[shark]

        fig.update_layout(
            title='Shark Attacks by Species Over Time',
            showlegend=True,
            paper_bgcolor=CHART_SETTINGS['background_color'],
            plot_bgcolor=CHART_SETTINGS['background_color'],
            font=dict(color=CHART_SETTINGS['font_color']),
            hovermode='x unified',
            margin=dict(l=10, r=10, t=40, b=10),
            height=400, 
            yaxis=dict(
                showgrid=True,
                gridcolor=CHART_SETTINGS['grid_color'],
                title='Number of Attacks',
                zeroline=False,
                showticklabels=False
            ),
            xaxis=dict(
                showgrid=False,
                title='Year'
            ),
            legend=dict(
                bgcolor='rgba(0,0,0,0.7)',
                font=dict(color=CHART_SETTINGS['font_color']),
                x=0.02,
                y=0.98,
                xanchor='left',
                yanchor='top',
                bordercolor='rgba(255,255,255,0.2)',
                borderwidth=1
            )
        )

        return fig

    def create_provocation_distribution(self, selected_injuries: Optional[List[str]] = None,
                                        selected_states: Optional[List[str]] = None,
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
        """Create grouped bar chart for activities and provocation."""
        df_filtered = self.data_manager.filter_data(
            selected_injuries=selected_injuries,
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

        activity_provocation = df_filtered.groupby(['Activity', 'Provocation']).size().unstack(fill_value=0)

        activity_provocation['total'] = activity_provocation.sum(axis=1)
        top_10_activities = activity_provocation.nlargest(10, 'total')

        fig = go.Figure()

        fig.add_trace(go.Bar(
            name='Provoked',
            x=top_10_activities.index,
            y=top_10_activities['provoked'],
            marker_color='#ef4444'
        ))

        fig.add_trace(go.Bar(
            name='Unprovoked',
            x=top_10_activities.index,
            y=top_10_activities['unprovoked'],
            marker_color='#3b82f6'
        ))

        fig.update_layout(
            title='Activity Distribution by Provocation',
            barmode='group',
            paper_bgcolor=CHART_SETTINGS['background_color'],
            plot_bgcolor=CHART_SETTINGS['background_color'],
            font=dict(color=CHART_SETTINGS['font_color']),
            margin=dict(l=10, r=10, t=40, b=10),
            height=LAYOUT_SETTINGS['chart_heights']['activity_chart'],
            xaxis=dict(
                showgrid=False,
                tickangle=-45,
                title='Activity'
            ),
            yaxis=dict(
                showgrid=True,
                gridcolor=CHART_SETTINGS['grid_color'],
                title='Number of Incidents'
            ),
            legend=dict(
                yanchor="top",
                y=0.99,
                xanchor="right",
                x=0.99,
                bgcolor='rgba(0,0,0,0.5)'
            )
        )

        return fig

    def create_population_pyramid(self, selected_injuries: Optional[List[str]] = None,
                                  selected_states=None, age_range=None,
                                  month_range=None, day_range=None, year_range=None,
                                  selected_days=None, selected_genders=None,
                                  selected_months=None, selected_activities=None,
                                  selected_time_periods=None, selected_sharks=None):
        """Create population pyramid showing gender and provocation distribution by age."""
        df_counts = self.data_manager.get_gender_age_provocation_distribution(
            selected_injuries=selected_injuries,
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
            x=-df_counts['Male_Provoked'],
            y=df_counts.index,
            name='Male (Provoked)',
            orientation='h',
            marker_color='#1d4ed8',
            hovertemplate='%{customdata} provoked incidents<br>Age group: %{y}<extra></extra>',
            customdata=df_counts['Male_Provoked'].abs().values
        ))

        fig.add_trace(go.Bar(
            x=-df_counts['Male_Unprovoked'],
            y=df_counts.index,
            name='Male (Unprovoked)',
            orientation='h',
            marker_color='#60a5fa',
            hovertemplate='%{customdata} unprovoked incidents<br>Age group: %{y}<extra></extra>',
            customdata=df_counts['Male_Unprovoked'].abs().values
        ))

        fig.add_trace(go.Bar(
            x=df_counts['Female_Provoked'],
            y=df_counts.index,
            name='Female (Provoked)',
            orientation='h',
            marker_color='#be185d',
            hovertemplate='%{customdata} provoked incidents<br>Age group: %{y}<extra></extra>',
            customdata=df_counts['Female_Provoked'].values
        ))

        fig.add_trace(go.Bar(
            x=df_counts['Female_Unprovoked'],
            y=df_counts.index,
            name='Female (Unprovoked)',
            orientation='h',
            marker_color='#f472b6',
            hovertemplate='%{customdata} unprovoked incidents<br>Age group: %{y}<extra></extra>',
            customdata=df_counts['Female_Unprovoked'].values
        ))

        max_value = max(
            abs(df_counts['Male_Provoked'] + df_counts['Male_Unprovoked']).max(),
            (df_counts['Female_Provoked'] + df_counts['Female_Unprovoked']).max()
        )

        fig.update_layout(
            title='Gender and Provocation Distribution by Age',
            barmode='relative',
            bargap=0.1,
            paper_bgcolor=CHART_SETTINGS['background_color'],
            plot_bgcolor=CHART_SETTINGS['background_color'],
            font=dict(color=CHART_SETTINGS['font_color']),
            margin=dict(l=10, r=10, t=40, b=10),
            height=400,
            xaxis=dict(
                title='Number of Incidents',
                showgrid=True,
                gridcolor=CHART_SETTINGS['grid_color'],
                range=[-max_value * 1.1, max_value * 1.1],
                zeroline=True,
                zerolinecolor=CHART_SETTINGS['grid_color'],
                tickformat=',.0f',
                ticktext=[str(abs(int(x))) for x in range(-int(max_value), int(max_value) + 1, 50)],
                tickvals=list(range(-int(max_value), int(max_value) + 1, 50))
            ),
            yaxis=dict(
                title='Age Group',
                showgrid=False
            ),
            showlegend=True,
            legend=dict(
                yanchor="top",
                y=0.99,
                xanchor="right",
                x=0.99,
                bgcolor='rgba(0,0,0,0.5)',
                font=dict(size=10)
            )
        )

        return fig
