from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
import os
import time

path = os.getcwd() + "/chromedriver"
driver = webdriver.Chrome(path)

try :
    driver.get("https://ticket.melon.com/main/index.htm")
    time.sleep(1)

    searchIndex = "뮤지컬"
    element = driver.find_element_by_class_name("placeholder")
    element.send_keys(searchIndex)
    driver.find_element_by_class_name("btn_comm").click()

    driver.find_element_by_xpath('//*[@id="conts"]/div/div/ul/li[1]/div/div[1]/div/a').click()
    time.sleep(1)


    html = driver.page_source
    bs = BeautifulSoup(html, "html.parser")

    pages = int(bs.find("em", class_= "link_page").text)
    print(pages)
    


    title = []
    page_count = 1
# range 수정
    while True :
        html = driver.page_source
        bs = BeautifulSoup(html, "html.parser")
        now_pages = bs.find_all("a", class_ = "link_page")
        print("현재 페이지 갯수 = ", (len(now_pages) + 1))

        for i in range(len(now_pages) + 1) :
            html = driver.page_source
            bs = BeautifulSoup(html, "html.parser")

            conts = bs.find("div", class_ = "box_movie tapping on").find_all("div", class_ = "show_infor")

            title.append("page" + str(page_count))
            page_count += 1
            for c in conts :
                title.append(c.find("p", class_ = "infor_text").find("span", class_ = "show_title").text)

#핵심 부분. 1 2 3 ... 10 > >> 전부 아래처럼 str(i+3)에 의해 눌림. i=0부터 시작하므로 첫번째 페이지 크롤링 하고 2 페이지로 넘어갈때 2페이지의 xpath
# 를 확인해보니 a[3]이였음. 즉, i=0에서 3을 더해야 2페이지로 넘어감
            
            if driver.find_element_by_xpath('//*[@id="drawPerformanceNavgation"]/div/a[' + str(i + 3) + ']') != None :
                driver.find_element_by_xpath('//*[@id="drawPerformanceNavgation"]/div/a[' + str(i + 3) + ']').click()
#만약 i==9면, 다음 페이지가 있을 것으로 예상함. 때문에 꺽새를 위에서 눌렀기 떄문에, while문에 의해 11 ~ 18페이지 개수를 now_pages에 저장하고 다시 돌림
#만약 i!=9면, (18페이지의 경우 i=8) while문 탈출
        if (i != 9) :
            break

finally :
    for t in title :
        if t.find("page") != -1 :
            print()
            print(t)
        else :
            print(t)

    driver.quit()