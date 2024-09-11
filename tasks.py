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

def cauta_produs(page):
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
    return product_name


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

        #caut produsul
        product_name=cauta_produs(page)        

        try:
            # Selectam toate rezultatele cautarii
            page.wait_for_selector('div[data-testid="products-results"]')
            list_of_results = page.locator('div[data-testid="products-results"]')
            
            # Extragerea titlului produsului
            title_locator = list_of_results.locator('.ds-product-tile-name h2')
            title = title_locator.inner_text()

            # Afișarea titlului primului produs gasit
            print(f"Titlu: {title}")

            if title==product_name:
                print("produs disponibil în stoc")
                break
            else:
                print("product not found\nThe process will resume in 5 seconds")
                page.wait_for_timeout(5000)  # Wait for 5 seconds 
                page.reload

        except Exception as ex:
            print("product not found\nThe process will resume in 5 seconds")
            page.reload
           
           
# Perie de păr Stitch

    
def intra_in_cont(page):
    # Aștept ca elementul să fie vizibil și apoi fac hover pe el
    page.wait_for_selector('div.ds-dropdown-wrapper.ds-dropdown-mode-hover')
    page.hover('div.ds-dropdown-wrapper.ds-dropdown-mode-hover')

    # Aștept să fie disponibil butonul de login
    login_button_selector='a[data-testid="login"]'
    page.wait_for_selector(login_button_selector)
    page.click(login_button_selector)

    # Deschide fișierul JSON și citește conținutul
    with open('connect_info.json', 'r', encoding='utf-8') as file:
        data = json.load(file)  # Încărcăm conținutul fișierului într-un dicționar

    page.fill('input[name="login[username]"]', data.get("USERNAME"))  #  email-ul 
    page.fill('input[name="login[password]"]', data.get("PASSWORD"))  #  parola 

    # Apas pe butonul "Intră în cont"
    page.click('button[data-selen="login-submit"]')


def get_all_url_from_favorites(page,products_container):
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
    return url_list


@task
def my_task_3a_v2():

    # Navigate to Site
    page=browser.goto("https://www.sinsay.com/ro/ro/")
    
    # agree cookies
    page.click('button:has-text("OK")')

    #login
    intra_in_cont(page)

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
        
        #formam lista de url-uri
        url_list=get_all_url_from_favorites(page,products_container)

        #parcurgem lista intrand pe fiecare   
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
            

