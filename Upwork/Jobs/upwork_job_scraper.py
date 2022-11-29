import os
import csv
import time
import pytz
import psutil
import datetime
import multiprocessing
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By


HEADLESS = True
SLEEP_TIME = 10
CACHE_DIR = 'caches'
OUTPUT_DIR = 'output'
OUTPUT_FILENAME = f"output_{datetime.datetime.now().strftime('%d_%m_%Y_%H_%M')}.csv"  # Must be in csv format
LOG_FILENAME = f"log_{datetime.datetime.now().strftime('%d_%m_%Y_%H_%M')}.csv"        # Must be in csv format
PROCNAME_1 = "geckodriver.exe"
PROCNAME_2 = "chromedriver.exe"
PROCNAME_3 = "firefox.exe"


def create_directory(directory_name, show_info=True):
    """
    Creates a directory. If it is already exist, it simply passes.
    :return:
    """
    try:
        os.mkdir(f"{directory_name}")
        if show_info:
            print(f"{directory_name} directory has been created succesfully.")

    except FileExistsError:
        if show_info:
            print(f"{directory_name} directory already exist.")
        pass


def create_torbrowser_webdriver_instance(geckodriver_path):
  options = Options()
  options.headless = HEADLESS
  firefox_capabilities = webdriver.DesiredCapabilities.FIREFOX

  firefox_capabilities['proxy'] = {
      "proxyType": "MANUAL",
      'socksProxy': '127.0.0.1:9150',
      "socksVersion": 5
  }

  driver = webdriver.Firefox(capabilities=firefox_capabilities,
                             options=options,
                             executable_path=geckodriver_path)
  return driver


def get_page_source_from_keyword(keyword, geckodriver_path):
    # Create browser instance
    driver = create_torbrowser_webdriver_instance(geckodriver_path)

    request_url = f'http://www.upwork.com/nx/jobs/search/?q={keyword.replace(" ", "%20").lower()}&sort=recency'

    driver.get(request_url)

    # Wait till the page is loaded
    WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.CLASS_NAME, "job-tile-title")))

    # Scroll to the bottom of the page
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

    # Get page source
    bsObj = BeautifulSoup(driver.page_source, "lxml")

    # Close the driver
    driver.close()

    # Write page source to file
    f = open(f"{CACHE_DIR}/{keyword}.html", "w",  encoding="utf-8")
    f.write(str(bsObj))
    f.close()


def parse_upwork_search_data(keyword, fileObj, writer):
    err_message = None

    # Try to read source file
    try:
        with open(f"{CACHE_DIR}/{keyword}.html",  encoding="utf-8") as fp:
            bsObj = BeautifulSoup(fp, 'html.parser')

    except Exception as e:
        err_message = "Read page source error."
        print(e)

    if err_message is None:
        # Try to parse data
        try:
            job_divs = bsObj.find_all('section', {'data-test':'JobTile'})

            for job_div in job_divs:

                try:
                    job_url_raw = job_div.find('h4', {'class': 'job-tile-title'}).find('a', href=True)['href']
                    job_url = "https://www.upwork.com" + job_url_raw
                except:
                    job_url = 'N/A'

                try:
                    job_title = job_div.find('h4', {'class': 'job-tile-title'}).text.strip()
                except:
                    job_title = 'N/A'

                try:
                    job_type = job_div.find('strong', {'data-test': 'job-type'}).text.strip()
                except:
                    job_type = 'N/A'

                try:
                    job_experience = job_div.find('span', {'data-test': 'contractor-tier'}).text.strip()
                except:
                    job_experience = 'N/A'

                try:
                    job_duration = job_div.find('span', {'data-test': 'duration'}).text.strip()
                except:
                    job_duration = 'N/A'

                try:
                    job_description = job_div.find('span', {'data-test': 'job-description-text'}).text.strip()
                except:
                    job_description = 'N/A'

                try:
                    job_skils = ""

                    skills_list = job_div.find_all('a', {'class': 'up-skill-badge text-muted'})

                    if len(skills_list) == 0:
                        job_skils = 'N/A'

                    else:
                        is_first = True
                        for skill in skills_list:
                            if is_first:
                                job_skils += skill.text.strip()
                                is_first = False

                            else:
                                job_skils += " | " + skill.text.strip()

                except:
                    job_skils = 'N/A'

                try:
                    job_country = job_div.find('small', {'data-test': 'client-country'}).text.strip()
                except:
                    job_country = 'N/A'

                time_scraped = datetime.datetime.now()

                data_to_write = [
                    keyword,
                    job_url,
                    job_title,
                    job_type,
                    job_experience,
                    job_duration,
                    job_description,
                    job_skils,
                    job_country,
                    time_scraped
                ]

                writer.writerow(data_to_write)

                fileObj.flush()


        except Exception as e:
            err_message = "Parse Error:\n" + str(e)


    if err_message is not None:
        success = False
    else:
        success = True

    return success, err_message


