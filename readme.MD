# SPARQL Query Interface

A simple web interface for executing SPARQL queries against an RDF repository.

## Features

- Connect to any SPARQL endpoint
- Execute SPARQL queries
- View query results
- User-friendly interface

## Prerequisites

- Python 3.8 or higher
- pip (Python package installer)

## Installation and Setup

### 1. Clone the Repository
```
git clone git@github.com:raufur-simanto/Smart-Home-Rdf4j.git
cd Smart-Home-Rdf4j
```
### 2. Create a virtual environment
```
python3 -m venv venv
```
### 3. Activate the virtual environment
```
source venv/bin/activate # On Windows use `venv\Scripts\activate`
```

### 4. Install the dependencies
```
pip install -r requirements.txt
```
### 5. Run the application
```
python app.py
```
### 6. Access the Application
Open your web browser and navigate to: `http://localhost:5000`


## Usage

1. Enter your SPARQL endpoint URL (default: http://localhost:8080/rdf4j-server)
2. Specify the repository ID
3. Enter your SPARQL query
4. Click "Execute Query" to see the results

