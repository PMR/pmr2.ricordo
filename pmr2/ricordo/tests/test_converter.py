import unittest

from pmr2.ricordo import converter


purl_go = 'http://purl.org/obo/owlapi/gene_ontology#GO_0005886'
purl_fma = 'http://purl.org/obo/owlapi/fma#FMA_63841'
purl_pr = 'http://purl.org/obo/owlapi/pro#PRO_000002023'
purl_cl = 'http://purl.org/obo/owlapi/pro#CL_0000017'
purl_chebi = 'http://purl.org/obo/owlapi/chebi_ontology#CHEBI_100461'
bhi_opb = 'http://bhi.washington.edu/OPB#OPB_01226'

idobo_go = 'http://identifiers.org/obo.go/GO:0005886'
idobo_fma = 'http://identifiers.org/obo.fma/FMA:63841'
idobo_pr = 'http://identifiers.org/obo.pr/PR:000002023'
# idobo_cl = 'http://identifiers.org/obo.cl/CL:0000017'
idobo_chebi = 'http://identifiers.org/obo.chebi/CHEBI:100461'

id_go = 'http://identifiers.org/go/GO:0005886'
id_fma = 'http://identifiers.org/fma/FMA:63841'
id_pr = 'http://identifiers.org/pr/PR:000002023'
id_cl = 'http://identifiers.org/cl/CL:0000017'
id_chebi = 'http://identifiers.org/chebi/CHEBI:100461'
id_opb = 'http://identifiers.org/opb/OPB_01226'


class ConverterTestCase(unittest.TestCase):
    """
    Test the converter
    """

    def test_nonstandard_to_identifers(self):

        self.assertEqual(converter.purlobo_to_identifiers(purl_go), [
            id_go, idobo_go,])

        self.assertEqual(converter.purlobo_to_identifiers(purl_fma), [
            id_fma, idobo_fma,])

        self.assertEqual(converter.purlobo_to_identifiers(purl_pr), [
            id_pr, idobo_pr,])

        self.assertEqual(converter.purlobo_to_identifiers(purl_cl), [
            id_cl,])

        self.assertEqual(converter.purlobo_to_identifiers(purl_chebi), [
            id_chebi, idobo_chebi,])

        self.assertEqual(converter.purlobo_to_identifiers(bhi_opb), [
            id_opb,])

    def test_identifers_to_nonstandard(self):

        self.assertEqual(converter.identifiers_to_purlobo(id_go), [purl_go])
        self.assertEqual(converter.identifiers_to_purlobo(idobo_go), [purl_go])

        self.assertEqual(converter.identifiers_to_purlobo(id_fma), [purl_fma])
        self.assertEqual(converter.identifiers_to_purlobo(idobo_fma),
            [purl_fma])

        self.assertEqual(converter.identifiers_to_purlobo(id_pr), [purl_pr])
        self.assertEqual(converter.identifiers_to_purlobo(idobo_pr), [purl_pr])

        self.assertEqual(converter.identifiers_to_purlobo(id_cl), [purl_cl])

        self.assertEqual(converter.identifiers_to_purlobo(id_chebi),
            [purl_chebi])
        self.assertEqual(converter.identifiers_to_purlobo(idobo_chebi),
            [purl_chebi])

        self.assertEqual(converter.identifiers_to_purlobo(id_opb), [bhi_opb])
