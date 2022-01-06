"""
Script to retrieve book ids from list of books from goodreads export file

Input: 
    goodreads library export csv file. 
    export link https://www.goodreads.com/review/import
Output:
    txt file with list of book urls.
    For older books, this is the format of the original scraper style ('id.Book_Title')
    For newer books, sometimes the format is different ('id-book-title')
"""




# imports
import argparse
import bs4
import geckodriver_autoinstaller
import os 
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait

def setup_driver(headless=True):
    """
    """
    geckodriver_autoinstaller.install()
    fireFoxOptions = webdriver.FirefoxOptions()
    fireFoxOptions.headless = headless
    driver = webdriver.Firefox(options=fireFoxOptions)
    return driver

def extract_book_isbn(file_name:str,shelf:str='read') -> list:
    """
    Read raw goodreas file and extract list of isbn

    Parameters:
    Output: list of isbn
    """
    # read file 
    filedir = os.path.join(os.path.dirname(__file__),f'input_data/{file_name}')
    books_df = pd.read_csv(filedir)
    # filter out if shelf name is not empty
    if len(shelf) > 0 :
        books_df = books_df[books_df['Exclusive Shelf'] == shelf]
    # return ibans
    return books_df.ISBN13.values.tolist()

def scroll_shim(passed_in_driver, object):
        x = object.location['x']
        y = object.location['y']
        scroll_by_coord = 'window.scrollTo(%s,%s);' % (
            x,
            y
        )
        scroll_nav_out_of_way = 'window.scrollBy(0, -120);'
        passed_in_driver.execute_script(scroll_by_coord)
        passed_in_driver.execute_script(scroll_nav_out_of_way)

def open_url_from_isbn(driver,isbn:str,browser_url:str) -> None:
    """
    opens url from given isbn
    """
    # open url
    driver.get(browser_url)

    # scroll down to where element is visible
    search_box = driver.find_element(By.ID, 'sitesearch_field')
    if 'firefox' in driver.capabilities['browserName']:
        scroll_shim(driver, search_box)
    # initiate action chain 
    action = ActionChains(driver)
    # click on search bar
    action.move_to_element(search_box)
    action.click(search_box)
    # enter isbn
    action.send_keys(isbn)
    # press enter key
    action.send_keys(Keys.ENTER)
    # perform action
    action.pause(3)
    action.perform()

def rertrieve_current_url(driver) -> str:
    """
    returns current url
    """
    return driver.current_url
    
def main():
    search_url = "https://www.goodreads.com/"

    # parse arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('--book_list_file_name', type=str)
    parser.add_argument('--shelf_type', type=str, default='read')
    args = parser.parse_args()
    print(f"Retrieving ISBNs from file {args.book_list_file_name}")

    # get ISBN 13 number
    isbn_list = extract_book_isbn(file_name=args.book_list_file_name, shelf=args.shelf_type)

    # setup driver
    driver = setup_driver(headless=True)

    # get page url for each isbn
    print(f"Started retrieving url for {len(isbn_list)} books...")
    urls = []
    for isbn in isbn_list:
        open_url_from_isbn(driver,isbn=str(isbn),browser_url=search_url)
        url = rertrieve_current_url(driver)
        urls.append(url.split("show/")[-1])
        
    # close driver
    print(f"Successfully retrieved urls for {len(urls)} books.")
    driver.quit()
    
    # save file with list of url as txt file
    dirname = os.path.dirname(__file__)
    output_pathname = os.path.join(dirname,'input_data/goodreads_mybooks.txt')
    with open(output_pathname,'w') as f:
        for row in urls:
            f.write(row+"\n")
    print(f"Output saved in {output_pathname}")
    
if __name__ == '__main__':
    main()

