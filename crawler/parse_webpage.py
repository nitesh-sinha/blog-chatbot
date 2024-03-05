import requests
from bs4 import BeautifulSoup as bs
from html2text import HTML2Text
from crawler.webpage import WebPage


class WebPageParser:
    def __init__(self, url: str):
        self.url = url

    def parse(self) -> WebPage:
        page_soup = self._download_page()
        self._clean_html_soup(page_soup)
        return WebPage(
            text=self._get_webpage_data(str(page_soup)),
            metadata=self._get_webpage_metadata(page_soup)
        )

    def _download_page(self):
        try:
            user_agent = "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) " \
                         "Chrome/79.0.3945.88 Safari/537.37"
            response = requests.get(self.url, headers={'User-Agent': user_agent})
            if response.status_code == 500:
                print(f"Encountered server error while fetching the webpage at {self.url}")
                # TODO: add wait a retry logic here
                return None
            webpage_html_soup = bs(response.content, "html.parser")
            return webpage_html_soup
        except Exception as ex:
            print(f"Exception occurred while downloading webpage content: {ex}")

    def _clean_html_soup(self, page_soup):
        # TODO: If we need to crawl links(to a certain level of depth)
        #  within the page as well, remove "link" tag from this list
        for content in page_soup(["script", "style", "link"]):
            content.extract()

    def _get_webpage_data(self, html_content: str) -> str:
        html2markdown_parser = HTML2Text()
        html2markdown_parser.images_to_alt = True # Use alt tag of image to extract textual data if it exists
        html2markdown_parser.single_line_break = True # Remove extra newline and condense the text
        html2markdown_parser.ignore_links = True # ignore links embedded within text
        markdown_text = html2markdown_parser.handle(html_content)
        return markdown_text

    def _get_webpage_metadata(self, page_soup: bs) -> dict:
        try:
            title = page_soup.title.string.strip()
        except:
            title = self.url[1:].replace('/', '-')
        page_description = page_soup.find("meta", attrs={"name": "description"})
        description = page_description.get("content") if page_description else title
        page_meta_keywords = page_soup.find("meta", attrs={"name": "keywords"})
        keywords = page_meta_keywords.get("content") if page_meta_keywords else ""
        return {
            "url": self.url,
            "title": title,
            "description": description,
            "keywords": keywords
        }
