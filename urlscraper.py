from bs4 import BeautifulSoup
import time
import json
from contextlib import contextmanager
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import ElementNotVisibleException
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import StaleElementReferenceException

base_url = 'https://www.rottentomatoes.com'

#split into sections around ~2000 in side
browse_urls = ['https://www.rottentomatoes.com/browse/dvd-all/?maxTomato=10&services=amazon;amazon_prime;fandango_now;hbo_go;itunes;netflix_iw;vudu',
            'https://www.rottentomatoes.com/browse/dvd-all/?minTomato=11&maxTomato=20&services=amazon;amazon_prime;fandango_now;hbo_go;itunes;netflix_iw;vudu',
            'https://www.rottentomatoes.com/browse/dvd-all/?minTomato=21&maxTomato=30&services=amazon;amazon_prime;fandango_now;hbo_go;itunes;netflix_iw;vudu',
            'https://www.rottentomatoes.com/browse/dvd-all/?minTomato=31&maxTomato=40&services=amazon;amazon_prime;fandango_now;hbo_go;itunes;netflix_iw;vudu',
            'https://www.rottentomatoes.com/browse/dvd-all/?minTomato=41&maxTomato=50&services=amazon;amazon_prime;fandango_now;hbo_go;itunes;netflix_iw;vudu',
            'https://www.rottentomatoes.com/browse/dvd-all/?minTomato=51&maxTomato=60&services=amazon;amazon_prime;fandango_now;hbo_go;itunes;netflix_iw;vudu',
            'https://www.rottentomatoes.com/browse/dvd-all/?minTomato=61&maxTomato=70&services=amazon;amazon_prime;fandango_now;hbo_go;itunes;netflix_iw;vudu',
            'https://www.rottentomatoes.com/browse/dvd-all/?minTomato=71&maxTomato=80&services=amazon;amazon_prime;fandango_now;hbo_go;itunes;netflix_iw;vudu',
            'https://www.rottentomatoes.com/browse/dvd-all/?minTomato=81&maxTomato=85&services=amazon;amazon_prime;fandango_now;hbo_go;itunes;netflix_iw;vudu',
            'https://www.rottentomatoes.com/browse/dvd-all/?minTomato=86&maxTomato=90&services=amazon;amazon_prime;fandango_now;hbo_go;itunes;netflix_iw;vudu',
            'https://www.rottentomatoes.com/browse/dvd-all/?minTomato=91&maxTomato=95&services=amazon;amazon_prime;fandango_now;hbo_go;itunes;netflix_iw;vudu',
            'https://www.rottentomatoes.com/browse/dvd-all/?minTomato=96&services=amazon;amazon_prime;fandango_now;hbo_go;itunes;netflix_iw;vudu']

class text_to_be_not_present_in_element(object):
    """ An expectation for checking if the given text is present in the
    specified element.
    locator, text
    """
    def __init__(self, locator, text_):
        self.locator = locator
        self.text = text_

    def __call__(self, driver):
        try :
            element_text = EC._find_element(driver, self.locator).text
            return not(self.text in element_text)
        except StaleElementReferenceException:
            return False

def parse_movie_urls():
    '''Creates dictionary of all movies under Browse All of RT using div class = "mb-movie"
    	and storing it as {title:url}'''
    
    #create dict
    movie_list = {}

    for browse_url in browse_urls:


        #start selenium driver
        driver = webdriver.Firefox()
        driver.get(browse_url)
        
        soup = BeautifulSoup(driver.page_source,"lxml")
        show_count = soup.find('span',attrs={'id':'showing-count'}).text
        total_count = int(show_count.split(' ')[3])
        
        #clicking loop: keep expanding page till it is showing all movies
        elem = driver.find_element_by_xpath('//*[@id="show-more-btn"]/button')

        while(True):
            

            #check current count vs total count
            soup = BeautifulSoup(driver.page_source,"lxml")
            show_count = soup.find('span',attrs={'id':'showing-count'}).text

            print(show_count)

            current_count = int(show_count.split(' ')[1])

            #if it has finished clicking, break out of while loop
            if(current_count >= (total_count-1)):
                break

            else:
                #continue clicking
                try:
                    elem.click()
                    wait = WebDriverWait(driver, 90)
                    #wait until mb-movies is not stale
                    # elem = wait.until((float(driver.find_element_by_class_name('mb-movies').get_attribute("style").split('opacity: ')[1][0]) == 0.5))
                    # elem = wait.until((float(driver.find_element_by_class_name('mb-movies').get_attribute("style").split('opacity: ')[1][0]) == 1))
                    wait = wait.until(text_to_be_not_present_in_element((By.ID,'showing-count'),show_count))
                except ElementNotVisibleException:
                    break
                except TimeoutException:
                    break
        
        print('Scraping now')
        
        #record each movie title and its url inside dict
        soup = BeautifulSoup(driver.page_source,"lxml")
        movies = soup.find('div', {'class' :"mb-movies"})
        for movie in movies:
            url = movie.find('a',{'class' : "popoverTrigger"})['href']
            title = movie.find('h3',{'class' : "movieTitle"}).text

            movie_list[title] = url
        
        driver.quit()

    with open('movie_urls.txt','w') as file:
        json.dump(movie_list,file, indent=4)

    return movie_list
    


if __name__ == '__main__':
	#run scraper and print completion time
	print('Running')
	start = time.time()
	movie_urls = parse_movie_urls()
	end = time.time() - start
	print("Completed, time: " + str(end) + " secs")



