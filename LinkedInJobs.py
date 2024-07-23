"""
This script is for scraping jobs data from LinkedIn by
searching specific job title and Location.
"""

import os
import time
from typing import Dict, List
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from loguru import logger

class LinkedInJobs:
    """This class contain the function thrugh which scrap data after search"""

    def __init__(self,driver_path : str,job_title : str,job_location:str) -> None:
        self.driver_path:str=driver_path
        self.job_title:str=job_title
        self.job_location:str=job_location
        self.driver = webdriver.Chrome(service=Service(self.driver_path))
        self.job_data:Dict[str,List[str]] = {
            "titles": [],
            "subtitles": [],
            "locations": [],
            "dates": []
        }

    def search_for_job(self):
        """
        Here you can search the specific job (e.g., web scraping)
        and the area/location (e.g., Pakistan)
        """

        jobs_btn = self.driver.find_element(By.XPATH,
        '//li//a[@data-tracking-control-name="guest_homepage-basic_guest_nav_menu_jobs"]')
        jobs_btn.click()
        time.sleep(2)

        search_jobs_title = self.driver.find_element(By.XPATH,
        '//section//input[@id="job-search-bar-keywords"]')
        search_jobs_title.send_keys(self.job_title)  # enter your job title for search

        search_jobs_location = self.driver.find_element(By.XPATH,
        '//section//input[@id="job-search-bar-location"]')
        search_jobs_location.clear()
        search_jobs_location.send_keys(
            self.job_location + Keys.ENTER)  # enter your location for search
        time.sleep(10)

    def scrap_jobs_data(self):
        """The main function which scrapes jobs after search"""

        jobs_list = self.driver.find_elements(By.XPATH,
            '//ul[@class="jobs-search__results-list"]//li')
        logger.info(f"Total {len(jobs_list)} jobs found")

        for job in jobs_list:
            job_title = job.find_element(By.XPATH,
            './/div[@class="base-search-card__info"]//h3[@class="base-search-card__title"]'
            ).text
            job_subtitle = job.find_element(By.XPATH,
                './/h4[@class="base-search-card__subtitle"]').text
            job_location = job.find_element(By.XPATH,
            './/div[@class="base-search-card__metadata"]//span[@class="job-search-card__location"]'
                ).text
            job_date = job.find_element(By.XPATH,
                './/div[@class="base-search-card__metadata"]//time').text

            self.job_data["titles"].append(job_title)
            self.job_data["subtitles"].append(job_subtitle)
            self.job_data["locations"].append(job_location)
            self.job_data["dates"].append(job_date)

    def scrolldown(self):
        """This function scrolls down till end to get all the jobs data"""

        while True:

            initial_height = self.driver.execute_script("return document.body.scrollHeight")

            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(3)
            self.driver.execute_script("window.scrollBy(0, 100);")
            time.sleep(0.5)
            self.driver.execute_script("window.scrollBy(0, -100);")
            time.sleep(0.5)
            see_more_jobs=self.driver.find_element(By.XPATH,"//button[@aria-label='See more jobs']")
            if see_more_jobs.is_displayed():
                see_more_jobs.click()
                time.sleep(3)
            else:
                end_of_jobs = self.driver.find_element(By.XPATH,
                    "//p[contains(text(), 'viewed all jobs for this search')]")
                if end_of_jobs.is_displayed():
                    break

            new_height = self.driver.execute_script("return document.body.scrollHeight")
            time.sleep(2)
            if new_height==initial_height:
                break

    def output(self):
        """ This function stores the data to CSV """

        df = pd.DataFrame({
        "Job Title": self.job_data["titles"],
        "Job Subtitle": self.job_data["subtitles"],
        "Location": self.job_data["locations"],
        "Date Posted": self.job_data["dates"]
        })
        df.to_csv(f"linkedIn_{self.job_title}.csv", index=False)
        logger.success("Data saved")

    def start(self):
        """
            This is the function where we get the starting point and
            call functions which do scraping process
        """

        url = "https://www.linkedin.com/"
        self.driver.maximize_window()
        self.driver.get(url)
        time.sleep(2)

        self.search_for_job()
        self.scrolldown()
        time.sleep(1)
        self.scrap_jobs_data()
        self.output()

        self.driver.quit()

if __name__ == "__main__":
    script_dir=os.path.dirname(os.path.abspath(__file__))
    DRIVER_PATH =os.path.join(script_dir,
        "D:/Codeaza/WebDriver/chromedriver-win64/chromedriver.exe")
    JOB_TITLE="Software Engineer"
    JOB_LOCATION="Pakistan"

    scraper=LinkedInJobs(DRIVER_PATH,JOB_TITLE,JOB_LOCATION)
    scraper.start()
