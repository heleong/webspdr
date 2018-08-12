#!/usr/bin/python

from urllib.request import build_opener
import urllib.request
import urllib.error
import urllib.parse
import urllib.robotparser
from http.cookiejar import CookieJar
import re, datetime, time

class Throttle(object):
    """Class for throttling b/w requests to the same domain"""
    def __init__(self, delay):
        self.delay = delay
        self.visited_domains = {}

    def wait(self, url):
        domain = urllib.parse.urlparse(url).netloc
        last_access = self.visited_domains.get(domain)

        print("Last access for domain: ", domain, " is ", last_access)
        if self.delay > 0 and last_access is not None:
            sleep_secs = self.delay - (datetime.datetime.now() - last_access).seconds
            print("Sleep time: ", sleep_secs, " for domain: ", domain)
            if sleep_secs > 0:
                time.sleep(sleep_secs)
        print("Wait for domain: ", domain)
        self.visited_domains[domain] = datetime.datetime.now()
        print("Last access for domain: ", domain, " is ",
              self.visited_domains[domain])

def download(url, user_agent='wswp', num_retry=2):
    """
    Download a given url and return html 
    """
    """
    if not urllib.robotparser.RobotFileParser().can_fetch(user_agent, url):
        print("Blocked by robot.txt: ", url)
        return None
    """
    print("Downloading: ", url)
    headers = {'User-Agent': user_agent}
    request = urllib.request.Request(url, headers=headers)

    cookie = CookieJar()
    opener = build_opener(urllib.request.HTTPCookieProcessor(cookie))

    try:
        response = opener.open(request)

    except urllib.error.URLError as e:
        print("Download error: ", e.reason)
        print("Download code: ", e.code)
        response = None

        if num_retry > 0:
            if hasattr(e, 'code') and 500 <= e.code < 600:
                return download(url, user_agent, num_retry-1)

    if response is not None:
        return response.read().decode('utf-8')


def crawl_links(seed_url, regex, max_depth = 2):
    """
    Crawl from the given seed URL following links matches regex
    """
    crawl_queue = [seed_url]
    throttle = Throttle(5)
    seen = {} 
    while crawl_queue:
        url = crawl_queue.pop()
        throttle.wait(url)
        html = download(url)
        depth = 0 if not seen.get(url) else seen.get(url)
        depth += 1
        seen[url] = depth
        print("Seen: ", seen)
        if html is not None and depth < max_depth:
            for link in get_links(html):
                if re.match(regex, link):
                    print("Found matching link:", link)
                    link = urllib.parse.urljoin(seed_url, link)
                    crawl_queue.append(link)

def get_links(html):
    """
    Return a list of links from html
    """
    #print("Getting links from: ", html)
    webpage_regex = re.compile('<a[^>]+href=["\'](.*?)["\']', re.IGNORECASE)
    links = webpage_regex.findall(html)
    print("Got links are: ", links)
    return links


if __name__ == '__main__':
    #crawl_links('http://example.webscraping.com', '/places/default/(index|view)/')
    crawl_links('https://nvidia.wd5.myworkdayjobs.com/NVIDIAExternalCareerSite/',
                '/')
