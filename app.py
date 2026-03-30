from flask import Flask, request, jsonify, send_from_directory
from databricks import sql
import os

app = Flask(__name__, static_folder='static', static_url_path='')

# CORS support
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
    response.headers.add('Access-Control-Allow-Methods', 'GET,POST,OPTIONS')
    return response

# Get Databricks connection
def get_connection():
    return sql.connect(
        server_hostname=os.getenv('DATABRICKS_SERVER_HOSTNAME'),
        http_path=os.getenv('DATABRICKS_HTTP_PATH'),
        access_token=os.getenv('DATABRICKS_TOKEN')
    )

@app.route('/')
def index():
    return send_from_directory('static', 'index.html')

@app.route('/api/health')
def health():
    return jsonify({'status': 'healthy', 'message': 'Data Explorer API is running'})

@app.route('/api/catalogs')
def get_catalogs():
    try:
        with get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute('SHOW CATALOGS')
                catalogs = [row[0] for row in cursor.fetchall()]
                return jsonify({'catalogs': catalogs})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/schemas/<catalog>')
def get_schemas(catalog):
    try:
        with get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(f'SHOW SCHEMAS IN {catalog}')
                schemas = [row[0] for row in cursor.fetchall()]
                return jsonify({'schemas': schemas})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/tables/<catalog>/<schema>')
def get_tables(catalog, schema):
    try:
        with get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(f'SHOW TABLES IN {catalog}.{schema}')
                tables = [row[1] for row in cursor.fetchall()]  # row[1] is tableName
                return jsonify({'tables': tables})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/query', methods=['POST'])
def query_data():
    try:
        data = request.json
        table_name = data.get('table')
        limit = data.get('limit', 100)
        
        if not table_name:
            return jsonify({'error': 'Table name is required'}), 400
        
        query = f'SELECT * FROM {table_name} LIMIT {limit}'
        
        with get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(query)
                columns = [desc[0] for desc in cursor.description]
                rows = cursor.fetchall()
                
                result = {
                    'columns': columns,
                    'rows': [list(row) for row in rows],
                    'count': len(rows)
                }
                return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/custom-query', methods=['POST'])
def custom_query():
    try:
        data = request.json
        query = data.get('query')
        
        if not query:
            return jsonify({'error': 'Query is required'}), 400
        
        with get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(query)
                columns = [desc[0] for desc in cursor.description]
                rows = cursor.fetchall()
                
                result = {
                    'columns': columns,
                    'rows': [list(row) for row in rows],
                    'count': len(rows)
                }
                return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=False)