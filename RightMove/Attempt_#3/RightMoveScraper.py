"""
What? Right Move scrapper

Code from taken from the reference below, but is heavily
modified. As per T&Cs of RightMove this use of their website
is not allowed. so, please do not use it.
Referece: https://github.com/toby-p/rightmove_webscraper.py
          https://docs.python-guide.org/scenarios/scrape/
"""

# Import modules
import datetime as dt
import numpy as np
import pandas as pd
import requests
from lxml import html


class RightmoveData:
    """Scraper main class.
    
    The `RightmoveData` webscraper collects structured data on properties
    returned by a search performed on www.rightmove.co.uk

    An instance of the class provides attributes to access data from the search
    results, the most useful being `get_results`, which returns all results as a
    Pandas DataFrame object.

    The query to rightmove can be renewed by calling the `refresh_data` method.
    """
    
    def __init__(self, url: str, verbose: bool = True):
        """Initialisation.
        
        Initialise the scraper with a URL from the results of a property
        search performed on www.rightmove.co.uk. Please note the order in
        which theline are executed is important.

        Args:
            url (str): full HTML link to a page of rightmove search results.
            get_floorplans (bool): optionally scrape links to the individual
                floor plan images for each listing (be warned this drastically
                increases runtime so is False by default).
        """
        
        self.verbose = verbose
        self._url = url
        self._validateURL()

        self._status_code = self._getStatusCode(url)
        self._first_page = self._getPageContent(url)
                        
        self._results = self._getResults()
        
        
    def _getStatusCode(self, url: str):
        """Request URL
        
        Request from URL some info
        
        Parameters
        ----------
            url : string
                The URL as in : https://www.rightmove.co.uk/property-to-rent ...
        
        Returns
        -------
            status_code : number 
            content : web page content, This is too long to be shown on screen.
                      One alternative would be to dump it into a .txt file.
        """
        
        r = requests.get(url)
        #if self.verbose == True:
            #print("status_code", r.status_code)                        
        return r.status_code

    def _getPageContent(self, url: str):
        """Request URL
        
        Request from URL some info
        
        Parameters
        ----------
            url : string
                The URL as in : https://www.rightmove.co.uk/property-to-rent ...
        
        Returns
        -------
            status_code : number 
            content : web page content, This is too long to be shown on screen.
                      One alternative would be to dump it into a .txt file.
        """
        
        r = requests.get(url)
        if self.verbose == True:
            print("status_code", r.status_code)                        
        return r.content
    
    def _validateURL(self):
        
        """Validate URL.

        Basic validation that the URL at least starts in the right format and
        returns status code 200.
        """
        
        real_url = "{}://www.rightmove.co.uk/{}/find.html?"
        protocols = ["http", "https"]
        types = ["property-to-rent", "property-for-sale", "new-homes-for-sale"]
        urls = [real_url.format(p, t) for p in protocols for t in types]
        conditions = [self.url.startswith(u) for u in urls]
        conditions.append(self._getStatusCode == 200)
        if not any(conditions):
            raise ValueError(f"Invalid rightmove search URL:\n\n\t{self.url}")
        else:
            if self.verbose == True:
                print("URL Validated!")
            return "URL Validated!"

    @property
    def url(self):
        return self._url

    @property
    def get_results(self):
        """Pandas DataFrame of all results returned by the search."""
        return self._results

    @property
    def results_count(self):
        """Total number of results returned by `get_results`. Note that the
        rightmove website may state a much higher number of results; this is
        because they artificially restrict the number of results pages that can
        be accessed to 42."""
        return len(self.get_results)

    @property
    def average_price(self):
        """Average price of all results returned by `get_results` (ignoring
        results which don't list a price)."""
        total = self.get_results["price"].dropna().sum()
        return total / self.results_count

    def summary(self, by: str = None):
        """DataFrame summarising results by mean price and count. Defaults to
        grouping by `number_bedrooms` (residential) or `type` (commercial), but
        accepts any column name from `get_results` as a grouper.

        Args:
            by (str): valid column name from `get_results` DataFrame attribute.
        """
        if not by:
            by = "type" if "commercial" in self.rent_or_sale else "number_bedrooms"
        assert by in self.get_results.columns, f"Column not found in `get_results`: {by}"
        df = self.get_results.dropna(axis=0, subset=["price"])
        groupers = {"price": ["count", "mean"]}
        df = df.groupby(df[by]).agg(groupers)
        df.columns = df.columns.get_level_values(1)
        df.reset_index(inplace=True)
        if "number_bedrooms" in df.columns:
            df["number_bedrooms"] = df["number_bedrooms"].astype(int)
            df.sort_values(by=["number_bedrooms"], inplace=True)
        else:
            df.sort_values(by=["count"], inplace=True, ascending=False)
        return df.reset_index(drop=True)

    @property
    def rent_or_sale(self):
        """String specifying if the search is for properties for rent or sale.
        Required because Xpaths are different for the target elements."""
        if "/property-for-sale/" in self.url or "/new-homes-for-sale/" in self.url:
            return "sale"
        elif "/property-to-rent/" in self.url:
            return "rent"
        elif "/commercial-property-for-sale/" in self.url:
            return "sale-commercial"
        elif "/commercial-property-to-let/" in self.url:
            return "rent-commercial"
        else:
            raise ValueError(f"Invalid rightmove URL:\n\n\t{self.url}")

    @property
    def results_count_display(self):
        """Returns an integer of the total number of listings as displayed on
        the first page of results. Note that not all listings are available to
        scrape because rightmove limits the number of accessible pages."""
        tree = html.fromstring(self._first_page)
        xpath = """//span[@class="searchHeader-resultCount"]/text()"""
        return int(tree.xpath(xpath)[0].replace(",", ""))

    @property
    def page_count(self):
        """Returns the number of result pages returned by the search URL. There
        are 24 results per page. Note that the website limits results to a
        maximum of 42 accessible pages."""
        page_count = self.results_count_display // 24
        if self.results_count_display % 24 > 0:
            page_count += 1
        # Rightmove will return a maximum of 42 results pages, hence:
        if page_count > 42:
            page_count = 42
        return page_count

    def _getPage(self, request_content: str):
        """Get the page.
        
        Method to scrape data from a single page of search results. 
        Used iteratively by the `getResults` method to scrape data from 
        every page returned by the search.
        """
               
        # Process the html:
        """
        tree now contains the whole HTML file in a nice tree structure 
        which we can go over two different ways: XPath and CSSSelect. 
        XPath is a way of locating information in structured documents 
        such as HTML or XML documents.
        """
        tree = html.fromstring(request_content)        
        #print(dir(tree))        
        
        # Set xpath for price:
        if "rent" in self.rent_or_sale:
            xp_prices = """//span[@class="propertyCard-priceValue"]/text()"""
        elif "sale" in self.rent_or_sale:
            xp_prices = """//div[@class="propertyCard-priceValue"]/text()"""
        else:
            raise ValueError("Invalid URL format.")

        # Set xpaths for listing title, property address, URL, and agent URL:        
        """
        How to get get the xpath (the alternative is to use CSS but in the long
        run, you'll run into problem)
        https://www.octoparse.com/blog/xpath-introduction-use-xpath-to-scrape-web-data#
        this symbol "//" allows you to navigate strain to the tag you are interested
        withouth prividin the full path
        """
        
        xp_titles = """//div[@class="propertyCard-details"]\
        //a[@class="propertyCard-link"]\
        //h2[@class="propertyCard-title"]/text()"""
        xp_addresses = """//address[@class="propertyCard-address"]//span/text()"""
        xp_weblinks = """//div[@class="propertyCard-details"]//a[@class="propertyCard-link"]/@href"""
        xp_agent_urls = """//div[@class="propertyCard-contactsItem"]\
        //div[@class="propertyCard-branchLogo"]\
        //a[@class="propertyCard-branchLogo-link"]/@href"""

        xp_fronrPageDescription = """//div[@class="propertyCard-description"]//span/text()"""
                                
    
        # Create data lists from xpaths:
        price_pcm = tree.xpath(xp_prices)          
        titles = tree.xpath(xp_titles)
        addresses = tree.xpath(xp_addresses)
        base = "http://www.rightmove.co.uk"
        weblinks = [f"{base}{tree.xpath(xp_weblinks)[w]}" for w in range(len(tree.xpath(xp_weblinks)))]
        agent_urls = [f"{base}{tree.xpath(xp_agent_urls)[a]}" for a in range(len(tree.xpath(xp_agent_urls)))]
        fronrPageDescriptions = tree.xpath(xp_fronrPageDescription)
        
        # Store the data in a Pandas DataFrame:
        data = [price_pcm, titles, addresses, weblinks, agent_urls, fronrPageDescriptions]        
        temp_df = pd.DataFrame(data)
        temp_df = temp_df.transpose()
        columns = ["price", "type", "address", "url", "agent_url", "frontPageDescription"]
        
        temp_df.columns = columns

        # Drop empty rows which come from placeholders in the html:
        temp_df = temp_df[temp_df["address"].notnull()]

        return temp_df

    def _getResults(self):
        """Get the results.

        Build a Pandas DataFrame with all results returned by the search.        
        """
        results = self._getPage(self._first_page)
        
        if self.verbose == True:
             print("Page No:", self.page_count)

        StopIteration
        # Iterate through all pages scraping results:
        for p in range(1, self.page_count + 1, 1):
            print("Scraping page No:", p)
            # Create the URL of the specific results page:
            p_url = f"{str(self.url)}&index={p * 24}"

            # Make the request:
            #status_code, content = self._request(p_url)
            status_code = self._getStatusCode(p_url)
            content = self._getPageContent(p_url)

            # Requests to scrape lots of pages eventually get status 400, so:
            if status_code != 200:
                print("GOT BAD STATUS CODE!")
                break

            # Create a temporary DataFrame of page results:            
            #print("----->>>>>>", p_url)
            temp_df = self._getPage(content)
            #print(temp_df.columns)            

            # Concatenate the temporary DataFrame with the full DataFrame:
            frames = [results, temp_df]
            results = pd.concat(frames)


        # Reset the index:
        results.reset_index(inplace=True, drop=True)        
        
        # Convert price column to numeric type:
        results["price"].replace(regex=True, inplace=True, to_replace=r"\D", value=r"")
        results["price"] = pd.to_numeric(results["price"])

        # Extract postcodes to a separate column:
        pat = r"\b([A-Za-z][A-Za-z]?[0-9][0-9]?[A-Za-z]?)\b"
        results["postcode"] = results["address"].astype(str).str.extract(pat, expand=True)

        # Extract number of bedrooms from `type` to a separate column:
        pat = r"\b([\d][\d]?)\b"
        results["number_bedrooms"] = results["type"].astype(str).str.extract(pat, expand=True)
        results.loc[results["type"].str.contains("studio", case=False), "number_bedrooms"] = 0
        results["number_bedrooms"] = pd.to_numeric(results["number_bedrooms"])

        # Clean up annoying white spaces and newlines in `type` column:
        results["type"] = results["type"].str.strip("\n").str.strip()
      

        return results
