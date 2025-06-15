import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from pymongo import MongoClient
import time
import pandas as pd
import re

def persist_data(server = "mongodb://localhost:27017/", database = "nvjobs", collection = "jobs", data = None):
    client = MongoClient(server)
    
    # Test the connection
    try:
        client.server_info()
        print("Successfully connected to MongoDB!")
        db = client[database]
        c = db[collection]
        if data is not None:
            doc = {"timestamp": datetime.datetime.now(), "data": data}
            c.insert_one(doc)
            print("Data inserted successfully!")
            return True
        else:
            print("No data to insert")
            return False
    except Exception as e:
        print(f"Failed to connect to MongoDB: {e}")
        return False
    finally:
        client.close()

def scrape_nvidia_jobs():
    # Set up Chrome options
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--headless=new")  # Use new headless mode
    chrome_options.add_argument("--window-size=1920,1080")  # Set window size
    chrome_options.add_argument("--disable-gpu")  # Disable GPU hardware acceleration
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(options=chrome_options)

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
        #print(jobs)
        return jobs        
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        # Close the browser
        driver.quit()

if __name__ == "__main__":
    jobs = scrape_nvidia_jobs()
    persist_data(data = jobs)