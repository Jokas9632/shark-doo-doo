import csv
import pandas as pd


def read_activity_data():
    with open(r"C:\Users\User\PycharmProjects\AustralianSharkIncidentDatabase\data\activityDat.csv") as file:
        data = list(csv.reader(file))
        df = pd.DataFrame(data[1:], columns=data[0])
        df.columns = ['Year', 'Status', 'Provoked', 'Activity']
        print(df.head())
        return df


def read_injury_data():
    with open(r'C:\Users\User\PycharmProjects\shark-doo-doo\data\injurydat.csv') as file:
        data = list(csv.reader(file))
        df = pd.DataFrame(data[1:], columns=data[0])
        return df


def convert_to_csv():
    txt_file = r'C:\Users\User\PycharmProjects\shark-doo-doo\data\injurydat.txt'
    csv_file = r'C:\Users\User\PycharmProjects\shark-doo-doo\data\injurydat.csv'

    with open(txt_file, "r") as txt_file, open(csv_file, "w", newline="") as csv_file:
        csv_writer = csv.writer(csv_file)
        lines = txt_file.readlines()
        header = lines[0].strip().split("\t")
        csv_writer.writerow(header)

        for line in lines[1:]:
            row = [value.strip() if value.strip() else "" for value in line.split("\t")]
            csv_writer.writerow(row)


read_activity_data()
# read_injury_data()
convert_to_csv()
