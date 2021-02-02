""" Disable user in JIRA via selenium """
from os import environ, makedirs
from os.path import isdir
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException

CHROME_DRIVER = '{}/chromedriver'.format("/usr/local/bin/")
SCREENSHOT_LOCATION = '{}/selenium'.format("/usr/local/lib/python3.8/dist-packages/")
ELEMENT_TIMEOUT = 10


class Selenium(object):
    """ Selenium """
    def __init__(self, user=None, password=None, headless=True):
        if user and password:
            self.user = user
            self.password = password
        else:
            self.user = environ['USER']
            self.password = environ['PASS']

        # Headless option set
        self.headless = headless

        # Set chrome browser options
        self.options = None
        self.set_chrome_options()

        # initialize the driver
        self.driver = webdriver.Chrome(executable_path=CHROME_DRIVER, chrome_options=self.options)

    def set_chrome_options(self):
        """ Set chrome browser options """
        options = webdriver.ChromeOptions()
        # set the window size
        options.add_argument('window-size=1200x600')
        # set the execution to be headless or not
        if self.headless:
            options.set_headless()
        self.options = options

    def get_page(self, url):
        """ Get web page at url """
        self.driver.get(url)

    def save_screenshot(self, filename):
        """ Save screenshot to log dir """
        if not isdir(SCREENSHOT_LOCATION):
            makedirs(SCREENSHOT_LOCATION, exist_ok=True)
        screenshot = '{}/{}.png'.format(SCREENSHOT_LOCATION, filename)
        self.driver.get_screenshot_as_file(screenshot)
        print('Screen shot is available here: {}'.format(screenshot))


    def move_and_click(self, name):
        try:
            webdriver.ActionChains(self.driver).move_to_element(name).click(name).perform()
            #print('Page element "{}" is clicked!'.format(name))
        except Exception as ex:
            print(ex)
    
    def wait_for_element_id_to_click(self, name):
        """ Wait for element to be clickable """
        try:
            WebDriverWait(self.driver, ELEMENT_TIMEOUT) \
                .until(EC.visibility_of_element_located((By.ID, name)))
            #print('Page element "{}" is ready!'.format(name))
        except TimeoutException:
            print('Loading page element "{}" timed out!'.format(name))
            raise
  
    def wait_for_element_xpath_to_click(self, name):
        """ Wait for element to be clickable """
        try:
            WebDriverWait(self.driver, ELEMENT_TIMEOUT) \
                .until(EC.visibility_of_element_located((By.XPATH, name)))
            #print('Page element "{}" is ready!'.format(name))
        except TimeoutException:
            print('Loading page element "{}" timed out!'.format(name))
            raise
            
    def wait_for_element_css_selector_to_click(self, name):
        """ Wait for element to be clickable """
        try:
            WebDriverWait(self.driver, ELEMENT_TIMEOUT) \
                .until(EC.visibility_of_element_located((By.CSS_SELECTOR, name)))
            #print('Page element "{}" is ready!'.format(name))
        except TimeoutException:
            print('Loading page element "{}" timed out!'.format(name))
            raise
