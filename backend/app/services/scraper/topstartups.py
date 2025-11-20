import json
import time
import random
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.action_chains import ActionChains
from app.models.project import ProjectYc as Project
from app.services.embedder.embedder import store_in_db_yc


def setup_driver(headless: bool = False) -> webdriver.Chrome:
    """Start a ChromeDriver instance with stable options."""
    options = Options()
    if headless:
        options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36")

    driver = webdriver.Chrome(options = options)
    driver.set_page_load_timeout(45)

    return driver

def period_sleep(a: float = 0.6, b: float = 1.2):
    """Sleep for a random period between a and b seconds."""
    time.sleep(random.uniform(a,b))

def scroll_to_bottom(driver: webdriver.Chrome):
    """Scroll to the bottom of the page to load all of the content."""
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2) #Waiting for new content
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

def show_more(driver: webdriver.Chrome):
    #Wait till "show more" appears and click it
    try:
        show_more = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located(
                (By.XPATH, "//*[@id='load-button']")
            )
        )
        show_more.click()
    except Exception as e:
        print(f"Error when trying to click show more at bottom of page: {e}")

def scrape_page(driver: webdriver.Chrome) -> list:
    card_wrapper = driver.find_elements(
        By.CSS_SELECTOR,
        "div.col-12.col-md-6.col-xl-4.infinite-item",
    )

    count = 0
    projects = []
    for wrap in card_wrapper:

        current_project = []

        card = wrap.find_element(By.CSS_SELECTOR, "div.card.card-body")
        #Extract the company name from the card
        company_name = card.find_element(By.CSS_SELECTOR, "h3 a#startup-website-link")

        #Extract the company link from the card
        company_link = company_name.get_attribute("href")

        #Extract the description of the company
        company_desc_el = card.find_element(By.CSS_SELECTOR, "p:has(#card-header)")
        #Extract the "what they do" part from the text
        company_desc = company_desc_el.text[13:].strip("\n")

        #Extract the tags from the card
        company_tags = []
        tag_elements = card.find_elements(
            By.CSS_SELECTOR, "span#industry-tags"
        )
        for tag in tag_elements:
            company_tags.append(tag.text)

        funding_tags = card.find_elements(
            By.CSS_SELECTOR, "span#funding-tags"
        )
        for tag in funding_tags:
            company_tags.append(tag.text)

        #Extract the team size from the card
        team_size = []
        facts_tags = card.find_elements(
            By.CSS_SELECTOR, "span#company-size-tags"
        )
        for tag in facts_tags:
            team_size.append(tag.text)

        #Extract the location of the company from the card
        company_location = ""

        company_el = card.find_element(
            By.CSS_SELECTOR, "#item-card-filter > p:nth-child(4)"
        )

        #Strip the location text to just be location
        line = company_el.text.split("\n")
        company_location = line[1]
        company_location = company_location[5:]

        #Strip the founded date
        company_founded = line[2]
        founded_arr = company_founded.split(" ")
        founded_date = founded_arr[3]
        print(founded_date)

        count += 1
        current_project.append(company_name.text)
        current_project.append(company_link)
        current_project.append(company_desc)
        current_project.append(company_tags)
        current_project.append(team_size[0])
        #print(current_project)
        #projects.append(current_project)

        projects.append(
            Project(
                name = company_name.text,
                short_description=company_desc,
                url = company_link,
                source = "Topstartups",
                tags = company_tags,
                location = company_location,
                founded = founded_date,
                team_size = team_size[0]
            )
        )

        print(projects)

    print("Listed items", count)
    period_sleep()

    return projects


def load_page(driver: webdriver.Chrome, url: str):
    driver.get(url)
    period_sleep()

    #Scroll to the bottom and click the "show more button"
    scroll_to_bottom(driver)
    period_sleep()
    show_more(driver)
    period_sleep()

    #Repeatidly scroll to the bottom till all page content has loaded
    scroll_to_bottom(driver)
    period_sleep()

    return None

def main() -> None:
    try:
        #Load all of elements on the page
        driver = setup_driver(headless=False)
        load_page(driver, url="https://topstartups.io/")

        #Extract all the elements from page
        projects = scrape_page(driver)
        store_in_db_yc(projects)

        print(f"Storing {len(projects)} projects into DB.")

    except Exception as e:
        print("Error in main when scrapping: ", e)

if __name__ == "__main__":
    main()