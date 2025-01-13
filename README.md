# Australian Shark Attack Dashboard 🦈

An interactive dashboard for visualizing and analyzing historical shark attack data in Australia. This application provides dynamic visualizations of shark attack patterns, geographical distributions, and various analytical insights across different Australian states.

## Project Structure

```
SHARK-DOO-DOO/
├── assignment_documents/     # Project documentation
├── code/
│   ├── data/               # Raw data files
│   │   ├── activityDat.csv
│   │   ├── injurydat.csv
│   │   └── timedb2.csv
│   └── shark_attack_vizualization/
│       ├── data/          # Processed data
│       │   ├── cleaned_data.csv
│       │   └── states.geojson
│       └── src/           # Source code
│           ├── app.py     # Main application
│           ├── config.py  # Configuration
│           ├── data.py    # Data processing
│           └── visualizations.py
├── data_cleaning.ipynb    # Data preprocessing notebooks
├── data_cleaning_v2.ipynb
├── EDA.ipynb             # Exploratory Data Analysis
├── LICENSE
└── README.md
```

## Setup and Installation

1. Clone the repository
```bash
git clone https://github.com/yourusername/australian-shark-attacks.git
cd australian-shark-attacks
```

2. Create and activate a virtual environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install required packages
```bash
pip install -r requirements.txt
```

4. Run the application
```bash
python app.py
```

5. Open your browser and navigate to `http://localhost:8050`

## Data Sources

The dashboard uses a comprehensive dataset of shark attacks in Australian waters, including historical attack records, geographic coordinates, shark species information, activity types, injury details, and demographic information.
