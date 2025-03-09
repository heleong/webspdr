from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import pandas as pd
import re

#TODO: Persist data to a database MongoDB

def scrape_nvidia_job_locations():
    # Set up Chrome options
    """chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run in headless mode (no browser UI)
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")"""
    
    # Initialize the Chrome driver
    #driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    driver = webdriver.Chrome()

    try:
        # Navigate to NVIDIA's job portal
        print("Navigating to NVIDIA's job portal...")
        driver.get("https://nvidia.wd5.myworkdayjobs.com/NVIDIAExternalCareerSite")
        
        # Wait for the page to load and job listings to appear
        wait = WebDriverWait(driver, 30)
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "ul[role='list']")))
        
        # Give the page a moment to fully load
        time.sleep(5)
        
        # Find all job number
        job_number = int(driver.find_elements(By.CSS_SELECTOR, "[data-automation-id='jobFoundText']")[0].text.split(" ")[0])
        print(f"Found {job_number} jobs")
        # Find all location elements
        print("Extracting location information...")
        filters = driver.find_elements(By.CSS_SELECTOR, "[data-uxi-widget-type='filterButton']")
        
        # Extract and clean location text
        jobs = {}
        tmp = {}
        for f in filters:
            # Open filter button one by one
            f.click()
            time.sleep(2)
            # Get all selections of job locations
            selections = driver.find_elements(By.CSS_SELECTOR, "[cursor='pointer']")
            print(selections)
            t = 0
            for s in selections:
                # Iterate selections and add to tmp dictionary
                k = s.text.split(" (")[0]
                v = int(s.text.split(" (")[-1].strip(')'))
                tmp[k] = v
                t += v
            tmp["total"] = job_number
            print(tmp)
            # Close filter button
            f.click()
            time.sleep(2)
            jobs[f.text.strip()] = tmp
            tmp = {}
        print(jobs)
        return jobs        
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        # Close the browser
        driver.quit()

if __name__ == "__main__":
    locations = scrape_nvidia_job_locations()
    print(locations)