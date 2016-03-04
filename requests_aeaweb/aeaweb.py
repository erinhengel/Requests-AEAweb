# -*- coding: utf-8 -*-

import sys
import traceback
import re
import getpass
from bs4 import BeautifulSoup
import requests

class AEAweb(object):
    """ Creates a custom Requests class to authenticate AEAweb user.
        Requests Session object stored in session attribute for reuse.
    """
    def __init__(self, login={}):
        
        # Ask for username and password if not supplied.
        if 'username' not in login:
            login['username'] = input('username: ')
        if 'password' not in login:
            login['password'] = getpass.getpass(stream=sys.stderr, prompt='password: ')
        
        # Input value to submit form.
        login['temp_pswd'] = 0
        
        # Start session and store in session attribute.
        self.session = requests.Session()
        
        # Root site.
        aea_site = 'https://www.aeaweb.org/'
        
        # Open web login form.
        aea_login = '{}/ms2/index.php'.format(aea_site)
        request = self.session.get(aea_login)
        
        # Grab CSRFToken.
        soup = BeautifulSoup(request.text, 'html.parser')
        for script in soup.find_all(attrs={'type':'text/javascript'}):
            js_text = script.text.replace('\n', '').replace('\r', '').replace('\t', '')
            match = re.search('addCSRFToken\(\"([a-z\d]+)\"\);', js_text)
            if match:
                login['csrf_token'] = match.group(1)
                break
        
        # AJAX login.
        aea_ajax = '{}/ms2/functions/ajax_login.php'.format(aea_site)
        post = self.session.post(aea_ajax, data=login)
        
        # Save destination URL.
        self.url = aea_site
        