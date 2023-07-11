from enum import Enum

from selenium import webdriver
from selenium.common import NoSuchElementException, UnexpectedAlertPresentException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
import time
import sys

class CourtType(Enum):
    Indoor = "Indoor"
    Bubble = "Bubble"
    Outdoor = "Outdoor"


class Day(Enum):
    Mon = "Mon"
    Tue = "Tue"
    Wed = "Wed"
    Thu = "Thu"
    Fri = "Fri"
    Sat = "Sat"
    Sun = "Sun"


## parameters:
print("Let's get your credentials ready.. please make sure they are accurate!")
user_name = input("Please enter user name: ")
pass_word = input("Please enter password: ")
print("Thanks now let's get your desired schedule:")
desired_time_slot_map = {Day.Mon: input("Please enter time you want on Monday: "),
                         Day.Tue: input("Please enter time you want on Tuesday: "),
                         Day.Wed: input("Please enter time you want on Wednesday: "),
                         Day.Thu: input("Please enter time you want on Thursday: "),
                         Day.Fri: input("Please enter time you want on Friday: "),
                         Day.Sat: input("Please enter time you want on Saturday: "),
                         Day.Sun: input("Please enter time you want on Sunday: ")}
desired_court_type_string = input("Please preferred court type: Bubble, Indoor or Outdoor: ")
desired_court_type = CourtType(desired_court_type_string)

## mins
interval = int(input("Please enter request interval, min is 5 mins: "))
interval = min(interval, 5)

## constants
day_indent_map = {"Mon": 2, "Tue": 3, "Wed": 4, "Thu": 5, "Fri": 6,
                  "Sat": 7, "Sun": 8}

this_week_status = {"Mon": False, "Tue": False, "Wed": False, "Thu": False, "Fri": False,
                    "Sat": False, "Sun": False}

chrome_options = Options()
chrome_options.add_experimental_option("detach", True)
tennis_url = "https://efun.toronto.ca/torontofun/Activities/ActivitiesAdvSearch.asp?invocationLink=ALTLINK&SectionId=119&SubSectionId=229&BasicSearch=True"
driver = webdriver.Chrome(chrome_options)
## //*[@id="no-search-result-div"]

## TODO implement this
def check_if_next_week_is_available():
    return True


def login():
    driver.get("https://efun.toronto.ca/torontofun/MyAccount/MyAccountUserLogin.asp?Referrer=")
    try:
        login = driver.find_element(By.ID, "user-login")
        client_number_field = \
            login.find_element(By.TAG_NAME, "table").find_element(By.TAG_NAME, "tr").find_elements(By.TAG_NAME, "td")[
                1].find_element(By.TAG_NAME, "input")
        password_field = \
            login.find_element(By.TAG_NAME, "table").find_elements(By.TAG_NAME, "tr")[1].find_elements(By.TAG_NAME, "td")[
                1].find_element(By.TAG_NAME, "input")
        log_in_button = \
            login.find_element(By.TAG_NAME, "table").find_elements(By.TAG_NAME, "tr")[3].find_elements(By.TAG_NAME, "td")[
                0].find_element(By.TAG_NAME, "input")

        client_number_field.send_keys(user_name)
        password_field.send_keys(pass_word)
        log_in_button.click()
    except NoSuchElementException:
        print("already logged in")


def filter_on_day(day: str):
    clear_filter()
    day_check_box = driver.find_element(By.XPATH,
                                        "//*[@id='days-panel']/table/tbody/tr[2]/td[%i]/input" % day_indent_map[day])
    if not day_check_box.is_selected():
        day_check_box.click()


def unfilter_on_day(day: str):
    day_check_box = driver.find_element(By.XPATH,
                                        "//*[@id='days-panel']/table/tbody/tr[2]/td[%i]/input" % day_indent_map[day])
    if day_check_box.is_selected():
        day_check_box.click()


def filter_on_day_and_search(day: str):
    filter_on_day(day)
    time.sleep(2)
    search = driver.find_element(By.XPATH, "//*[@id='adv-search-buttons']/span[2]/span/input")
    search.click()


def clear_filter():
    unfilter_on_day(Day.Mon.value)
    unfilter_on_day(Day.Tue.value)
    unfilter_on_day(Day.Wed.value)
    unfilter_on_day(Day.Thu.value)
    unfilter_on_day(Day.Fri.value)
    unfilter_on_day(Day.Sat.value)
    unfilter_on_day(Day.Sun.value)


