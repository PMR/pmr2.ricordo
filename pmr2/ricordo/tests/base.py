import requests

def test_available(text, url):
    try:
        return text in requests.get(url).text
    except:
        return False

def owlkb_test_available():
    return test_available('RICORDO-owlkb-webservice',
        'http://127.0.0.1:8080/ricordo-owlkb-ws/')

def rdfstore_test_available():
    return test_available('RICORDO-rdfstore-webservice',
        'http://127.0.0.1:8080/ricordo-rdfstore-ws/')

def virtuoso_test_available():
    try:
        r = requests.get('http://127.0.0.1:8890/sparql/')
        return 'Virtuoso SPARQL' in r.text
    except:
        return False
