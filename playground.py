from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

option = webdriver.ChromeOptions()
option.add_argument(argument="--incognito")

browser = webdriver.Chrome(executable_path=r"C:\git\projects\SM-bot\chromedriver_win32\chromedriver.exe",
                           options=option)

browser.get("https://github.com/svandegar")

# wait 20 secs for page to load
timeout = 20

try:
    WebDriverWait(browser,timeout).until(
        EC.visibility_of_element_located((By.XPATH,
                                          # wait till the image is loaded as this is the last thing to be loaded
                                          "//img[@class='avatar width-full rounded-2']")))
except TimeoutException:
    print("Timed out waiting for page to load")
    browser.quit()

# find_elements_by_xpath returns an array of selenium objects.
titles_element = browser.find_elements_by_xpath("//a[@class='text-bold']")

# use list comprehension to get the actual repo titles and not the selenium objects
titles = [x.text for x in titles_element]

# print out all the titles
print('titles:')
print(titles,'\n')

language_element = browser.find_element_by_xpath("//p[@class='mb-0f6 text-gray']")

# use list comprehension to get the actual repo languages and not the selenium objects
languages = [x.text for x in language_element]

print("languages:")
print(languages,"\n")

for title, language in zip(titles,languages):
    print("RepoName : Language")
    print(title+ ": " + language,"/n")