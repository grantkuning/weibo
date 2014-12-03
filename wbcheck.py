from selenium import webdriver
import os
import time

'''
A little buggy for now. Also slow as hell, but that's not an immediate problem.
time.sleep(1) is a pretty clumsy little bit of code, but it seems to work fairly
well. One of the problems is that when you get a 404 on weibo.com, it will
automatically redirect you back to your homepage, so Selenium doesn't have all
day to check if it's at a 404. So far biggest bug I've found is that a page
can get stuck loading forever and never time out. Hopefully I'll get that
figured out soon. It doesn't seem to fail to recognize any 404s when it comes
across them though, which was my biggest fear.
'''

un = input('Enter username: ')
pw = input('Enter password: ')

browser = webdriver.Firefox()
browser.get('http://www.weibo.com/login')

username = browser.find_element_by_css_selector('.username > input:nth-child(1)')
password = browser.find_element_by_css_selector('.password > input:nth-child(1)')
username.clear()
username.send_keys(un)
password.clear()
password.send_keys(pw)
browser.find_element_by_css_selector('div.info_list:nth-child(6) > div:nth-child(1) > a:nth-child(1)').click()

browser.implicitly_wait(10)
time.sleep(3)

for (top, userdirs, userfiles) in os.walk('/Users/grantkuning/Documents/!save/'):
    for user in userdirs:
        for (usertop, tsdirs, tsfiles) in os.walk(top+user):
            for file in tsfiles:
                if file.endswith('.txt'):
                    with open(usertop+'/'+file) as f:
                        for line in f:
                            pass
                        url = line
                    browser.get(url)
                    time.sleep(1)
                    if browser.title == '404错误':
                        print(usertop+'/'+file)
                        print(url)
                        print()
browser.close()