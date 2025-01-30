# CyBuses 🚌

This A real-time bus tracking system for Cyprus public transportation, built with Django and Leaflet. 

Real time bus tracking is currently not available on Google Maps for Cyprus.

## 🚧 Work in Progress

This project is currently under active development. Features and documentation will be updated regularly.

## 🌟 Features

- Real-time bus tracking on an interactive map
- Display of bus stops and routes
- Multi-language support (English and Greek)
- GTFS-RT integration for live vehicle positions

## 🛠 Tech Stack

- Django + GeoDjango for the backend
- Leaflet.js for interactive maps
- PostgreSQL + PostGIS for spatial data storage
- GTFS-RT for real-time transit data

## 🚀 Quick Start

1. Clone the repository:
```bash
git clone https://github.com/yourusername/CyBuses.git
cd CyBuses
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up the database:
```bash
python manage.py migrate
```

4. Run the development server:
```bash
python manage.py runserver
```

5. Visit `http://localhost:8000` in your browser

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🤝 Contributing

This is a work in progress and contributions are welcome! Feel free to open issues and submit pull requests.
