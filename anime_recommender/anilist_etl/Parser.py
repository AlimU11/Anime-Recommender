import pickle
import re
import time
from collections import defaultdict

import bs4
import tqdm
from selenium import webdriver
from selenium.common.exceptions import (
    ElementClickInterceptedException,
    NoSuchElementException,
)
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

BASE = 'https://anilist.co'
NOT_FOUND = '/img/404/404_chan1.jpg'
HEADERS = {
    'userAgent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.53 Safari/537.36',
}


class Parser:
    """Parser for AniList."""

    @staticmethod
    def init_driver():
        """Initialize the driver."""
        u = 'https://anilist.co/anime/1'

        chrome_options = Options()
        chrome_options.add_argument('--disable-extensions')
        # chrome_options.add_argument("--headless")

        driver = webdriver.Chrome(options=chrome_options)

        driver.implicitly_wait(10)
        driver.execute_cdp_cmd('Network.setUserAgentOverride', HEADERS)
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        driver.get(u)
        time.sleep(3)

        # no need to automatically click using ipynb with headfull mode
        # try:
        #    WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH,'''/html/body/div[1]/div/div/div/div[2]/div/button[2]'''))).click()
        # except Exception as e:
        #    print(e)

        return driver

    @staticmethod
    def parse_links(driver: webdriver.Chrome, links: list[str]) -> dict:
        """Parse the links using the driver.

        Parameters
        ----------
        driver : webdriver
            Selenium webdriver.

        links : list[str]
            List of links to parse.

        Returns
        -------
        dict
            Dictionary with parsed html pages.
        """
        data = {}

        for link in tqdm.tqdm(links):

            # load and check page
            page = BASE + link
            driver.get(page)
            driver.implicitly_wait(2)
            if NOT_FOUND in driver.page_source:
                continue

            # get id
            pattern = re.search("""anime\/([0-9]+)""", link)
            idx = pattern.group(1)

            # click spoiler toggle
            try:
                btn = driver.find_element(By.CLASS_NAME, 'spoiler-toggle')
                action = webdriver.ActionChains(driver)
                action.move_to_element(btn)

                try:
                    WebDriverWait(driver, 3).until(EC.element_to_be_clickable(btn)).click()

                    # unfocus tags panel
                    element = driver.find_element(By.CLASS_NAME, 'review button edit')
                    action.move_to_element(element)
                except ElementClickInterceptedException as e:
                    print(e)
            except NoSuchElementException as e:
                pass

            data[idx] = driver.page_source

        return data

    @staticmethod
    def parse(driver: webdriver, min_v: int, max_v: int, links: list[str], step: int = 1000):
        """Parse links in batches. Each batch is saved to a pickle file.

        Parameters
        ----------
        driver : webdriver
            Selenium webdriver.

        min_v : int
            Minimum value in `links` slice.

        max_v : int
            Maximum value in `links` slice.

        links : list[str]
            List of links to parse.

        step : int, optional
            Step size for slicing `links`, by default 1000.
        """
        for i in range(min_v, max_v, step):
            data = Parser.parse_links(driver, links[i : i + step])

            with open(f'from_{i}_to_{i+step-1}.pickle', 'wb') as f:
                pickle.dump(data, f, protocol=pickle.HIGHEST_PROTOCOL)


def process_string(s: str) -> str:
    """Preprocess parsed string. Remove spaces, newlines and tabs.

    Parameters
    ----------
    s : str
        String to preprocess.


    Returns
    -------
    str
        Preprocessed string.
    """
    return s.text.lower().strip().replace('\n', '').replace('\t', '')


def process_list(l: list[bs4.element.Tag]) -> list[str]:
    """Preprocess parsed list. Remove spaces, newlines and tabs.

    Parameters
    ----------
    l : list[bs4.element.Tag]
        List to preprocess.

    Returns
    -------
    list[str]
        Preprocessed list.
    """
    return [i.text.strip().replace('\n', '').replace('\t', '') for i in l.select('a')]


def process_title(s: str) -> str:
    """Process title. Not removing spaces, newlines and tabs.

    Parameters
    ----------
    s : str
        String to preprocess.

    Returns
    -------
    str
        Preprocessed title.

    """
    return s.text


dataset_process = defaultdict(lambda: process_string)
dataset_process['studios'] = process_list
dataset_process['producers'] = process_list
dataset_process['genres'] = process_list
dataset_process['romaji'] = process_title
dataset_process['english'] = process_title
dataset_process['native'] = process_title


def extract_data_task(html: str, key: str) -> dict:
    """Extract data from html.

    Parameters
    ----------
    html : str
        Html page to extract data from.

    key : str
        Page id.

    Returns
    -------
    dict
        Extracted data.
    """
    data = {}

    if NOT_FOUND in html:
        return data

    bs = bs4.BeautifulSoup(html, 'html.parser')
    data[key] = {}

    data[key]['link'] = 'https://anilist.co/anime/' + key
    data[key]['title'] = bs.find('h1').text.strip()
    data[key]['description'] = bs.find('p', {'class': 'description'}).text.strip()
    data[key]['tags'] = [
        (i.select_one('a').text.strip(), i.select_one('.rank').text) for i in bs.find_all('div', {'class': 'tag'})
    ]
    data[key]['image_src'] = bs.find('img')['src']
    dataset_types = [
        i.text.replace('\n', '').replace('\t', '').replace(' ', '_').lower()
        for i in bs.find_all('div', {'class': 'type'})
    ]
    data[key]['data'] = {
        key: dataset_process[key](value) for key, value in zip(dataset_types, bs.select('.value')) if key != 'synonyms'
    }
    data[key]['is_adult'] = len(bs.select('.adult-label')) > 0

    return data
