import os.path

from zope.browserpage import viewpagetemplatefile as vptf

path = lambda p: os.path.join(os.path.dirname(__file__), 'templates', p)

ViewPageTemplateFile = lambda f: vptf.ViewPageTemplateFile(path(f))
