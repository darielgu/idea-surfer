import json
import time

from app.models.project import Project
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager


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

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    return driver


def scrape_batch(batch_name: str, limit: int = 10):
    """Scrape YC company list and individual company pages."""
    base_url = (
        f"https://www.ycombinator.com/companies?batch={batch_name.replace(' ', '%20')}"
    )
    print(f"\nScraping batch: {batch_name}")

    driver = start_driver(headless=False)
    driver.get(base_url)
    time.sleep(3)

    cards = driver.find_elements(By.CSS_SELECTOR, "a[class*='company_']")
    print(f"Found {len(cards)} companies in {batch_name}")

    projects = []

    # Go into card here
    for i, card in enumerate(cards[:limit], 1):
        href = card.get_attribute("href")

        try:  # try grabbing name
            name = card.find_element(
                By.CSS_SELECTOR, "span[class*='_coName']"
            ).text.strip()
        except Exception:
            print("Could not find company name element, using fallback.")
            name = card.text.strip().split("\n")[0]

        try:  # try grabbing location
            location = card.find_element(
                By.CSS_SELECTOR, "span[class*='_coLocation']"
            ).text.strip()
        except Exception:
            location = "Unknown"

        try:  # try grabbing short description
            short_desc_el = card.find_element(
                By.CSS_SELECTOR, "div.mb-1\\.5.text-sm span"
            )
            short_description = short_desc_el.text.strip()
        except Exception:
            short_description = ""

        try:  # try grabbing tags
            tag_elements = card.find_elements(
                By.CSS_SELECTOR, "div[class*='pillWrapper'] span[class*='pill']"
            )
            tags = [t.text.strip() for t in tag_elements if t.text.strip()]
        except Exception:
            tags = []

        # now go to the company page
        print(f"→ ({i}/{limit}) Visiting {name}")
        time.sleep(1)

        # open company in a new tab
        driver.execute_script(f"window.open('{href}', '_blank');")
        driver.switch_to.window(driver.window_handles[1])

        try:  # try grabbing long description
            desc_el = WebDriverWait(driver, 3).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, "div.prose.max-w-full.whitespace-pre-line")
                )
            )
            long_description = desc_el.text.strip()
            long_description = long_description.replace("\u2019", " ")
        except Exception:
            long_description = "No description found"
        info_rows = driver.find_elements(
            By.CSS_SELECTOR, "div.flex.flex-row.justify-between"
        )

        # init defaults
        founded = batch = team_size = status = primary_partner = None

        # try grabbing extra info
        for row in info_rows:
            try:
                label_el = row.find_element(By.CSS_SELECTOR, "span")
                label = (
                    label_el.text.strip().lower().rstrip(":")
                )  # e.g. 'founded', 'batch', etc.

                # value in either <span> or <a>
                try:
                    value_el = row.find_element(
                        By.CSS_SELECTOR, "span:not(:first-child), a"
                    )
                    value = value_el.text.strip()
                except Exception:
                    value = None

                # map into variables
                if "founded" in label:
                    founded = value
                elif "batch" in label:
                    batch = value
                elif "team size" in label:
                    team_size = value
                elif "status" in label:
                    status = value
                elif "primary partner" in label:
                    primary_partner = value

            except Exception:
                continue
        projects.append(
            Project(
                name=name,
                short_description=short_description,
                long_description=long_description,
                url=href,  # pyright: ignore[reportArgumentType]
                source="YC",
                tags=tags,
                location=location,
                founded=founded,
                batch=batch,
                team_size=team_size,
                status=status,
                primary_partner=primary_partner,
            )
        )

        # close tab and return to yc all companies page
        driver.close()
        driver.switch_to.window(driver.window_handles[0])
        time.sleep(1)

    # * save results -- TEMP
    output_path = f"yc_{batch_name.replace(' ', '_')}.json"
    with open(output_path, "w") as f:
        json.dump([p.model_dump(mode="json") for p in projects], f, indent=2)

    print(f"\nScraped {len(projects)} projects for {batch_name}")
    print(f"Saved to {output_path}")
    # * END OF -- TEMP : for now saving to json - in future embed each dict obj into DB

    print("=========================================")
    print(f"Projects: {projects}")

    driver.quit()


def run_scrape_yc(batches: list[str]):
    """Run YC scraper for predefined batches."""
    for b in batches:
        scrape_batch(b, limit=10)


if __name__ == "__main__":
    batches = ["Fall 2025"]
    for b in batches:
        scrape_batch(b, limit=10)
