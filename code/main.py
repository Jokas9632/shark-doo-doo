import csv
import pandas as pd


def read_activity_data():
    with open("cleaned_data.csv") as file:
        data = list(csv.reader(file))
        df_cleaned = pd.DataFrame(data[1:], columns=data[0])
        df_cleaned.columns = ['Year', 'Status', 'Provocation', 'Activity', 'Day', 'Month', 'Injury', 'State',
                              'Location', 'Latitude', 'Longitude', 'SharkName', 'SharkLength', 'SharksCount',
                              'InjuryLocation', 'Severity', 'Gender', 'Age', 'IncidentTime', 'Latitude_timedb2',
                              'SharkScientific', 'TimeOfDay']
        return df_cleaned


df = read_activity_data()
print(df['Activity'].value_counts())
