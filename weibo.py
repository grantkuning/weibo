from selenium.common import exceptions
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from datetime import datetime
from textwrap import wrap
import os
import time as t
import urllib.request

'''
General documentation:
    This program automatically logs into my weibo account and scrapes my feed. I have designated a folder
in my computer to store all files scraped in this way, which is /Users/grantkuning/Documents/!save/. In
the future, I would like to make this path customizable. The program sorts the posts into folders by
username, and then by the time they were posted. The posts are then saved in these folders as plain text.
As an example, one such file has the path .../!save/temp/新华网/2014-12-01 08/36/36/ByMhZsLAX.txt. 新华网
("Xinhuanet", online branch of China's state press agency) is the username, and it was posted at 8:36:36
on December 1st, 2014. Note that OS X does not support colons in folder names; they are converted to
slashes automatically. These slashes do not indicate separate folders; "2014-12-01 08/36/36" is one folder.
    The file name comes from the ID of the post. The direct link to the post is
http://www.weibo.com/2810373291/ByMhZsLAX. The number that precedes the post ID, 2810373291, is the ID of
the poster. Going to http://www.weibo.com/2810373291 redirects to Xinhuanet's main page, which is at
http://www.weibo.com/newsxh. A direct link to each post is copied to each text file, along with the name
of the poster and the timestamp.
    If the post has images attached, these will also be saved to the folder of the corresponding
timestamp. weibo.com displays only one image attachment at full size, while the rest are shown as
thumbnails. Rather than locating each thumbnail, clicking on it, and then downloading the full-size
image as it appears, the program identifies the url for each thumbnail and then derives the url of the
full-size image from that. This is possible because the difference between the urls is simple, and
consistent. Continuing with the same example, the url for the thumbnail of the first image of the post
is http://ww3.sinaimg.cn/square/a782e4abjw1emtvrrgvbaj20c80gatat.jpg, while the full-size image is at
http://ww3.sinaimg.cn/bmiddle/a782e4abjw1emtvrrgvbaj20c80gatat.jpg. As such, it's simply a matter of
changing "square" to "bmiddle" in each url. This will also be necessary occasionally even if only one
image is attached.
    The Chinese word weibo (微博) means "microblog" or "microblogging." As such, it could refer to posts,
an account, or the name of the most popular Chinese microblogging platform by far, Sina Weibo, now known
simply as Weibo, hosted at weibo.com. In this program, the term "weibo" will refer to the main text of a
post. In some cases, "wb" will be used as an abbreviation.
    This program uses the variable time0 to identify the most recent post it has scraped. This is stored
in the UNIX time format in log.txt. When reviewing my feed on weibo.com, this program will ignore posts
older than time0. Note: log.txt does not store UNIX times per se. Rather than UTC, it is adapted to
UTC+8:00, which is China Standard Time. See below.
    Note on times: All Chinese-speaking countries use UTC + 8, and none observe daylight savings. Thus,
by grabbing the UNIX timestamp from the website and adding eight hours in seconds, you will always
correctly render the local (Chinese) time the post was made, accurate to the second. Although weibo.com
includes digits in its timestamps for milliseconds, these last three digits are always zeros. As such,
I cancel them out by dividing by 1000. Also note that there is a "time" attribute, but it is not accurate
to the second, and occasionally a poster will post twice in one minute, in which case two posts would
have the same timestamp. Using UNIX time avoids this problem.
'''

rt_photos = []                      # Used for distinguishing between "retweeted" photos, and new ones.
time0 = 0
with open('/Users/grantkuning/Documents/!save/log.txt') as log:
    for line in log:
        pass
    time0 = int(line.split()[0])

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

def embiggen(url):                              # Converts thumbnail url to full-size.
    p = url.split('/')
    p[3] = 'bmiddle'
    return('/'.join(p))

