#-*- coding: utf-8 -*-

"""
Requests-AEAweb is a custom Requests class to log onto AEAweb.org, the website of the
American Economic Association. Basic usage for returning a Requests session object:
    
    >>> from requests_aeaweb import AEAweb
    >>> deets = {'username': 'someuser', 'password': 'XXXX'}
    >>> conn = AEAweb(login=deets)
    >>> s = conn.session
    
The AER subclass contains methods to download the webpage HTML, PDF
and bibliographic information of articles published in the Amercan Economic Review.
    
    >>> from requests_aeaweb import AER
    >>> doc_id = '10.1257/aer.20140289'
    >>> conn = AER(login=deets)
    >>> html = conn.html(id=doc_id)
    >>> ref = conn.ref(id=doc_id)
    >>> pdf = conn.pdf(id=doc_id, file='article.pdf')
    
Full documentation at <http://www.erinhengel.com/software/requests-aeaweb>.

:copyright: (c) 2016 by Erin Hengel.
:license: Apache 2.0, see LICENSE for more details.
"""

__title__ = 'requests_aeaweb'
__version__ = '0.0.1'
__author__ = 'Erin Hengel'
__license__ = 'Apache 2.0'
__copyright__ = 'Copyright 2016 Erin Hengel'


from .aeaweb import AEAweb
from .aer import AER
