import re


class Converter(object):

    def __init__(self, rules):
        self.compiled_rules = [(re.compile(k), v) for k, v in rules]

    def __call__(self, identifier):
        return [rule.sub(replacement, identifier) for rule, replacement in
            self.compiled_rules if rule.search(identifier)]

# purl.org/obo/* to identifiers.org/obo/*
purlobo_to_identifiers = Converter((
    ('^http://purl.org/obo/owlapi/gene_ontology#GO_([0-9]{7})$',
        'http://identifiers.org/go/GO:\\1'),
    ('^http://purl.org/obo/owlapi/gene_ontology#GO_([0-9]{7})$',
        'http://identifiers.org/obo.go/GO:\\1'),

    ('^http://purl.org/obo/owlapi/fma#FMA_([0-9]*)$',
        'http://identifiers.org/fma/FMA:\\1'),
    ('^http://purl.org/obo/owlapi/fma#FMA_([0-9]*)$',
        'http://identifiers.org/obo.fma/FMA:\\1'),

    ('^http://purl.org/obo/owlapi/pro#PRO_([0-9]*)$',
        'http://identifiers.org/pr/PR:\\1'),
    ('^http://purl.org/obo/owlapi/pro#PRO_([0-9]*)$',
        'http://identifiers.org/obo.pr/PR:\\1'),

    ('^http://purl.org/obo/owlapi/pro#CL_([0-9]*)$',
        'http://identifiers.org/cl/CL:\\1'),

    ('^http://purl.org/obo/owlapi/chebi_ontology#CHEBI_([0-9]*)$',
        'http://identifiers.org/chebi/CHEBI:\\1'),
    ('^http://purl.org/obo/owlapi/chebi_ontology#CHEBI_([0-9]*)$',
        'http://identifiers.org/obo.chebi/CHEBI:\\1'),

    ('^http://bhi.washington.edu/OPB#OPB_([0-9]*)$',
        'http://identifiers.org/opb/OPB_\\1'),

))

# inverse of the above.
identifiers_to_purlobo = Converter((
    ('^http://identifiers.org/obo.go/GO:([0-9]{7})$',
        'http://purl.org/obo/owlapi/gene_ontology#GO_\\1'),
    ('^http://identifiers.org/go/GO:([0-9]{7})$',
        'http://purl.org/obo/owlapi/gene_ontology#GO_\\1'),

    ('^http://identifiers.org/obo.fma/FMA:([0-9]*)$',
        'http://purl.org/obo/owlapi/fma#FMA_\\1'),
    ('^http://identifiers.org/fma/FMA:([0-9]*)$',
        'http://purl.org/obo/owlapi/fma#FMA_\\1'),

    ('^http://identifiers.org/obo.pr/PR:([0-9]*)$',
        'http://purl.org/obo/owlapi/pro#PRO_\\1'),
    ('^http://identifiers.org/pr/PR:([0-9]*)$',
        'http://purl.org/obo/owlapi/pro#PRO_\\1'),

    ('^http://identifiers.org/cl/CL:([0-9]*)$',
        'http://purl.org/obo/owlapi/pro#CL_\\1'),

    ('^http://identifiers.org/obo.cheibi/CHEBI:([0-9]*)$',
        'http://purl.org/obo/owlapi/chebi_ontology#CHEBI_\\1'),
    ('^http://identifiers.org/chebi/CHEBI:([0-9]*)$',
        'http://purl.org/obo/owlapi/chebi_ontology#CHEBI_\\1'),

    ('^http://identifiers.org/opb/OPB_([1-9]*)$',
        'http://bhi.washington.edu/OPB#OPB_\\1'),

))

# purl.org/obo to RICORDO-OWLKB contracted form.

purlobo_to_owlkb = Converter((
    ('http://purl.org/obo/owlapi/gene_ontology#GO_([0-9]{7})', 'GO_\\1'),
    ('http://purl.org/obo/owlapi/fma#FMA_([0-9]*)', 'FMA_\\1'),
    ('http://purl.org/obo/owlapi/pro#PRO_([0-9]*)', 'PRO_\\1'),
    ('http://purl.org/obo/owlapi/pro#CL_([0-9]*)', 'CL_\\1'),
    ('http://purl.org/obo/owlapi/chebi_ontology#CHEBI_([0-9]*)', 'CHEBI_\\1'),
))

# inverse of the above

purlobo_to_owlkb = Converter((
    ('^GO_([0-9]{7})$', 'http://purl.org/obo/owlapi/gene_ontology#GO_\\1'),
    ('^FMA_([0-9]*)$', 'http://purl.org/obo/owlapi/fma#FMA_\\1'),
    ('^PRO_([0-9]*)$', 'http://purl.org/obo/owlapi/pro#PRO_\\1'),
    ('^CL_([0-9]*)$', 'http://purl.org/obo/owlapi/pro#CL_\\1'),
    ('^CHEBI_([0-9]*)$', 'http://purl.org/obo/owlapi/chebi_ontology#CHEBI_\\1'),
))
