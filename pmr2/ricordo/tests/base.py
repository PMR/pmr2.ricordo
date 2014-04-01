import requests

from Zope2.App import zcml
from Products.Five import fiveconfigure
from Products.PloneTestCase.layer import onsetup, onteardown
from Products.PloneTestCase import PloneTestCase as ptc


@onsetup
def setup():
    import pmr2.ricordo
    fiveconfigure.debug_mode = True
    zcml.load_config('configure.zcml', pmr2.ricordo)
    fiveconfigure.debug_mode = False

@onteardown
def teardown():
    pass

setup()
teardown()

def test_available(text, url):
    try:
        return text in requests.get(url).text
    except:
        return False

def owlkb_test_available():
    return test_available('RICORDO-owlkb-webservice',
        'http://127.0.0.1:8080/ricordo-owlkb-ws/')

def rdfstore_test_available():
    return virtuoso_test_available()

def virtuoso_test_available():
    try:
        r = requests.get('http://127.0.0.1:8890/sparql/')
        return 'Virtuoso SPARQL' in r.text
    except:
        return False
