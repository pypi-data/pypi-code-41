# coding:utf-8
from __future__ import print_function

import time
from selenium import webdriver
from selenium.common import exceptions


PAIRS_URL = 'https://pairs.lv'
LOGIN_URL = 'https://pairs.lv/#/login'
MAX_TRY = 100
INTERVAL_SEC = 0.2


def main():
    driver = open_driver()
    leave_footprints(driver)


def open_driver():
    driver = webdriver.Chrome()
    driver.get(PAIRS_URL)
    for i in range(0, MAX_TRY):
        if driver.current_url != PAIRS_URL:
            if driver.current_url == LOGIN_URL:
                input('ログインしてください')
        if driver.current_url == LOGIN_URL:
            continue
        return driver
    time.sleep(INTERVAL_SEC)

    raise exceptions.TimeoutException


def leave_footprints(driver):
    count = 1
    for page in counter():
        open_like_from_me(driver, page)

        try:
            persons = find_user_info(driver)
        except exceptions.TimeoutException:
            driver.quit()
            print('\n終了しました')
            quit(0)
            return count

        for person in persons[:-1]:
            open_person(person.find_element_by_tag_name('a'), count)
            count += 1
            close_person(driver)


def counter(start=1):
    count = start
    while True:
        yield count
        count += 1


def open_like_from_me(driver, page):
    list_url = 'https://pairs.lv/#/like/from_me/'
    driver.get(list_url + str(page))
    time.sleep(1)


def find_user_info(driver):
    for i in range(0, MAX_TRY):
        info = driver.find_elements_by_class_name('user_info')
        ignore_item = 2
        if len(info) <= ignore_item:
            time.sleep(INTERVAL_SEC)
        else:
            return info
    raise exceptions.TimeoutException


def open_person(person, count):
    for i in range(0, 30):
        try:
            person.click()
            print_leave_count(count)
            return
        except exceptions.WebDriverException:
            time.sleep(INTERVAL_SEC)
    raise exceptions.TimeoutException


def print_leave_count(count):
    progress_string = '\r現在{}人に足跡を付けました'
    print(progress_string.format(count), end='')


def close_person(driver):
    for i in range(0, MAX_TRY):
        try:
            close_button = driver.find_element_by_class_name('modal_close')
            close_button.click()
            return
        except (exceptions.ElementNotInteractableException,
                exceptions.ElementClickInterceptedException):
            time.sleep(INTERVAL_SEC)
    raise exceptions.TimeoutException


if __name__ == '__main__':
    main()
