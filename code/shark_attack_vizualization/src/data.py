import pandas as pd
import json
from shapely.geometry import shape
from typing import Dict, List, Optional
from config import (
    DATA_PATHS,
    DATA_SETTINGS,
    REVERSE_STATE_MAPPING,
    STATE_NAME_MAPPING
)


class DataManager:
    def __init__(self):
        """Initialize DataManager with empty data structures."""
        self.df = pd.read_csv(DATA_PATHS['csv_file'])
        self.df['Latitude'] = self.df['Latitude'].apply(self._clean_coordinate)
        self.df['Longitude'] = self.df['Longitude'].apply(self._clean_coordinate)
        self.df['Injury'] = self.df['Injury'].str.lower()
        self.geojson_data = self._load_geojson()
        self.state_centroids = self._calculate_state_centroids()
        self._add_day_of_week()
        self._add_time_period()
        self._create_hover_text()

    def _clean_coordinate(self, coord):
        """Clean coordinate values by removing special characters and converting to float."""
        if pd.isna(coord):
            return None
        try:
            # Convert to string first
            coord_str = str(coord)
            # Remove special characters and keep only numbers, decimal points, and minus signs
            cleaned = ''.join(c for c in coord_str if c.isdigit() or c in '.-')
            # Convert to float
            return float(cleaned)
        except (ValueError, TypeError):
            return None

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

    def _categorize_time_period(self, time_str):
        """Categorize time into periods of the day."""
        if not time_str or pd.isna(time_str):
            return None

        try:
            hours = int(time_str.split(':')[0])

            if 6 <= hours < 12:
                return 'morning'
            elif 12 <= hours < 18:
                return 'afternoon'
            elif 18 <= hours < 21:
                return 'evening'
            else:
                return 'night'
        except:
            return None

    def _add_time_period(self):
        """Add time period column based on IncidentTime."""
        self.df['TimePeriod'] = self.df['IncidentTime'].apply(self._categorize_time_period)

    def _create_hover_text(self):
        """Create hover text for map points."""
        self.df['hover_text'] = self.df.apply(
            lambda row: f"""
<b>Year:</b> {int(row['Year']) if pd.notnull(row['Year']) else 'Unknown'}<br>
<b>Shark Species:</b> {row['SharkName'] if pd.notnull(row['SharkName']) else 'Unknown'}<br>
<b>Activity:</b> {row['Activity'] if pd.notnull(row['Activity']) else 'Unknown'}<br>
<b>Injury:</b> {row['Injury'] if pd.notnull(row['Injury']) else 'Unknown'}<br>
<b>Gender:</b> {row['Gender'] if pd.notnull(row['Gender']) else 'Unknown'}<br>
<b>Age:</b> {int(row['Age']) if pd.notnull(row['Age']) else 'Unknown'}<br>
<b>Time:</b> {row['IncidentTime'] if pd.notnull(row['IncidentTime']) else 'Unknown'}<br>
<b>Time Period:</b> {row['TimePeriod'].title() if pd.notnull(row['TimePeriod']) else 'Unknown'}
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
                    selected_activities: Optional[List[str]] = None,
                    selected_time_periods: Optional[List[str]] = None,
                    selected_sharks: Optional[List[str]] = None,
                    selected_injuries: Optional[List[str]] = None) -> pd.DataFrame:
        """Filter data based on selected criteria."""
        df_filtered = self.df.copy()

        if selected_states:
            # Handle both state codes and full names
            selected_short_states = []
            for state in selected_states:
                if state in REVERSE_STATE_MAPPING:  # If it's a full name
                    selected_short_states.append(REVERSE_STATE_MAPPING[state])
                elif state in STATE_NAME_MAPPING:   # If it's already a state code
                    selected_short_states.append(state)
            
            df_filtered = df_filtered[df_filtered['State'].isin(selected_short_states)]

        # Rest of the filtering logic remains the same
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

        if selected_time_periods and len(selected_time_periods) > 0:
            df_filtered = df_filtered[df_filtered['TimePeriod'].isin(selected_time_periods)]

        if selected_sharks and len(selected_sharks) > 0:
            df_filtered = df_filtered[df_filtered['SharkName'].isin(selected_sharks)]

        if selected_injuries and len(selected_injuries) > 0:
            df_filtered = df_filtered[df_filtered['Injury'].str.lower().isin(selected_injuries)]

        return df_filtered
    def get_attacks_by_state(self, selected_injuries: Optional[List[str]] = None,
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
                             selected_sharks: Optional[List[str]] = None) -> pd.Series:
        """Get attack counts by state."""
        df_filtered = self.filter_data(
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
        return df_filtered['State'].value_counts()

    def get_activity_distribution(self, selected_injuries: Optional[List[str]] = None,
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
                                  selected_sharks: Optional[List[str]] = None) -> pd.Series:
        """Get distribution of activities."""
        df_filtered = self.filter_data(
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
        # Calculate percentages
        activity_counts = df_filtered['Activity'].value_counts()
        total_activities = activity_counts.sum()
        activity_percentages = (activity_counts / total_activities * 100).round(1)

        return activity_percentages.head(DATA_SETTINGS['top_n_activities'])

    def get_shark_species_distribution(self, selected_injuries: Optional[List[str]] = None,
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
                                       selected_sharks: Optional[List[str]] = None) -> pd.Series:
        """Get distribution of shark species."""
        df_filtered = self.filter_data(
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
        return df_filtered['SharkName'].value_counts().head(DATA_SETTINGS['top_n_species'])

    def get_day_distribution(self, selected_injuries: Optional[List[str]] = None,
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
                             selected_sharks: Optional[List[str]] = None) -> pd.Series:
        """Get distribution of attacks by day of week with percentages."""
        df_filtered = self.filter_data(
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

        # Get day counts and calculate percentages
        day_counts = df_filtered['DayOfWeek'].value_counts()
        total_attacks = day_counts.sum()
        day_percentages = (day_counts / total_attacks * 100).round(1)

        # Define correct day order
        days_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        return day_percentages.reindex(days_order).fillna(0)

    def get_monthly_distribution(self, selected_injuries: Optional[List[str]] = None,
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
                                 selected_sharks: Optional[List[str]] = None) -> pd.Series:
        """Get monthly distribution of attacks with percentages."""
        df_filtered = self.filter_data(
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

        # Create a month name mapping
        month_names = {
            1: 'January', 2: 'February', 3: 'March', 4: 'April',
            5: 'May', 6: 'June', 7: 'July', 8: 'August',
            9: 'September', 10: 'October', 11: 'November', 12: 'December'
        }

        monthly_counts = df_filtered['Month'].value_counts()
        total_attacks = monthly_counts.sum()

        # Convert to percentages and sort by month number
        monthly_percentages = (monthly_counts / total_attacks * 100).sort_index()

        # Convert month numbers to names
        monthly_percentages.index = monthly_percentages.index.map(month_names)

        return monthly_percentages

    def get_age_distribution(self, selected_injuries: Optional[List[str]] = None,
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
                             selected_sharks: Optional[List[str]] = None) -> pd.Series:
        """Get distribution of attacks by age groups."""
        df_filtered = self.filter_data(
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

        def categorize_age(age):
            if pd.isna(age):
                return 'Unknown'
            elif age <= 12:
                return '0-12'
            elif age <= 17:
                return '13-17'
            elif age <= 24:
                return '18-24'
            elif age <= 34:
                return '25-34'
            elif age <= 44:
                return '35-44'
            elif age <= 54:
                return '45-54'
            else:
                return '55+'

        df_filtered['AgeGroup'] = df_filtered['Age'].apply(categorize_age)
        age_counts = df_filtered['AgeGroup'].value_counts()
        total_attacks = age_counts.sum()
        age_percentages = (age_counts / total_attacks * 100).round(1)

        # Sort by age group order
        age_group_order = ['0-12', '13-17', '18-24', '25-34', '35-44', '45-54', '55+', 'Unknown']
        return age_percentages.reindex(age_group_order).fillna(0)

    def get_gender_age_provocation_distribution(self, selected_injuries: Optional[List[str]] = None,
                                                selected_states=None, age_range=None,
                                                month_range=None, day_range=None, year_range=None,
                                                selected_days=None, selected_genders=None,
                                                selected_months=None, selected_activities=None,
                                                selected_time_periods=None, selected_sharks=None):
        """Get distribution of attacks by age groups, gender, and provocation."""
        df_filtered = self.filter_data(
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

        def categorize_age(age):
            if pd.isna(age):
                return 'Unknown'
            elif age <= 12:
                return '0-12'
            elif age <= 17:
                return '13-17'
            elif age <= 24:
                return '18-24'
            elif age <= 34:
                return '25-34'
            elif age <= 44:
                return '35-44'
            elif age <= 54:
                return '45-54'
            else:
                return '55+'

        df_filtered['AgeGroup'] = df_filtered['Age'].apply(categorize_age)

        # Create MultiIndex DataFrame for all combinations
        male_provoked = df_filtered[(df_filtered['Gender'] == 'male') &
                                    (df_filtered['Provocation'] == 'provoked')]['AgeGroup'].value_counts()
        male_unprovoked = df_filtered[(df_filtered['Gender'] == 'male') &
                                      (df_filtered['Provocation'] == 'unprovoked')]['AgeGroup'].value_counts()
        female_provoked = df_filtered[(df_filtered['Gender'] == 'female') &
                                      (df_filtered['Provocation'] == 'provoked')]['AgeGroup'].value_counts()
        female_unprovoked = df_filtered[(df_filtered['Gender'] == 'female') &
                                        (df_filtered['Provocation'] == 'unprovoked')]['AgeGroup'].value_counts()

        # Create DataFrame with all categories
        age_groups = ['0-12', '13-17', '18-24', '25-34', '35-44', '45-54', '55+', 'Unknown']
        df_counts = pd.DataFrame({
            'Male_Provoked': male_provoked.reindex(age_groups).fillna(0),
            'Male_Unprovoked': male_unprovoked.reindex(age_groups).fillna(0),
            'Female_Provoked': female_provoked.reindex(age_groups).fillna(0),
            'Female_Unprovoked': female_unprovoked.reindex(age_groups).fillna(0)
        }, index=age_groups)

        return df_counts
