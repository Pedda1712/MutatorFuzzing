import logging
import urllib
from bs4 import BeautifulSoup

from .Source import Information, Source

logger = logging.getLogger(__name__)

class SoupInformation(Information):
    """A dynamic piece of SUT information, fetched from the Web."""
    
    info: str
    """Information content (e.g. website text)."""
    
    url: str
    """Where this information was fetched from."""
    
    def __init__(self, info: str, url: str):
        """Initialize a piece of web information.

        Parameters
        ----------
        info : str
          Text fetched from the source (e.g. website content).
        url : str
          URL this information was fetched from.
        """
        self.info = info
        self.url = url

class SoupSource(Source):
    """An information source that parses a website to produce information."""
    
    url: str
    """URL to parse into text."""
    
    def __init__(self, url: str):
        """Initialize a website soup information source.

        Parameters
        ----------
        url : str
          URL to fetch when information gets requested.
        """
        self.url = url
        

    def fetch(self) -> SoupInformation | None:
        """Fetch information from this web source.

        A call to this function will make an HTTP request to the
        specified URL and will use 'BeautifulSoup' to parse the
        returned HTML code into text, only applying some light
        postprocessing.
        """
        logger.info(f"Attempting to fetch {self.url} ...")
        try:
            headers = {'User-Agent':'Mozilla'} # dirty, dirty, dirty
            request = urllib.request.Request(self.url,None,headers)
            html = urllib.request.urlopen(request).read()
            soup = BeautifulSoup(html, features="html.parser")
            for script in soup(["script", "style"]):
                script.extract()
            if soup.body is None:
                logger.warn("Soup body is none ..., returning no information")
                return None
            text = soup.body.get_text()
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = '\n'.join(chunk for chunk in chunks if chunk)
            return SoupContextInformation(str(text), self.url)
        except Exception as e:
            logger.warn(f"Exception {e} occured while attempting to fetch SoupSource, returning no information ...")
            return None
