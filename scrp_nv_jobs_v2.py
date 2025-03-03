from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

# Set up the WebDriver (e.g., Chrome)
driver = webdriver.Chrome()

try:
    # Open the NVIDIA career site
    driver.get("https://nvidia.wd5.myworkdayjobs.com/NVIDIAExternalCareerSite")

    # Wait for the job listings to load
    WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.CLASS_NAME, "css-1q2dra3"))
    )

    # Scroll to load more jobs (if applicable)
    for _ in range(1):  # Adjust the range for more scrolling
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)  # Wait for new jobs to load

    locations = driver.find_elements(By.CLASS_NAME, "css-a4dzgn")
    print("location length: ", len(locations))
    for location in locations:
        print(location.text)
    TODO: extract job postings

    # Extract job postings
    #jobs = driver.find_elements(By.CLASS_NAME, "css-1q2dra3")
    #for job in jobs:
    #   title = job.find_element(By.CLASS_NAME, "css-a4dzgn").text
    #   location = job.find_element(By.CLASS_NAME, "css-1wh1oc8").text
    #   print(f"Title: {title}, Location: {location}")

finally:
    # Close the WebDriver
    driver.quit()
