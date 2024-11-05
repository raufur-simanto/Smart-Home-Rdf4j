# app.py
from flask import Flask, render_template, request, jsonify
from SPARQLWrapper import SPARQLWrapper, JSON, XML
import json
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__)

COMMON_PREFIXES = """
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
"""

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/query', methods=['POST'])
def query():
    try:
        server_url = request.form['server_url']
        repository_id = request.form['repository_id']
        query_text = request.form['query']

        endpoint_url = f"{server_url}/repositories/{repository_id}"
        
        # Initialize SPARQL wrapper
        sparql = SPARQLWrapper(endpoint_url)
        
        # Add common prefixes 
        if not 'PREFIX rdf:' in query_text:
            query_text = COMMON_PREFIXES + query_text

        sparql.setQuery(query_text)

        # Determine query type and set format
        query_type = determine_query_type(query_text.strip().upper())
        if query_type == 'SELECT' or query_type == 'ASK':
            sparql.setReturnFormat(JSON)
        else:
            # For CONSTRUCT queries, we'll use JSON-LD format
            sparql.setReturnFormat(JSON)

        results = sparql.query().convert()

        # Debug logging
        logger.debug(f"Query type: {query_type}")
        # logger.debug(f"Results type: {type(results)}")
        # logger.debug(f"Results: {results}")

        if query_type == 'SELECT':
            processed_results = process_select_results(results)
            return jsonify({
                'success': True,
                'type': 'SELECT',
                'results': processed_results
            })
        elif query_type == 'ASK':
            return jsonify({
                'success': True,
                'type': 'ASK',
                'results': results.get('boolean', False)
            })
        elif query_type == 'CONSTRUCT':
            # Process CONSTRUCT results
            if isinstance(results, bytes):
                triples_str = results.decode('utf-8')
                triple_lines = triples_str.strip().split('\n')
                triples = []
                
                
                for line in triple_lines:
                    # Skip empty lines
                    if not line.strip():
                        continue
                    
                    # Remove the trailing dot and split by spaces
                    parts = line.strip(' .').split(' ', 2)
                    if len(parts) == 3:
                        subject = parts[0].strip('<>')
                        predicate = parts[1].strip('<>')
                        object_value = parts[2]
                        # logger.info(f"Triple: {subject} {predicate} {object_value}")
                        
                        # Remove quotes from literal values
                        if object_value.startswith('"') and object_value.endswith('"'):
                            object_value = object_value[1:-1]
                        else:
                            object_value = object_value.strip('<>')
                            
                        triples.append({
                            'subject': format_uri(subject),
                            'predicate': format_uri(predicate),
                            'object': object_value
                        })
                
                return jsonify({
                    'success': True,
                    'type': 'CONSTRUCT',
                    'results': triples
                })
            
            return jsonify({
                'success': False,
                'error': 'Unexpected result format'
            })
        else:
            # DESCRIBE results
            return jsonify({
                'success': True,
                'type': query_type,
                'results': str(results)
            })

    except Exception as e:
        print(f"Error in query route: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        })

def determine_query_type(query):
    # Skip prefix declarations to find the actual query type
    lines = query.split('\n')
    for line in lines:
        line = line.strip().upper()
        if line.startswith('SELECT'):
            return 'SELECT'
        elif line.startswith('ASK'):
            return 'ASK'
        elif line.startswith('CONSTRUCT'):
            return 'CONSTRUCT'
        elif line.startswith('DESCRIBE'):
            return 'DESCRIBE'
    raise ValueError('Unknown query type')

def process_select_results(results):
    if not results.get('results', {}).get('bindings'):
        return {'headers': [], 'rows': []}
    
    bindings = results['results']['bindings']
    if not bindings:
        return {'headers': [], 'rows': []}
    
    headers = list(bindings[0].keys())
    
    rows = []
    for binding in bindings:
        row = []
        for header in headers:
            value = binding.get(header, {}).get('value', '')
            row.append(value)
        rows.append(row)
    
    return {'headers': headers, 'rows': rows}

def format_uri(uri):
    """Format URI to show only the relevant part"""
    if '#' in uri:
        return uri.split('#')[-1]
    return uri.split('/')[-1]

if __name__ == '__main__':
    app.run(port=5000)
