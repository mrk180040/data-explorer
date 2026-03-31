from flask import Flask, request, jsonify, send_from_directory
from databricks import sql
import os
import re

app = Flask(__name__, static_folder='static', static_url_path='')

MAX_QUERY_LIMIT = 1000
SAFE_IDENTIFIER_RE = re.compile(r'^[A-Za-z0-9_-]+$')
ALLOWED_QUERY_PREFIXES = ('select', 'with', 'show', 'describe', 'explain')
DISALLOWED_QUERY_PATTERNS = (
    r'\b(insert|update|delete|merge|drop|alter|truncate|create|grant|revoke|use|call|copy\s+into)\b',
    r'--',
    r'/\*',
    r';'
)

# CORS support
@app.after_request
def after_request(response):
    allowed_origin = os.getenv('ALLOWED_ORIGIN')
    if allowed_origin:
        response.headers.add('Access-Control-Allow-Origin', allowed_origin)
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
    response.headers.add('Access-Control-Allow-Methods', 'GET,POST,OPTIONS')
    return response


@app.before_request
def handle_preflight():
    if request.method == 'OPTIONS' and request.path.startswith('/api/'):
        return ('', 204)

# Get Databricks connection
def get_connection():
    return sql.connect(
        server_hostname=os.getenv('DATABRICKS_SERVER_HOSTNAME'),
        http_path=os.getenv('DATABRICKS_HTTP_PATH'),
        access_token=os.getenv('DATABRICKS_TOKEN')
    )


def quote_identifier(identifier):
    if not identifier or not SAFE_IDENTIFIER_RE.match(identifier):
        raise ValueError(f'Invalid identifier: {identifier}')
    return f'`{identifier}`'


def parse_table_name(full_table_name):
    if not full_table_name:
        raise ValueError('Table name is required')

    parts = [part.strip() for part in full_table_name.split('.')]
    if len(parts) != 3 or not all(parts):
        raise ValueError('Table name must be in format catalog.schema.table')

    return '.'.join(quote_identifier(part) for part in parts)


def parse_limit(raw_limit):
    try:
        parsed_limit = int(raw_limit)
    except (TypeError, ValueError):
        raise ValueError('Limit must be an integer')

    if parsed_limit < 1 or parsed_limit > MAX_QUERY_LIMIT:
        raise ValueError(f'Limit must be between 1 and {MAX_QUERY_LIMIT}')

    return parsed_limit


def is_safe_readonly_query(query_text):
    normalized_query = query_text.strip().lower()
    if not normalized_query:
        return False

    if not normalized_query.startswith(ALLOWED_QUERY_PREFIXES):
        return False

    for pattern in DISALLOWED_QUERY_PATTERNS:
        if re.search(pattern, normalized_query):
            return False

    return True

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
        catalog_identifier = quote_identifier(catalog)
        with get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(f'SHOW SCHEMAS IN {catalog_identifier}')
                schemas = [row[0] for row in cursor.fetchall()]
                return jsonify({'schemas': schemas})
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/tables/<catalog>/<schema>')
def get_tables(catalog, schema):
    try:
        catalog_identifier = quote_identifier(catalog)
        schema_identifier = quote_identifier(schema)
        with get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(f'SHOW TABLES IN {catalog_identifier}.{schema_identifier}')
                tables = [row[1] for row in cursor.fetchall()]  # row[1] is tableName
                return jsonify({'tables': tables})
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/query', methods=['POST'])
def query_data():
    try:
        data = request.get_json(silent=True) or {}
        table_name = data.get('table')
        limit = parse_limit(data.get('limit', 100))
        safe_table_name = parse_table_name(table_name)

        query = f'SELECT * FROM {safe_table_name} LIMIT {limit}'
        
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
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/custom-query', methods=['POST'])
def custom_query():
    try:
        data = request.get_json(silent=True) or {}
        query = (data.get('query') or '').strip()
        
        if not query:
            return jsonify({'error': 'Query is required'}), 400

        if not is_safe_readonly_query(query):
            return jsonify({'error': 'Only single-statement read-only queries are allowed'}), 400
        
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