from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
import time
import sys

# to call this script
# python3 fetch_links_with_selenium.py <page_number>
driver = webdriver.Firefox()
driver.get("https://www.bharatiyakritisampada.nic.in/advance-search")

try:
    # 542 seconds to display 100000 results
    nb_items_per_page = 10000
    page_number = sys.argv[1]

    WebDriverWait(driver, 60).until(
        EC.presence_of_element_located((By.ID, "pagelimit"))
    )

    select_items_per_page = driver.find_element_by_id("pagelimit")

    # hack:
    # set nb of items per page wanted in select option
    driver.execute_script(
        "arguments[0].options[0].text = '"
        + str(nb_items_per_page)
        + "'; "
        + "arguments[0].options[0].value = '"
        + str(nb_items_per_page)
        + "'",
        select_items_per_page,
    )

    select_items_per_page = Select(select_items_per_page)
    select_items_per_page.select_by_value(str(nb_items_per_page))

    search_button = driver.find_element_by_css_selector("span.ajax_search")
    search_button.click()

    start = time.time()

    # Wait for loader to be invisible
    WebDriverWait(driver, 7200).until(
        EC.invisibility_of_element((By.ID, "spinnerouter"))
    )

    end = time.time()
    print(str(end - start) + " seconds")

    if page_number != 1:
        # We select second pagination button and we change its id
        # to go directly to any page we want
        pagination_button_2 = driver.find_element_by_id("2")
        driver.execute_script(
            "arguments[0].id = '" + str(page_number) + "';",
            pagination_button_2,
        )
        pagination_button_2.click()

        WebDriverWait(driver, 7200).until(
            EC.invisibility_of_element((By.ID, "spinnerouter"))
        )

    links = driver.find_elements_by_xpath("//td//a[@href]")
    print("writing links in file links_page_" + str(page_number) + ".txt ...")
    with open("./links/links_page_" + str(page_number) + ".txt", "a") as f:
        for link in links:
            f.write(link.get_attribute("href") + "\n")
            # print(link.get_attribute("href"))


finally:
    driver.quit()
    print("end")
