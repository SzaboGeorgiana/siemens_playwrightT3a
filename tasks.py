import os
from pathlib import Path

import requests
from robocorp import browser
from robocorp.tasks import task
from RPA.Excel.Files import Files as Excel
import json


FILE_NAME = "challenge.xlsx"
EXCEL_URL = f"https://rpachallenge.com/assets/downloadFiles/{FILE_NAME}"
OUTPUT_DIR = Path(os.getenv("ROBOT_ARTIFACTS", "output"))

@task
def my_task_3a_v1():

    # Navigate to Site
    page=browser.goto("https://www.sinsay.com/ro/ro/")
    
    # agree cookies
    page.click('button:has-text("OK")')
            
    # Așteaptă să fie disponibil butonul de căutare
    search_button_selector='button:has-text("Căutare")'
    page.wait_for_selector(search_button_selector)
    page.click(search_button_selector)

    while True:
        # Așteaptă să fie disponibil câmpul de căutare
        search_input_selector = 'input[name="query"]'  
        page.wait_for_selector(search_input_selector)

        # Deschide fișierul și citește conținutul
        with open('fisier.txt', 'r', encoding='utf-8') as file:
            product_name = file.read()

        print(product_name)
        # Completează câmpul de căutare
        page.fill(search_input_selector, product_name)
        page.press(search_input_selector,"Enter")

        try:
            # Căutăm denumirea produsului   
            page.wait_for_selector('div[data-testid="products-results"]')

            # Selectăm toate imaginile din div-ul cu rezultatele produselor
            list_of_results = page.locator('div[data-testid="products-results"]')
            
            # Extragerea titlului produsului
            title_locator = list_of_results.locator('.ds-product-tile-name h2')
            title = title_locator.inner_text()

            # Afișarea detaliilor produsului
            print(f"Titlu: {title}")
            if title==product_name:
                # click pe produs
                title_locator.click()
                # page.wait_for_timeout(1000000)  # Wait for 1000 seconds before closing the browser

                # verificare stoc
                stock_info = page.inner_text('span.titlestyled__StockInfo-sc-1obtcrd-2.ivCHmc > span:nth-child(1)')
                
                # Afișează textul extras
                print(stock_info)
                if "produs disponibil în stoc"==stock_info:
                    break
                else:
                    print("produs indisponibil\nThe process will resume in 5 seconds")
                    page.wait_for_timeout(5000)  # Wait for 5 seconds before closing the browser
                    page.reload
            else:
                print("product not found\nThe process will resume in 5 seconds")
                page.wait_for_timeout(5000)  # Wait for 5 seconds before closing the browser
                page.reload
        except Exception as ex:
            print("product not found\nThe process will resume in 5 seconds")
            page.reload
           
           
# Perie de păr Stitch

    
@task
def my_task_3a_v2():

    # Navigate to Site
    page=browser.goto("https://www.sinsay.com/ro/ro/")
    
    # agree cookies
    page.click('button:has-text("OK")')

    # Deschide fișierul JSON și citește conținutul
    with open('connect_info.json', 'r', encoding='utf-8') as file:
        data = json.load(file)  # Încărcăm conținutul fișierului într-un dicționar

    # Aștept ca elementul să fie vizibil și apoi fac hover pe el
    page.wait_for_selector('div.ds-dropdown-wrapper.ds-dropdown-mode-hover')
    page.hover('div.ds-dropdown-wrapper.ds-dropdown-mode-hover')

    # Aștept să fie disponibil butonul de login
    login_button_selector='a[data-testid="login"]'
    page.wait_for_selector(login_button_selector)
    page.click(login_button_selector)

    page.fill('input[name="login[username]"]', data.get("USERNAME"))  #  email-ul 
    page.fill('input[name="login[password]"]', data.get("PASSWORD"))  #  parola 

    # Apas pe butonul "Intră în cont"
    page.click('button[data-selen="login-submit"]')

    # Click pe x pentru oferta new sletter
    page.wait_for_selector('button.ds-button.ds-button__light.ds-button__icon')
    page.click('button.ds-button.ds-button__light.ds-button__icon.ds-button-size__l')

    #click pe favorite
    page.wait_for_selector('div[data-testid="header_heart"]')
    page.click('div[data-testid="header_heart"]')

    page.wait_for_selector('.products-container')
    products_container =  page.query_selector('.products-container')
    if products_container:
        print("Containerul de produse există.")
        
        # Obține toate produsele din container
        page.wait_for_selector('div[data-sku]')
        products =  products_container.query_selector_all('div[data-sku]')
        url_list=[]
        # Iterează prin fiecare produs și face click pe el
        for product in products:
            product.wait_for_selector('a')
            link =  product.query_selector('a')
            if link:
                # Extrage URL-ul produsului
                product_url =  link.get_attribute('href')
                url_list.append(product_url)
                
        for product_url in url_list:        
            print(f"Accesăm produsul: {product_url}")
            # Navighează la pagina produsului
            page.goto(product_url)
            page.wait_for_timeout(5000)  # Wait for 5 seconds

            if page.is_visible('div[data-testid="product-unavailable"]'):
                    print("product not in stock")
            else:
                    print("produs disponibil în stoc", product_url)
                    break    
                   
    else:
        print("Containerul de produse nu există.")
            




@task
def solve_challenge():
    """
    Main task which solves the RPA challenge!

    Downloads the source data Excel file and uses Playwright to fill the entries inside
    rpachallenge.com.
    """
    browser.configure(
        browser_engine="chromium", 
        screenshot="only-on-failure", 
        headless=True 
    )
    try:
        # Reads a table from an Excel file hosted online.
        excel_file = download_file(
            EXCEL_URL, target_dir=OUTPUT_DIR, target_filename=FILE_NAME
        )
        excel = Excel()
        excel.open_workbook(excel_file)
        rows = excel.read_worksheet_as_table("Sheet1", header=True)

        # Surf the automation challenge website and fill in information from the table
        #  extracted above.
        page = browser.goto("https://rpachallenge.com/")
        page.click("button:text('Start')")
        for row in rows:
            fill_and_submit_form(row, page=page)
        element = page.locator("css=div.congratulations")
        browser.screenshot(element)
    finally:
        # A place for teardown and cleanups. (Playwright handles browser closing)
        print("Automation finished!")


def download_file(url: str, *, target_dir: Path, target_filename: str) -> Path:
    """
    Downloads a file from the given URL into a custom folder & name.

    Args:
        url: The target URL from which we'll download the file.
        target_dir: The destination directory in which we'll place the file.
        target_filename: The local file name inside which the content gets saved.

    Returns:
        Path: A Path object pointing to the downloaded file.
    """
    # Obtain the content of the file hosted online.
    response = requests.get(url)
    response.raise_for_status()  # this will raise an exception if the request fails
    # Write the content of the request response to the target file.
    target_dir.mkdir(exist_ok=True)
    local_file = target_dir / target_filename
    local_file.write_bytes(response.content)
    return local_file


def fill_and_submit_form(row: dict, *, page: browser.Page):
    """
    Fills a single form with the information of a single row from the table.

    Args:
        row: One row from the generated table out of the input Excel file.
        page: The page object over which the browser interactions are done.
    """
    field_data_map = {
        "labelFirstName": "First Name",
        "labelLastName": "Last Name",
        "labelCompanyName": "Company Name",
        "labelRole": "Role in Company",
        "labelAddress": "Address",
        "labelEmail": "Email",
        "labelPhone": "Phone Number",
    }
    for field, key in field_data_map.items():
        page.fill(f"//input[@ng-reflect-name='{field}']", str(row[key]))
    page.click("input:text('Submit')")
