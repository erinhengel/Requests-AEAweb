# -*- coding: utf-8 -*-

import re
from bs4 import BeautifulSoup
from requests_aeaweb import AEAweb

class AER(AEAweb):
    """ Create AEAweb connection to www.aeaweb.com.
        Download HTML of AER articles.
        Download bibliographic data of AER articles.
        Download PDF of AER articles.
    """
    def __init__(self, login):
        # Establish a Raven connection object.
        AEAweb.__init__(self, login=login)
    
    def html(self, id):
        """ Download html of document's webpage. """
        payload = {'doi': id}
        html_url = '{}/articles.php'.format(self.url)
        request = self.session.get(html_url, params=payload)
        return request.text
    
    def pdf(self, id, file=None):
        """ Download PDF of document.
            If file supplied, save to local disk. """
            
        # Get the redirection url.
        payload = {'return_to': '/doi/pdfplus/{}'.format(id)}
        pdf_url = '{}/atypon.php'.format(self.url)
        request = self.session.get(pdf_url, params=payload)
        soup = BeautifulSoup(request.text, 'html.parser')
        try:
            url = soup.meta['content'].replace('0;url=', '')
            request = self.session.get(url)
        except TypeError:
            pass
        
        if 'application/pdf' in request.headers['Content-Type']:
            mypdf = request.content
            if file:
                with open(file, 'wb') as fh:
                    fh.write(mypdf)
            return mypdf
        # If no PDF was found...
        else:
            soup = BeautifulSoup(request.text, 'html.parser')
            error = soup.find('p', 'error')
            if error:
                print(error.text)
                return
            else:
                print("Could not find PDF for article {}.\nCheck that you've correctly specified the DOI.".format(id))
                return
        
    def ref(self, id):
        """ Download bibliographic data of document.
            If affiliation, find institutions affiliated with authors. """

        # Get the webpage of the document. Using parameters from initial GET,
        # construct URL to access EBSCOhost's bibliography export function.
        html = self.html(id=id)
        soup = BeautifulSoup(html, 'html.parser')
    
        bibtex = {
            'Abstract': soup.find(attrs={'property': 'og:description'})['content'].replace('\n', ' ').replace('\r', ' ').strip(),
            'Title': soup.find(attrs={'name': 'citation_title'})['content'].strip(),
            'PubDate': soup.find(attrs={'name': 'citation_publication_date'})['content'].strip(),
            'Journal': soup.find(attrs={'name': 'citation_journal_title'})['content'].strip(),
            'ISSN': soup.find(attrs={'name': 'citation_issn'})['content'].strip(),
            'Volume': soup.find(attrs={'name': 'citation_volume'})['content'].strip(),
            'Issue': soup.find(attrs={'name': 'citation_issue'})['content'].strip(),
            'FirstPage': soup.find(attrs={'name': 'citation_firstpage'})['content'].strip(),
            'LastPage': soup.find(attrs={'name': 'citation_lastpage'})['content'].strip(),
            'DOI': soup.find(attrs={'name': 'citation_doi'})['content'].strip(),
            'Authors': [],
            'JEL': []
        }
    
        # Abstract.
        # Delete JEL codes from end of abstract and save.
        # Regular expressions used to find JEL codes at end of abstract (used also to get JEL codes below).
        jel_regex1 = re.compile(r'(.*)\(JEL[,:\s]+(.*)\)')
        jel_regex2 = re.compile(r'(.*)\((([A-Z][\d]+[,; ]*)+)\)$')
        jel_regex3 = re.compile(r'(.*)JEL[:\s](.*)')
        jel_regex1_match = None
        jel_regex2_match = None
        jel_regex3_match = None
        # Try each JEL regex match sequentially.
        jel_regex1_match = jel_regex1.search(bibtex['Abstract'])
        if jel_regex1_match:
            bibtex['Abstract'] = jel_regex1_match.group(1).strip()
        else:
            jel_regex2_match = jel_regex2.search(bibtex['Abstract'])
            if jel_regex2_match:
                bibtex['Abstract'] = jel_regex2_match.group(1).strip()
            else:
                jel_regex3_match = jel_regex3.search(bibtex['Abstract'])
                if jel_regex3_match:
                    bibtex['Abstract'] = jel_regex3_match.group(1).strip()
        
        # Volume.
        # Make integer.
        bibtex['Volume'] = int(bibtex['Volume'])
        
        # Pages.
        # Try to turn pages into integers; otherwise, keep as strings.
        # First and last pages sometimes, e.g., 1033-80; turn them into 1033 and 1080.
        try:
            bibtex['FirstPage'] = int(bibtex['FirstPage'])
            bibtex['LastPage'] = int(bibtex['LastPage'])
            if bibtex['LastPage'] < bibtex['FirstPage']:
                substr = len(str(bibtex['FirstPage'])) - len(str(bibtex['LastPage']))
                bibtex['LastPage'] = int(str(bibtex['FirstPage'])[:substr] + str(bibtex['LastPage']))
                # assert bibtex['LastPage'] >= bibtex['FirstPage']
        except ValueError:
            pass
        
        # Publication date.
        # YYYY-MM-DD format.
        date = bibtex['PubDate'].split('/')
        bibtex['PubDate'] = '{}-{}-01'.format(date[0], date[1].zfill(2))
        
        # JEL codes.
        # First look for text in JEL Classification heading of html.
        jel_text = soup.find(string=re.compile('JEL Classifications'))
        if jel_text:
            for _ in range(5):
                jel_text = jel_text.next_element
                try:
                    bibtex['JEL'] = [x.string.split(':')[0] for x in jel_text.contents if x.string is not None]
                    if bibtex['JEL']:
                        break
                except AttributeError:
                    pass
        # Otherwise, try regular expressions to find JEL codes at end of abstract.
        else:
            if jel_regex1_match:
                bibtex['JEL'] = [x for x in re.split('\W+', jel_regex1_match.group(2)) if x]
            else:
                if jel_regex2_match:
                    bibtex['JEL'] = [x for x in re.split('\W+', jel_regex2_match.group(2)) if x]
                else:
                    if jel_regex3_match:
                        bibtex['JEL'] = [x for x in re.split('\W+', jel_regex3_match.group(2)) if x]
        
        # Authors.
        # Look for author's affiliation; add to dictionary if found.
        for author in soup.find_all(attrs={'name': 'citation_author'}):
            aut_dict = {'Name': author['content']}
            try:
                if author.next_element['name'] == 'citation_author_institution':
                    aut_dict['Affiliation'] = author.next_element['content']
            except KeyError:
                pass
            bibtex['Authors'].append(aut_dict)
                
        return bibtex