if __name__ == "__main__":
    keyword_to_scrape = [
        "Proxy",
        "Google Data Studio",
        "Looker Studio",
        'Data',
        'Data Scraping',
        'Data Extraction',
        'Web Automation',
        'Software',
        'Data Pull',
        'Web Data',
        'Website Data Pull',
        'Google Results Data',
        'Pull Google Results',
        'Webpage keyword finder',
        'Dataset',
        'Instagram',
        'Twitter',
        'Upwork',
        'Amazon',
        'Airbnb',
        'Craiglist',
        'eCommerce',
        'eBay',
        'Facebook',
        'Financial Data',
        'Fiverr',
        'Github',
        'Google Play',
        'Instagram',
        'Jobs Scraper',
        'Leads',
        'Lead Generation',
        'LinkedIn',
        'Netflix',
        'Patreon',
        'Pinterest',
        'Quora',
        'Reddit',
        'RSS',
        'Spotify',
        'SkyScanner',
        'TikTok',
        'Trip',
        'Tumblr',
        'Twitter',
        'Upwork',
        'URL Scraper',
        'Walmart',
        'Image Scraper',
        'WooCommerce',
        'Yahoo Finance',
        'Yellow Pages',
        'Youtube',
        'Zillow',
        "rates data scrape",
        "rates pull",
        "customer website data",
        "customer data pull",
        "customer data",
        "loan data",
        "financial data pull",
        "mobile data",
        "cell phone application scrape",
        "cell phone app data",
        "gaming data scrape",
        "gaming user data",
        "steam data",
        "steam advertising",
        "manufacturing data",
        "manufacturing supplier",
        "supply chain data",
        "doctor information data",
        "hospital data scrape",
        "hospital information"

    ]

    data_fields = [
        'Keyword',
        'Job Link',
        'Job Title',
        'Job Type',
        'Experience',
        'Duration',
        'Job Description',
        'Skills Required',
        'Client Country',
        'Time Scraped (GMT-5)'
    ]

    log_data_fields = [
        'Keyword',
        'Scraping Started(GMT-5)',
        'Scraping Finished(GMT-5)',
        'Time Passed (Seconds)',
        'Status',
        'Error Message'
    ]

    # Create cache directory
    create_directory(CACHE_DIR)

    # Create output directory
    create_directory('output')

    # Create output file
    output_file_name = f"{OUTPUT_DIR}/{OUTPUT_FILENAME}"
    output_file = open(output_file_name, 'w+', encoding='utf-8', newline="")

    # Create log file
    log_file_name = f"{OUTPUT_DIR}/{LOG_FILENAME}"
    log_file = open(log_file_name, 'w+', encoding='utf-8', newline="")

    # Create output csv writer
    main_writer = csv.writer(output_file, delimiter=',')

    # Create log csv writer
    log_writer = csv.writer(log_file, delimiter=',')

    # Init output file
    output_file.writelines("SEP=,\n")
    main_writer.writerow(data_fields)
    output_file.flush()

    # Init log file
    log_file.writelines("SEP=,\n")
    log_writer.writerow(log_data_fields)
    log_file.flush()

    print(f"The result will be written to {output_file_name}.")
    print(f"The log can be found at {log_file_name}.")

    # Install geckodriver
    geckodriver_path = GeckoDriverManager().install()

    while True:
        for key in keyword_to_scrape:
            print("------------------------------------")
            print(f"Scraping results for \'{key}\'")

            # Start time flag both as realtime and cpu time
            scraping_start_time_dt = datetime.datetime.now()
            scraping_start_time_cpu = time.time()

            # Create process
            p1 = multiprocessing.Process(target=get_page_source_from_keyword, args=(key, geckodriver_path, ))

            # Start the process
            p1.start()

            # Wait until the process finish
            p1.join()

            # Try to parse the data
            print(f"Parsing the scraped source of \'{key}\'")
            parse_success, error_message = parse_upwork_search_data(key, output_file, main_writer)

            if parse_success:
                print(f"Success: {parse_success}")
            else:
                print(f"Success: {parse_success}, Message: {error_message}")

            # Remove cache file
            try:
                os.remove(f"{CACHE_DIR}/{key}.html")
            except:
                pass

            # End time flag both as realtime and cpu time
            scraping_end_time_dt = datetime.datetime.now()
            scraping_end_time_cpu = time.time()

            # Calculate time passed as seconds
            time_passed = scraping_end_time_dt - scraping_start_time_dt

            # Write logs
            log_data_to_write = [
                key,
                scraping_start_time_dt,
                scraping_end_time_dt,
                time_passed,
                parse_success,
                error_message
            ]

            log_writer.writerow(log_data_to_write)

            log_file.flush()

            # Kill garbage processes to prevent memory overflow
            for proc in psutil.process_iter():
                # check whether the process name matches
                try:
                    if proc.name() == PROCNAME_1:
                        proc.kill()
                        print(f"The process {PROCNAME_1} has been killed.")

                    if proc.name() == PROCNAME_2:
                        proc.kill()
                        print(f"The process {PROCNAME_2} has been killed.")

                    if proc.name() == PROCNAME_3:
                        proc.kill()
                        print(f"The process {PROCNAME_3} has been killed.")
                except:
                    pass

            print(f"Waiting {SLEEP_TIME} seconds...")
            time.sleep(SLEEP_TIME)
