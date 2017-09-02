import urlparse
import time
import logging
import sys

from urllib import quote
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium import webdriver
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary


url = "http://172.16.1.203/"
driver_path = "drivers/geckodriver"

log = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, stream=sys.stdout)


def get_forms(driver):
    return driver.find_elements_by_tag_name("form")


def get_links(driver):
    return [tag.get_attribute("href") for tag in driver.find_elements_by_tag_name("a") if tag.get_attribute("href")]


def format_url_args(args_dict):
    url_args = ""
    for key, val in args_dict.iteritems():
        url_args += "%s=%s&" % (key, val.decode("utf-8"))
    return url_args[:-1]


def fuzz_name_anchors(link, paylods):
    if "#" in link:
        new_link = link.split("#")[0]
        new_link += "#"
        for payload in paylods:
            fuzzed_link = new_link + payload.decode("utf-8")
            driver.get(fuzzed_link)
            driver.refresh()
            time.sleep(0.5)
            if detect_xss(driver):
                log.info("XSS found in url : %s at anchor using payload : %s "
                         "In order to verify it check : %s", link, payload, fuzzed_link)
                return True


def replace_get_arg(parsed_url, arg, new_value):
    params = {arg: new_value}
    url_parts = list(urlparse.urlparse(link))
    query = dict(urlparse.parse_qsl(url_parts[4]))
    query.update(params)
    url_parts[4] = format_url_args(query)
    urlparse.parse_qs(parsed_url.query)[arg] = new_value
    new_url = (urlparse.urlunparse(url_parts))
    return new_url


def detect_xss(driver):
    try:
        alert = driver.switch_to.alert
        alert.accept()
        return True
    except Exception as e:
        return False


def fuzz_get_params(link, payloads):
    for payload in payloads:
        parsed = urlparse.urlparse(link)
        for arg in urlparse.parse_qs(parsed.query).keys():
            new_url = replace_get_arg(
                parsed_url=parsed,
                arg=arg,
                new_value=payload
            )
            driver.get(new_url)
            time.sleep(0.5)
            if detect_xss(driver):
                log.info("XSS found in url : %s at arg : %s using payload : %s "
                         "In order to verify it check : %s", link, arg, payload, new_url)
                return True

    log.info("Finished checking [%s], no XSS found", link)
    return False


if __name__ == '__main__':

    driver = webdriver.Firefox(executable_path=driver_path)

    driver.get(url)
    driver.implicitly_wait(2)

    links = get_links(driver)
    xss_paylods = open("payloads/xss.pld").readlines()
    for link in links:

        driver.get(link)
        forms = get_forms(driver)

        if "xss" in link:
            start = time.time()
            fuzz_get_params(link, xss_paylods)
            fuzz_name_anchors(link, xss_paylods)
            end = time.time()
            duration = end - start
            log.info("Url [%s] XXSyzed within %.2f seconds", link, duration)

    driver.close()
