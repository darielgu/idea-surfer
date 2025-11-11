import json
import time

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

def start_driver(headless: bool = False):
    """Start a ChromeDriver instance with stable options."""
    options = Options()
    if headless:
        options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--user-agent=Mozilla/5.0 ... Chrome/123.0.0.0 Safari/537.36")

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    driver.set_page_load_timeout(60)
    return driver

def daily_url(year: int, month: int, day: int) -> str:
    return f"https://www.producthunt.com/leaderboard/daily/{year:04d}/{month:02d}/{day:02d}"

def collect_product_urls(driver, timeout=30):
    #Wait for the list of product to load
    WebDriverWait(driver, timeout).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "main"))
    )

    links = driver.find_elements(By.CSS_SELECTOR, "a[href*='/products/']")
    seen = set()
    urls = []

    print("Getting links after sleep")
    time.sleep(2)


    for a in links:
        href = a.get_attribute("href")
        #Ensure there is an href to add to list
        if not href:
            continue
        if "/products/" in href and "#" not in href and href not in seen:
            seen.add(href)
            urls.append(href)

    time.sleep(2)
    
    print(urls)

    time.sleep(2)

    return urls

def scrape_external_url(driver, timeout=30):
    WebDriverWait(driver, timeout).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "main"))
    )

    links = driver.find_elements(By.TAG_NAME, "a")

    for a in links:
        href = a.get_attribute("href") or ""
        if "ref=producthunt" in href and "producthunt.com" not in href:
            return href
    
    return None

def get_launch_tags(driver, timeout=20):
    # make sure page is ready
    WebDriverWait(driver, timeout).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "main"))
    )

    #try to locate the “Launch tags:” container (two strategies)
    section = None
    #CSS first: some builds expose data attributes
    for sel in [
        "[data-test='launch-tags']",
        "section:has(> h2:contains('Launch tags'))",  # may not work in all drivers
    ]:
        try:
            section = driver.find_element(By.CSS_SELECTOR, sel)
            break
        except Exception:
            pass

    # if first doesn't worl try XPath fallback using the visible label text
    if section is None:
        try:
            section = driver.find_element(
                By.XPATH,
                "//*[@class and contains(., 'Launch tags')]"
            )
        except Exception:
            section = driver.find_element(By.CSS_SELECTOR, "main")  # very last resort

    #scroll into view so lazy content renders
    try:
        ActionChains(driver).move_to_element(section).perform()
    except Exception:
        driver.execute_script("arguments[0].scrollIntoView({block:'center'});", section)

    #grab topic links inside the section (and fallback to the whole page if needed)
    def _extract(container):
        anchors = container.find_elements(By.CSS_SELECTOR, "a[href*='/topics/']")
        tags = [a.text.strip() for a in anchors if a.text.strip()]
        return tags

    tags = _extract(section)
    if not tags:  # fallback if the section locator wasn’t precise
        tags = _extract(driver)

    # normalize data to return
    seen, normalized = set(), []
    for t in tags:
        clean = " ".join(t.split()).lower()
        if clean and clean not in seen:
            seen.add(clean)
            normalized.append(clean)
    return normalized



def scrape_link(driver, batch: str ,url: str, timeout = 30):

    projects = []
    source = "Product Hunt"

    #Get the page url and wait for page to load
    driver.get(url)

    WebDriverWait(driver, timeout).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "main"))
    )

    time.sleep(1)

    #Ensure the title loads before scrapping it
    title_el = WebDriverWait(driver, timeout).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "h1"))
    )

    short_el = WebDriverWait(driver, timeout).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "h2"))
    )

    #Extract the long description
    xpath = "//*[@id='root-container']/div[3]/div/main/div[1]/div[2]/div"
    try:
        long_el = WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((By.XPATH, xpath))
        )
    except Exception:
        print("Error extracting long description")


    title = title_el.text.strip()
    short_description = short_el.text.strip()
    long_description = long_el.text.strip()

    #Scrape external link of product
    external_link = scrape_external_url(driver)

    #Get the tags to append
    tags = get_launch_tags(driver)

    time.sleep(1)

    projects.append(
        Project(
            name = title,
            short_description=short_description,
            long_description=long_description,
            url = external_link,
            source = source,
            tags = tags,
            batch = batch,
        )
    )

    time.sleep(2)

    #print(projects)

    return projects






def run_scrape(driver, year: int, month: int, day:int):
    driver.get(daily_url(year, month, day))
    WebDriverWait(driver, 30).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "main"))
    )

    print("Loaded main page")

    time.sleep(10)

    urls = collect_product_urls(driver)

    time.sleep(2)

    batch = str(year) + str(month) + str(day)

    for u in urls:
        projects = scrape_link(driver, batch, u)

        #Upload every project to database
        print(f"Storing {len(projects)} projects from batch {batch} into DB.")
        store_in_db_yc(projects)


if __name__ == "__main__":
    year = 2025
    month = 11
    day = 10
    driver = start_driver()
    try:
        project_upload = run_scrape(driver, year, month, day)
    finally:
        driver.quit()