def imgscrape(path):
    t.sleep(3)
    if len(browser.find_elements_by_css_selector('img[action-data^="pic_id="]')) > 1:
        for photo in browser.find_elements_by_css_selector('img[action-data^="pic_id="]'):
            p = photo.get_attribute('src')
            p = embiggen(p)
            urllib.request.urlretrieve(p, path + p.split('/')[len(p.split('/'))-1])
            rt_photos.append(p)
    elif len(browser.find_elements_by_css_selector('.bigcursor img')) == 1:
        p = browser.find_element_by_css_selector('.bigcursor img').get_attribute('src')
        if 'bmiddle' not in p:
            p = embiggen(p)
        urllib.request.urlretrieve(p, path + p.split('/')[len(p.split('/'))-1])
        rt_photos.append(p)

def scrape(link, dir = ''):
    browser.find_element_by_tag_name('body').send_keys(Keys.COMMAND + 't')      # New tab
    browser.get(link)
    time = browser.find_element_by_css_selector('.S_txt2 a[href*="profile"]')
    timestamp = str(datetime.utcfromtimestamp((int(time.get_attribute('date'))/1000)+28800))
    weibo = browser.find_element_by_css_selector('.WB_text.W_f14').text
    user = browser.title.split('的')[0]          # Chinese lesson: 的 is equivalent to 's.
                                                # e.g. "Grant的微博" = "Grant's weibo [account]."
    if dir:
        path = '/Users/grantkuning/Documents/!save/temp/'+dir+'/'+timestamp+'/'
    else:
        path = '/Users/grantkuning/Documents/!save/temp/'+user+'/'+timestamp+'/'

    filename = path + link.split('/')[4] + '.txt'
    os.makedirs(path)
    with open(filename, 'w') as f:
        f.write('@'+user+' ['+timestamp+']'+'\n')
        for line in wrap(weibo, 40):
            f.write(line+'\n')
        f.write(link)

    if len(browser.find_elements_by_css_selector('.S_txt2 a[date]')) > 1:       # Checks if posts quotes another.
        href = browser.find_elements_by_css_selector('.S_txt2 a[date]')[0].get_attribute('href')
        scrape(href, user+'/'+timestamp)                                        # If so, scrape the quoted post.
    else:
        imgscrape(path)
    imgscrape(path)         # Posts which quote posts that have images attached sometimes have images of their own.
            # In this case, it is necessary to scrape for images twice, to discern which images go with which post.
    try:
        browser.find_element_by_tag_name('body').send_keys(Keys.COMMAND + 'w')      # Close tab
    except exceptions.StaleElementReferenceException:
        browser.find_element_by_tag_name('body').send_keys(Keys.COMMAND + 'w')      # In case it doesn't close.
                                                                                    # Works better than you'd think.
while True:
    for id in browser.find_elements_by_css_selector('.S_txt2 a[href*="?ref=home"]'):
        utime = (int(id.get_attribute('date'))/1000)+28800
        if utime > time0:
            scrape(id.get_attribute('href').split('?')[0])

    addtime = browser.find_element_by_css_selector('.S_txt2 a[href*="?ref=home"]')
    time0 = (int(addtime.get_attribute('date'))/1000)+28800
    with open('/Users/grantkuning/Documents/!save/log.txt', 'a') as log:
        log.write('\n'+str(int(time0))+' ['+str(datetime.utcfromtimestamp(time0))+']')
    print('Folder updated. Chinese time:', str(datetime.utcfromtimestamp(time0)))

    if browser.title != '我的首页 微博-随时随地发现新鲜事':         # Checks if the browser is looking at the home page.
        browser.find_element_by_tag_name('body').send_keys(Keys.COMMAND + 'w')      # If not, close tab.

    wait = True
    waitcount = 0
    while wait:
        if len(browser.find_elements_by_css_selector('.WB_notes')) > 0 or waitcount > 60:
            wait = False                            # WB_notes is the class name of the "new posts" notification.
            browser.refresh()
        else:
            t.sleep(5)
            waitcount += 1