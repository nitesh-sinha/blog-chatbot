import requests
from bs4 import BeautifulSoup as bs

class BlogCrawler:
    def __init__(self, blog_url: str):
        self.blog_base_url = blog_url

    def crawl(self):
        # Fetch sitemap of the blog
        # Parse sitemap to obtain links to all blog pages
        # (Optional) Recursively fetch embedded links in blog pages to crawl them upto a certain depth.
        sitemap_content = self.fetch_sitemap()
        return self.parse_sitemap(sitemap_content)

    def fetch_sitemap(self):
        try:
            user_agent = "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) " \
                         "Chrome/79.0.3945.88 Safari/537.37"
            response = requests.get(self.blog_base_url+"/sitemap.xml", headers={'User-Agent': user_agent})
            if response.status_code == 500:
                print(f"Encountered server error while fetching the sitemap")
                # TODO: add wait a retry logic here
                return None
            return response.content
        except Exception as ex:
            print(f"Unknown exception while downloading sitemap: {ex}")

    def parse_sitemap(self, sitemap_content):
        sitemap_soup = bs(sitemap_content, "xml")
        loc_tags = sitemap_soup.find_all("loc")
        return loc_tags
