import csv
import pandas as pd


def read_activity_data():
    with open(r"data\activityDat.csv") as file:
        data = list(csv.reader(file))
        df = pd.DataFrame(data[1:], columns=data[0])
        df.columns = ['Year', 'Status', 'Provocation', 'Activity']
        print(df.head())
        return df


def read_injury_data():
    with open(r"data\injurydat.csv") as file:
        data = list(csv.reader(file))
        df = pd.DataFrame(data[1:], columns=data[0])
        df.columns = ['Day', 'Month', 'Year', 'Injury', 'State', 'Location', 'Latitude', 'Longitude', 'SharkName',
                      'SharkLength', 'Provocation', 'SharksCount', 'Activity', 'InjuryLocation', 'Severity', 'Gender',
                      'Age', 'IncidentTime']
        print(df.head())
        return df


def read_timedb2_data():
    with open(r"data\timedb2.csv") as file:
        data = list(csv.reader(file))
        df = pd.DataFrame(data[1:], columns=data[0])
        df.columns = ['Day', 'Month', 'Year', 'Latitude', 'Longitude', 'SharkName', 'SharkScientific',
                      'Provocation', 'Activity', 'InjuryLocation', 'InjuryDescription', 'Severity',
                      'Gender', 'Age', 'IncidentTime']
        print(df.head())
        return df


df_act = read_activity_data()
df_inj = read_injury_data()
df_loc = read_locdat2_data()
df_time = read_timedb2_data()
