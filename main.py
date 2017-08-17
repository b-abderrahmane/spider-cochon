import urlparse
import time
import timeit

from urllib import urlencode
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium import webdriver
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary

PAYLOADS = open("payloads/xss.pld").readlines()
url = "http://172.16.1.203/"
driver_path = "drivers/geckodriver"


def get_forms(driver):
    return driver.find_elements_by_tag_name("form")


def get_links(driver):
    return [tag.get_attribute("href") for tag in driver.find_elements_by_tag_name("a") if tag.get_attribute("href")]


def format_url_args(args_dict):
    url_args = ""
    for key, val in args_dict.iteritems():
        url_args += "%s=%s&" % (key, val.decode("utf-8"))
    return url_args[:-1]

def fuzz_name_anchros():
    pass

def fuzz_get_params(link, payloads):
    for payload in payloads:
        parsed = urlparse.urlparse(link)
        print link
        for arg in urlparse.parse_qs(parsed.query).keys():
            params = {arg: payload}
            url_parts = list(urlparse.urlparse(link))
            query = dict(urlparse.parse_qsl(url_parts[4]))
            query.update(params)
            url_parts[4] = format_url_args(query)
            urlparse.parse_qs(parsed.query)[arg] = payload
            new_url = (urlparse.urlunparse(url_parts))
            driver.get(new_url)
            time.sleep(0.5)
            try:
                alert = driver.switch_to.alert
                alert.accept()
                print "SOMETHING HERE --- checked '%s' for '%s' in '%s' " % (payload, arg, new_url)
                return True
            except Exception as e:
                continue
                #print "nothing to see here --- checked '%s' for '%s' in '%s'" % (payload, arg, new_url)
    return False

if __name__ == '__main__':

    driver = webdriver.Firefox(executable_path=driver_path)

    driver.get(url)
    driver.implicitly_wait(1)

    links = get_links(driver)

    for link in links:

        print link
        driver.get(link)
        forms = get_forms(driver)
        if forms:
            print link, forms

        """
        if "xss" in link:
            start = time.time()
            fuzz_get_params(link, PAYLOADS)
            end = time.time()
            print(end - start)
            print link
        """
    driver.close()
