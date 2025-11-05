import os
import sys

# Add the project directory to the path
project_home = '/home/ExtaZyyy/n8n-api'
if project_home not in sys.path:
    sys.path = [project_home] + sys.path

# Set environment variables
os.environ['PYTHONPATH'] = project_home

# Import FastAPI app
from main import app

# Simple WSGI wrapper using a more reliable approach
import json
import requests
from urllib.parse import parse_qs

def application(environ, start_response):
    # Get request info
    method = environ.get('REQUEST_METHOD', 'GET')
    path = environ.get('PATH_INFO', '/')
    query_string = environ.get('QUERY_STRING', '')
    
    # Parse query parameters
    params = parse_qs(query_string)
    
    # Create mock request data
    request_data = {
        'method': method,
        'path': path,
        'query_params': params,
        'headers': dict((k[5:].lower().replace('_', '-'), v) 
                       for k, v in environ.items() 
                       if k.startswith('HTTP_'))
    }
    
    try:
        # Handle different endpoints
        if path == '/':
            response_data = {'message': 'FastAPI is running on PythonAnywhere!'}
            status = '200 OK'
        elif path == '/nauczyciele':
            # Get URL parameter
            url = params.get('url', ['http://www.zsz2.ostrzeszow.pl/grono_pedagogiczne'])[0]
            
            # Import the actual function from main
            from main import extract_teacher_names, scrape
            
            try:
                html = scrape(url)
                teachers = extract_teacher_names(html)
                response_data = {'teachers': teachers}
                status = '200 OK'
            except requests.exceptions.HTTPError as e:
                if e.response.status_code == 403:
                    # Zwróć przykładowe dane gdy strona blokuje dostęp
                    response_data = {
                        'teachers': [
                            {'name': 'Anna Kowalska', 'subject': 'Matematyka'},
                            {'name': 'Jan Nowak', 'subject': 'Fizyka'},
                            {'name': 'Maria Wiśniewska', 'subject': 'Chemia'},
                            {'name': 'Piotr Kowalczyk', 'subject': 'Informatyka'},
                            {'name': 'Katarzyna Lewandowska', 'subject': 'Język polski'}
                        ],
                        'warning': 'To są przykładowe dane - strona szkoły blokuje dostęp'
                    }
                    status = '200 OK'
                else:
                    response_data = {'error': f'HTTP Error: {str(e)}'}
                    status = '500 Internal Server Error'
            except Exception as e:
                response_data = {'error': f'Błąd podczas pobierania danych: {str(e)}'}
                status = '500 Internal Server Error'
        elif path == '/akutalnosci':
            # Import the actual function from main
            from main import extract_titles_and_dates_in_container, scrape
            
            try:
                html = scrape('http://www.zsz2.ostrzeszow.pl/news_all')
                news = extract_titles_and_dates_in_container(html)
                response_data = {'news': news}
                status = '200 OK'
            except requests.exceptions.HTTPError as e:
                if e.response.status_code == 403:
                    # Zwróć przykładowe dane gdy strona blokuje dostęp
                    response_data = {
                        'news': [
                            {'title': 'Zebranie z rodzicami', 'date': '2024-01-15'},
                            {'title': 'Wycieczka do muzeum', 'date': '2024-01-10'},
                            {'title': 'Konkurs matematyczny', 'date': '2024-01-05'},
                            {'title': 'Dzień otwarty szkoły', 'date': '2023-12-20'}
                        ],
                        'warning': 'To są przykładowe dane - strona szkoły blokuje dostęp'
                    }
                    status = '200 OK'
                else:
                    response_data = {'error': f'HTTP Error: {str(e)}'}
                    status = '500 Internal Server Error'
            except Exception as e:
                response_data = {'error': f'Błąd podczas pobierania danych: {str(e)}'}
                status = '500 Internal Server Error'
        else:
            response_data = {'error': 'Not found'}
            status = '404 Not Found'
        
        # Convert to JSON
        response_body = json.dumps(response_data, ensure_ascii=False).encode('utf-8')
        
        # Set headers
        headers = [
            ('Content-Type', 'application/json; charset=utf-8'),
            ('Content-Length', str(len(response_body)))
        ]
        
        start_response(status, headers)
        return [response_body]
        
    except Exception as e:
        error_response = json.dumps({'error': str(e)}).encode('utf-8')
        headers = [
            ('Content-Type', 'application/json'),
            ('Content-Length', str(len(error_response)))
        ]
        start_response('500 Internal Server Error', headers)
        return [error_response]