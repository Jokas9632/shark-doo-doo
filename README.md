# Australian Shark Attack Dashboard 🦈

An interactive dashboard for visualizing and analyzing historical shark attack data in Australia. This application provides dynamic visualizations of shark attack patterns, geographical distributions, and various analytical insights across different Australian states.

## Project Structure

```
project/
├── app.py                 # Main application file
├── data/
│   ├── cleaned_data.csv   # Processed shark attack data
│   └── states.geojson     # Australian states boundaries
├── config.py              # Configuration settings
├── data.py               # Data management and processing
├── visualizations.py     # Visualization components
└── requirements.txt      # Project dependencies
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
