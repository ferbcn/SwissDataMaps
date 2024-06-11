# SwissMaps.xyz

This project is a web application that uses different data sources to display geospatial data and information using Plotly Dash ontop of a FastApi Web Server (Starlett, gunicorn/uvicorn under the hood).

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes.

### Prerequisites

- Python
- pip

### Installing

```bash
pip install -r requirements.txt
```

### Run Uvicorn

```bash
uvicorn main:app --reload
```

### Running the App in Docker

```bash
docker compose up --build
```

### Live App
[https://swissmaps.xyz](https://swissmaps.xyz)

![App screenshot](assets/screen.png)

