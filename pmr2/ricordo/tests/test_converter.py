import unittest

from pmr2.ricordo import converter


class ConverterTestCase(unittest.TestCase):
    """
    Test the converter
    """

    def test_purlobo_to_identifers(self):
        purl_go = 'http://purl.org/obo/owlapi/gene_ontology#GO_0005886'
        purl_fma = 'http://purl.org/obo/owlapi/fma#FMA_63841'

        idobo_go = 'http://identifiers.org/obo.go/GO:0005886'
        idobo_fma = 'http://identifiers.org/obo.fma/FMA:63841'

        id_go = 'http://identifiers.org/go/GO:0005886'
        id_fma = 'http://identifiers.org/fma/FMA:63841'

        self.assertEqual(converter.purlobo_to_identifiers(purl_go), [
            idobo_go, id_go])

        self.assertEqual(converter.purlobo_to_identifiers(purl_fma), [
            idobo_fma, id_fma])
