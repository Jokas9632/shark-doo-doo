import pandas as pd
import json
from shapely.geometry import shape
from typing import Dict, List, Optional
from config import (
    DATA_PATHS,
    DATA_SETTINGS,
    REVERSE_STATE_MAPPING,
)

class DataManager:
    def __init__(self):
        """Initialize DataManager with empty data structures."""
        self.df = pd.read_csv(DATA_PATHS['csv_file'])
        self.geojson_data = self._load_geojson()
        self.state_centroids = self._calculate_state_centroids()
        self._add_day_of_week()
        self._create_hover_text()

    def _load_geojson(self) -> Dict:
        """Load GeoJSON data for Australian states."""
        with open(DATA_PATHS['geojson_file']) as f:
            return json.load(f)

    def _calculate_state_centroids(self) -> Dict:
        """Calculate centroids for each state for label placement."""
        centroids = {}
        for feature in self.geojson_data['features']:
            state_name = feature['properties']['STATE_NAME']
            geometry = shape(feature['geometry'])
            centroid = geometry.centroid
            centroids[state_name] = {
                'lat': centroid.y,
                'lon': centroid.x
            }
        return centroids

    def _add_day_of_week(self):
        """Add day of week column based on Year, Month, and Day."""
        self.df['Date'] = pd.to_datetime(
            self.df[['Year', 'Month', 'Day']].assign(Day=self.df['Day'].fillna(1)),
            format='%Y%m%d',
            errors='coerce'
        )
        self.df['DayOfWeek'] = self.df['Date'].dt.day_name()

    def _create_hover_text(self) -> None:
        """Create hover text for map points."""
        self.df['hover_text'] = self.df.apply(
            lambda row: f"""
<b>Year:</b> {int(row['Year']) if pd.notnull(row['Year']) else 'Unknown'}<br>
<b>Shark Species:</b> {row['SharkName'] if pd.notnull(row['SharkName']) else 'Unknown'}<br>
<b>Activity:</b> {row['Activity'] if pd.notnull(row['Activity']) else 'Unknown'}<br>
<b>Injury:</b> {row['Injury'] if pd.notnull(row['Injury']) else 'Unknown'}<br>
<b>Gender:</b> {row['Gender'] if pd.notnull(row['Gender']) else 'Unknown'}<br>
<b>Age:</b> {int(row['Age']) if pd.notnull(row['Age']) else 'Unknown'}
""",
            axis=1
        )

    def filter_data(self, selected_states: Optional[List[str]] = None,
                   age_range: Optional[List[float]] = None,
                   month_range: Optional[List[int]] = None,
                   day_range: Optional[List[int]] = None,
                   year_range: Optional[List[int]] = None,
                   selected_days: Optional[List[str]] = None,
                   selected_genders: Optional[List[str]] = None,
                   selected_months: Optional[List[int]] = None,
                   selected_activities: Optional[List[str]] = None) -> pd.DataFrame:
        """Filter data based on selected criteria."""
        df_filtered = self.df.copy()
        
        if selected_states:
            selected_short_states = [REVERSE_STATE_MAPPING[state] 
                               for state in selected_states]
            df_filtered = df_filtered[df_filtered['State'].isin(selected_short_states)]
        
        if age_range:
            df_filtered = df_filtered[
                (df_filtered['Age'] >= age_range[0]) & 
                (df_filtered['Age'] <= age_range[1])
            ]
        
        if month_range:
            df_filtered = df_filtered[
                (df_filtered['Month'] >= month_range[0]) & 
                (df_filtered['Month'] <= month_range[1])
            ]
        
        if day_range:
            df_filtered = df_filtered[
                (df_filtered['Day'] >= day_range[0]) & 
                (df_filtered['Day'] <= day_range[1])
            ]
        
        if year_range:
            df_filtered = df_filtered[
                (df_filtered['Year'] >= year_range[0]) & 
                (df_filtered['Year'] <= year_range[1])
            ]

        if selected_days and len(selected_days) > 0:
            df_filtered = df_filtered[df_filtered['DayOfWeek'].isin(selected_days)]
            
        if selected_genders and len(selected_genders) > 0:
            df_filtered = df_filtered[df_filtered['Gender'].isin(selected_genders)]
            
        if selected_months and len(selected_months) > 0:
            df_filtered = df_filtered[df_filtered['Month'].isin(selected_months)]
            
        if selected_activities and len(selected_activities) > 0:
            df_filtered = df_filtered[df_filtered['Activity'].isin(selected_activities)]
        
        return df_filtered

    def get_quick_facts(self, selected_states: Optional[List[str]] = None,
                       age_range: Optional[List[float]] = None,
                       month_range: Optional[List[int]] = None,
                       day_range: Optional[List[int]] = None,
                       year_range: Optional[List[int]] = None,
                       selected_days: Optional[List[str]] = None,
                       selected_genders: Optional[List[str]] = None,
                       selected_months: Optional[List[int]] = None,
                       selected_activities: Optional[List[str]] = None) -> Dict:
        """Get quick facts about the data."""
        df_filtered = self.filter_data(
            selected_states=selected_states,
            age_range=age_range,
            month_range=month_range,
            day_range=day_range,
            year_range=year_range,
            selected_days=selected_days,
            selected_genders=selected_genders,
            selected_months=selected_months,
            selected_activities=selected_activities
        )
        
        return {
            'total_attacks': len(df_filtered),
            'year_range': f"{df_filtered['Year'].min()} - {df_filtered['Year'].max()}",
            'most_dangerous_state': df_filtered['State'].mode().iloc[0] if not df_filtered.empty else 'N/A',
            'most_common_shark': df_filtered['SharkName'].mode().iloc[0] if not df_filtered.empty else 'N/A'
        }

    def get_attacks_by_state(self, selected_states: Optional[List[str]] = None,
                           age_range: Optional[List[float]] = None,
                           month_range: Optional[List[int]] = None,
                           day_range: Optional[List[int]] = None,
                           year_range: Optional[List[int]] = None,
                           selected_days: Optional[List[str]] = None,
                           selected_genders: Optional[List[str]] = None,
                           selected_months: Optional[List[int]] = None,
                           selected_activities: Optional[List[str]] = None) -> pd.Series:
        """Get attack counts by state."""
        df_filtered = self.filter_data(
            selected_states=selected_states,
            age_range=age_range,
            month_range=month_range,
            day_range=day_range,
            year_range=year_range,
            selected_days=selected_days,
            selected_genders=selected_genders,
            selected_months=selected_months,
            selected_activities=selected_activities
        )
        return df_filtered['State'].value_counts()

    def get_yearly_trend(self, selected_states: Optional[List[str]] = None,
                        age_range: Optional[List[float]] = None,
                        month_range: Optional[List[int]] = None,
                        day_range: Optional[List[int]] = None,
                        year_range: Optional[List[int]] = None,
                        selected_days: Optional[List[str]] = None,
                        selected_genders: Optional[List[str]] = None,
                        selected_months: Optional[List[int]] = None,
                        selected_activities: Optional[List[str]] = None) -> pd.Series:
        """Get yearly trend of attacks."""
        df_filtered = self.filter_data(
            selected_states=selected_states,
            age_range=age_range,
            month_range=month_range,
            day_range=day_range,
            year_range=year_range,
            selected_days=selected_days,
            selected_genders=selected_genders,
            selected_months=selected_months,
            selected_activities=selected_activities
        )
        return df_filtered['Year'].value_counts().sort_index()

    def get_activity_distribution(self, selected_states: Optional[List[str]] = None,
                                age_range: Optional[List[float]] = None,
                                month_range: Optional[List[int]] = None,
                                day_range: Optional[List[int]] = None,
                                year_range: Optional[List[int]] = None,
                                selected_days: Optional[List[str]] = None,
                                selected_genders: Optional[List[str]] = None,
                                selected_months: Optional[List[int]] = None,
                                selected_activities: Optional[List[str]] = None) -> pd.Series:
        """Get distribution of activities."""
        df_filtered = self.filter_data(
            selected_states=selected_states,
            age_range=age_range,
            month_range=month_range,
            day_range=day_range,
            year_range=year_range,
            selected_days=selected_days,
            selected_genders=selected_genders,
            selected_months=selected_months,
            selected_activities=selected_activities
        )
        return df_filtered['Activity'].value_counts().head(DATA_SETTINGS['top_n_activities'])

    def get_shark_species_distribution(self, selected_states: Optional[List[str]] = None,
                                     age_range: Optional[List[float]] = None,
                                     month_range: Optional[List[int]] = None,
                                     day_range: Optional[List[int]] = None,
                                     year_range: Optional[List[int]] = None,
                                     selected_days: Optional[List[str]] = None,
                                     selected_genders: Optional[List[str]] = None,
                                     selected_months: Optional[List[int]] = None,
                                     selected_activities: Optional[List[str]] = None) -> pd.Series:
        """Get distribution of shark species."""
        df_filtered = self.filter_data(
            selected_states=selected_states,
            age_range=age_range,
            month_range=month_range,
            day_range=day_range,
            year_range=year_range,
            selected_days=selected_days,
            selected_genders=selected_genders,
            selected_months=selected_months,
            selected_activities=selected_activities
        )
        return df_filtered['SharkName'].value_counts().head(DATA_SETTINGS['top_n_species'])