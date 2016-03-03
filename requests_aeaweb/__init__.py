#-*- coding: utf-8 -*-

"""
Requests-Raven is a custom Requests class to log onto Raven, the University of Cambridge's central
web authentication service. Basic usage for returning a Requests session object:
    
    >>> from requests_raven import Raven
    >>> deets = {'userid': 'ab123', 'pwd': 'XXXX'}
    >>> conn = Raven(url='http://qje.oxfordjournals.org', login=deets)
    >>> s = conn.session
    
JSTOR, EBSCOhost and Wiley are Raven subclasses specifically for logging onto www.jstor.org,
www.ebscohost.com and onlinelibrary.wiley.com, respectively.
    
    >>> from requests_raven import JSTOR
    >>> doc_id = '10.1086/682574'
    >>> conn = JSTOR(login=deets)
    >>> html = conn.html(id=doc_id)
    >>> pdf = conn.pdf(id=doc_id, file='article.pdf')
    
Full documentation at <http://www.erinhengel.com/software/requests-aeaweb>.

:copyright: (c) 2015 by Erin Hengel.
:license: Apache 2.0, see LICENSE for more details.
"""

__title__ = 'requests_aeaweb'
__version__ = '0.0.1'
__author__ = 'Erin Hengel'
__license__ = 'Apache 2.0'
__copyright__ = 'Copyright 2016 Erin Hengel'


from .aeaweb import AEAweb
from .aer import AER