def filter_on_next_week():
    filter_on_day(Day.Mon.value)
    filter_on_day(Day.Tue.value)
    filter_on_day(Day.Wed.value)
    filter_on_day(Day.Thu.value)
    filter_on_day(Day.Fri.value)
    filter_on_day(Day.Sat.value)
    filter_on_day(Day.Sun.value)
    search = driver.find_element(By.XPATH, "//*[@id='adv-search-buttons']/span[2]/span/input")
    search.click()


## start search
## make sure user is on page that tennis is selected and detailed table is shown


## //*[@id="activity-1-20387"]/div[1]/span[1]/a
## search for current page and add if all parameters match
def try_add_to_cart(day: Day, desired_time_slot: str, desired_court_type: CourtType) -> bool:
    filter_on_day_and_search(day.value)
    time.sleep(4)
    try:
        driver.find_element(By.CLASS_NAME, "no-search-result-div")
        print("No such elements for", day.value)
        return False
    except NoSuchElementException:
        print("Searching results... for", day.value)
    drop_in_tennis = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, "//*[@id='activity-1-20387']/div[1]/span[1]/a")))
    drop_in_tennis.click()
    while True:
        current_index = 0
        for _ in driver.find_elements(By.XPATH, "//*[@id='activity-detail-table']/div/table/tbody/tr"):
            current_index += 1
            try:
                add_to_bucket_button = driver.find_element(By.XPATH,
                                                           "//*[@id='activity-detail-table']/div/table/tbody/tr[%s]/td[8]/div[2]/span/a" % current_index)
            except NoSuchElementException:
                continue
            day_text = driver.find_element(By.XPATH, "//*[@id='activity-detail-table']/div/table/tbody/tr[%s]/td[3]"
                                           % current_index)
            time_slot_text = driver.find_element(By.XPATH,
                                                 "//*[@id='activity-detail-table']/div/table/tbody/tr[%s]/td[4]"
                                                 % current_index)
            court_name_text = driver.find_element(
                By.XPATH,
                "//*[@id='activity-detail-table']/div/table/tbody/tr[%s]/td[6]/a" % current_index)

            if (day_text.accessible_name == day.value and
                    time_slot_text.accessible_name.startswith(desired_time_slot) and
                    desired_court_type.value in court_name_text.accessible_name and
                    add_to_bucket_button.accessible_name == "Add to Cart"):
                print(day_text.accessible_name, time_slot_text.accessible_name + " is available adding to basket", )
                add_to_bucket_button.click()
                time.sleep(4)
                select_candidate_name_and_add_to_cart_continue_shopping()
                this_week_status[day.value] = True
                return True
        next_button = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//*[@id='activity-detail-table']/div/div[2]/div[2]/a[3]")))
        if next_button.get_attribute('aria-hidden') != "true":
            next_button.click()
            time.sleep(4)
        else:
            return False


## //*[@id="activity-detail-table"]/div/div[2]/div[2]/a[3]
def select_candidate_name_and_add_to_cart_continue_shopping():
    try:
        Select(driver.find_element(By.XPATH,
                                   "//*[@id='Item0']/tbody/tr/td[1]/table/tbody/tr[1]/td[1]/div/span[2]/select")).select_by_index(
            1)
        time.sleep(2)
        ## cancel actually means continue shopping
        driver.find_element(By.XPATH, "//*[@id='cancel']").click()
    except UnexpectedAlertPresentException:
        time.sleep(4)
        driver.find_element(By.XPATH,
                            "/html/body/div[1]/div[2]/form/div[1]/div[1]/table[1]/tbody/tr/td[2]/span/input").click()
        time.sleep(2)
        driver.find_element(By.XPATH, "/html/body/div[1]/div[1]/a").click()


def main():
    ## first login
    login()

    ## check if next week is ready or not

    driver.get(tennis_url)

    for key in desired_time_slot_map:
        try_add_to_cart(key, desired_time_slot_map[key], CourtType.Bubble)

    driver.get("https://efun.toronto.ca/torontofun/MyBasket/MyBasketCheckout.asp")
    try:
        print("going to submit!")
        driver.find_element(By.XPATH, "//*[@id='completeTransactionButton']").click()
        time.sleep(4)
        driver.find_element(By.XPATH, "//*[@id='program-liability-waiver']/form/div[2]/span[1]/input").click()
        print("well done!")
        sys.exit()
    except NoSuchElementException:
        print("cart is empty, cannot do anything...")


if __name__ == "__main__":
    while True:
        main()
        time.sleep(interval * 60)
