
import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from pymongo import MongoClient
import time
import pandas as pd
import re
import json

def fangdi_scrp(project_id="d40383f20b61fd2a", id="024975", build_prefix="富业路199弄", data=None):
    #project_id = "d40383f20b61fd2a" => "旗忠悦园 富业路199弄"
    #id = "024975" => "闵行房管(2024)预字0000256号"
    # Set up Chrome options
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--headless=new")  # Use new headless mode
    chrome_options.add_argument("--window-size=1920,1080")  # Set window size
    chrome_options.add_argument("--disable-gpu")  # Disable GPU hardware acceleration
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(options=chrome_options)

    try:
        # Navigate to fangdi's job portal
        print("Navigating to fangdi.com.cn ...")
        driver.get("https://www.fangdi.com.cn/new_house/new_house_detail.html?project_id=" + project_id)
        
        # Wait for the page to load and job listings to appear
        wait = WebDriverWait(driver, 30)
        wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "li.today_region.f_left")))
        
        #TODO: Get sales infomration
        #TODO: Get 开盘单元
  
        #点击目标 开盘单元
        #click the target unit in 开盘单元 section
        units = driver.find_elements(By.CSS_SELECTOR, "li.today_region.f_left")
        print("********** 开盘单元 **********")
        print(units)
        
        for u in units:
            if id in u.text:
                print("********** " + id + " **********")
                print(u.text)
                u.click()
                break
        
        #Get 销售表
        sub_projects = driver.find_elements(By.CLASS_NAME, "sale_table_items")
        print("********** 销售表 **********")
        print(sub_projects)
        target_buildings = []
        for p in sub_projects:
            if build_prefix in p.text:
                print("********** " + p.text + " **********")
                #print(p.find_elements(By.CSS_SELECTOR, "div.sale_table_item.clearfix"))
                #print("********** " + " **********")
                target_buildings.extend(p.find_elements(By.CSS_SELECTOR, "div.sale_table_item.clearfix"))
        print("********** 目标销售表 **********" + " (" + str(len(target_buildings)) + ")")
        #print(target_buildings)

        #遍历目标销售表
        #traverse the target sales table
        d = {}
        for b in target_buildings:
            print("********** " + b.text.split("\n")[0] + " **********")
            bn = b.text.split("\n")[0].strip()
            b.find_element(By.CSS_SELECTOR, "a.f_left.text_ellipsis").click()
            # Give the page a moment to fully load
            time.sleep(2)
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "table.layui-table.colorfull_table")))
            # 遍历目标楼栋获取每户销售情况
            # 已签(yellow) 已登记(red) 可售(gree) 已付定金(purple-red?)
            # document.querySelectorAll("div > table") => get tables from https://www.fangdi.com.cn/new_house/more_info.html?project_id=d40383f20b61fd2a&building_id=d2b652455ed3c704e37369a0789568c2&start_id=41ef8f1e6b6741fc
            tables = driver.find_elements(By.CSS_SELECTOR, "table.layui-table.colorfull_table")
            print("********** tables **********")
            print(tables[0].text)

            i = 1
            u = {}
            bld = {"building_name": bn, "units": []}
            while i < len(tables):
                # 获取表格中的所有行,从第二行开始
                r = tables[i]
                print("********** " + r.text + " **********")
                # 获取表格中的所有单元格，从第二格子开始
                cells = r.find_elements(By.CSS_SELECTOR, "td")
                j = 1
                while j < 3:
                    print("********** " + cells[j].text + " **********")
                    print("********** " + str(cells[j].get_attribute("class")) + " **********")
                    u["unit_info"] = cells[j].text.strip()
                    u["status_class"] = cells[j].get_attribute("class").split(" ")[0]
                    match u["status_class"]:
                        case "_yellow_bg":
                            u["status"] = "已签"
                        case "_red_bg":
                            u["status"] = "已登记"
                        case "_green_bg":
                            u["status"] = "可售"
                        case _:
                            u["status"] = "未知"
                    print("********** unit is: " + " **********")
                    print(u)
                    bld["units"].append(u)
                    print("********** bld is: " + " **********")
                    print(bld)
                    u={}
                    j += 1
                i += 1
            data["buildings"].append(bld)
            driver.back()
            wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "li.today_region.f_left")))  
            # Give the page a moment to fully load
            time.sleep(2)
    finally:
        # Close the browser
        driver.quit() 

def persist_data(server = "mongodb://localhost:27017/", database = "realestate", collection = "fuye199", data = None):
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

if __name__ == "__main__":
    scraped_data = {
    "project_id": "d40383f20b61fd2a",
    "id": "024975", 
    "build_prefix": "富业路199弄",
    "buildings": []
    }
    fangdi_scrp(data=scraped_data)
    persist_data(data=scraped_data)
    print(scraped_data)

"""scraped_data = {
    "project_id": "d40383f20b61fd2a",
    "id": "024975", 
    "build_prefix": "富业路199弄",
    "buildings": [
        {
            "building_name": "富业路199弄1号",
            "units": [
                {
                    "unit_info": "101室",
                    "status_class": "green available",
                    "status": "可售"
                }
            ]
        }
    ]
    }"""