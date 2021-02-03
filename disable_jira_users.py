from os import environ
import time
import argparse
from selenium_client import Selenium
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.keys import Keys

import pandas as pd
from datetime import datetime, timedelta
import dateutil
from pathlib import Path

JIRA_SERVER = "https://admin.atlassian.com/"

def main():
    args = parse_args()
    selenium = Selenium(headless=False)
    get_user_management_session(selenium.driver, selenium)
    
    user_file = None
    if args.users == None:
        # No users file provided, let's download
        user_file = download_user_file(selenium.driver, selenium)
    else:
        # Let's use the provided one
        user_file = args.users
    email_address_to_disable = get_inactive_users(user_file, args.days)
    #print(email_address_to_disable)
    for user in email_address_to_disable:
        set_jira_user_inactive(selenium.driver, selenium, user)
    
    # Clean up the downloaded file
    if args.users == None:
        Path(user_file).unlink()
    quit_driver(selenium.driver)

def parse_args():
    """ Parse command line args """
    parser = argparse.ArgumentParser(description='Disable user in JIRA')
    parser.add_argument('--users', required=False, help='Path to export.csv file with users exported from Jira')
    parser.add_argument('--days', required=True, help='Number of days inactive (e.g. 60 or 90)', type=int)
    return parser.parse_args()


def get_user_management_session(driver, selenium):
    """ Get an authenticated session to manage users """
    try:
        # Load the page
        selenium.get_page(JIRA_SERVER)
        
        # Enter credentials and login
        selenium.wait_for_element_id_to_click('username')
        driver.find_element_by_id('username').send_keys(selenium.user)
        selenium.wait_for_element_id_to_click('login-submit')
        selenium.move_and_click(driver.find_element_by_xpath('//*[@id="login-submit"]'))
        selenium.wait_for_element_id_to_click('password')
        driver.find_element_by_id("password").send_keys(selenium.password)
        driver.find_element_by_id("login-submit").click()
        print("[*] Logged into admin.atlassian.com")
        
        # Click 'Manage users'
        driver.implicitly_wait(5)
        selenium.move_and_click(driver.find_element_by_xpath("//*[contains(text(), 'Manage users')]"))
        print("[*] Onto the user management portal")
        #sleep(2)
        
    except Exception as error: # pylint: disable=broad-except
        print("[!] {}".format(error))
        selenium.save_screenshot('{}-{}'.format(user, int(time())))
        quit_driver(driver)


def download_user_file(driver, selenium):
    try:
        # Click "Export users"
        selenium.wait_for_element_xpath_to_click("//*[contains(text(), 'Export users')]")

        '''
        Sometimes we get a "StaleElementException" if the element is reloaded between moving 
        and clicking, so in that case we retry twice
        '''
        attempts = 0
        while attempts < 5:
            try:
                selenium.move_and_click(driver.find_element_by_xpath("//*[contains(text(), 'Export users')]"))
                break
            except Exception as error:
                print("[!] {}".format(error))
            attempts+=1
        # Click "Download file"
        driver.implicitly_wait(15)
        selenium.move_and_click(driver.find_element_by_xpath("//*[contains(text(), 'Download file')]"))

        # wait to download the file
        while not is_download_finished("/tmp/"):
            time.sleep(1)

        if not Path('/tmp/export-users.csv').exists():
            print("[!] Failed to download export-users.csv")
            quit_driver(driver)
            exit(1)
        
        return "/tmp/export-users.csv"

    except Exception as error: # pylint: disable=broad-except
        print("[!] {}".format(error))
        quit_driver(driver)
        exit(1)


def is_download_finished(temp_folder):
    chrome_temp_file = sorted(Path(temp_folder).glob('*.crdownload'))
    downloaded_files = sorted(Path(temp_folder).glob('*.csv'))
    if (len(firefox_temp_file) == 0) and \
       (len(chrome_temp_file) == 0) and \
       (len(downloaded_files) >= 1):
        return True
    else:
        return False

def set_jira_user_inactive(driver, selenium, user):
    """ Disable a Jira user"""
    try:
        # Click Search field and enter the username
        selenium.move_and_click(driver.find_element_by_xpath("//input[@aria-label='Search']"))
        # First clear any input from previous queries
        driver.find_element_by_xpath("//input[@aria-label='Search']").send_keys(Keys.CONTROL + "a")
        driver.find_element_by_xpath("//input[@aria-label='Search']").send_keys(Keys.DELETE)
        driver.find_element_by_xpath("//input[@aria-label='Search']").send_keys(user)
        
        # Wait one second to fetch results before continueing
        time.sleep(1)
        
        # Click on the button with three-dots
        driver.find_element_by_css_selector('.cLrmQm').click()
        # Click on 'Revoke site access'
        selenium.move_and_click(driver.find_element_by_xpath("//*[contains(text(), 'Revoke site access')]"))

    # Click final red 'Revoke site access' button
        selenium.wait_for_element_css_selector_to_click('#submit-activate-user-modal')
        driver.find_element_by_css_selector('#submit-activate-user-modal').click()
        time.sleep(1)
        print("[+] User {} succesfully disabled".format(user))
    
    except NoSuchElementException as e:
        if "Revoke site access" in str(e):
            print("[!] Cannot Revoke site access, {} might be already inactive".format(user))      
        time.sleep(1)
    
    except Exception as error: # pylint: disable=broad-except
        print("[!] {}".format(error))
        selenium.save_screenshot('{}-{}'.format(user, int(time())))
        driver.quit()

def quit_driver(driver):
    driver.quit()
    print('[*] quitting')


def get_inactive_users(filename, days):
    pd.set_option('display.max_rows', None)
    df = pd.read_csv(filename, parse_dates=['Last seen in Jira Software', 'created'])
    df = df.loc[df['Last seen in Jira Software'] != 'Never logged in']
    df['Last seen in Jira Software'] = df['Last seen in Jira Software'].apply(dateutil.parser.parse)

    results = df[(df['Last seen in Jira Software'] < numberOfDaysAgo(days)) & (df['created'] < numberOfDaysAgo(days)) & (df['active'] == 'Yes')]
    print("[+] Found " + str(len(results['email'].unique())) + " inactive users")
    print(results[['email', 'Last seen in Jira Software']])
    input("[?] Do you want to disable these Jira users? Press any key to continue. Press CTRL+C to abort")
    return set(results['email'].to_list())

def numberOfDaysAgo(numberOfDays):
    return datetime.now() - timedelta(days=numberOfDays)
    

if __name__ == "__main__":
    main()
