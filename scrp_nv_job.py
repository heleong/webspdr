#!/usr/bin/python

from urllib.request import build_opener
import urllib.request
import urllib.error
import urllib.parse
import urllib.robotparser
from http.cookiejar import CookieJar
import re, datetime, time
from selenium import webdriver
import logging
import pymongo

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
    logging.basicConfig(level=logging.INFO,
                format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                datefmt='%a, %d %b %Y %H:%M:%S')

    nv_job_url = "https://nvidia.wd5.myworkdayjobs.com/NVIDIAExternalCareerSite/"
    chrome_bin = "/usr/local/bin/chromedriver"
    opts = webdriver.ChromeOptions()
    opts.add_argument('headless')

    br = webdriver.Chrome(executable_path=chrome_bin, chrome_options=opts)

    br.get(nv_job_url)

    #wait for js to complete execute, signal is title changes from "Workday" to "Search for Jobs"
    while br.title != "Search for Jobs":
        time.sleep(2)

    span_total_results = br.find_element_by_id("wd-FacetedSearchResultList-PaginationText-facetSearchResultList.newFacetSearch.Report_Entry")

    #TODO: change total results matching from split()[0] to regex matching
    total = span_total_results.text.split(' ')[0]
    logging.info("Total open: " + total)
    #Get today's new open #
    lis = br.find_elements_by_tag_name("li")
    today_open_num = 0
    for i in lis:
        if i.text.find("Posted Today") != -1:
            today_open_num += 1

    ids = {"jobcategory": "wd-Facet-jobFamilyGroup", \
            "countries": "wd-Facet-locationHierarchy1", \
            "locations": "wd-Facet-locations", \
            "jobtype": "wd-Facet-workerSubType",\
            "full_part_time": "wd-Facet-timeType"}
    #ids = {"jobcategory": "wd-Facet-jobFamilyGroup"}

    #
    #connect to local mongodb localhost:27017
    #
    client = pymongo.MongoClient("localhost", 27017)
    db = client.nvidiajobs

    for k, v in ids.items():
        #find each job category section
        el = br.find_element_by_id(v)
        #click '>' to expand
        #expanded by default
        #ex_btn = el.find_element_by_id("wd-icon-chevron-down")
        #ex_btn.click()
        #click 'more' to expand
        more_btn = el.find_element_by_css_selector("span[title=More]")

        if more_btn.is_displayed():
            more_btn.click()
        #find all categories
        catgrs = el.find_elements_by_tag_name("label")
        opens = el.find_elements_by_tag_name("span")  #NOTE - opens data is only useful from index [1,n-2]
        logging.info(str(opens[1].text))
        data = {"total": total, "today_open": today_open_num}
        for i in range(len(catgrs)):
            logging.info(str(i) + " " + str(catgrs[i].text) + " " + str(i+2) + " " + str(opens[i+2].text))
            key = str(catgrs[i].text).replace(".","") #NOTE - Remove '.' to eliminate error from mongodb complaints about invalid key with '.'
            value = int(str(opens[i+2].text)[1:-1])
            data[key] = value

        logging.info(data)
        db[k].insert(data)

    client.close()
    br.quit()
