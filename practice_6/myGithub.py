from selenium import webdriver
from bs4 import BeautifulSoup
import os
import time
import csv

# 내 깃허브 레포지토리 정보(이름, 언어, 날짜)를 csv로 저장
class Github :
    def __init__(self) :
        self.myRepos_ = []
        self.path = os.getcwd() + "/chromedriver"
        self.driver = webdriver.Chrome(self.path)

    def writeCSV(self):
        file = open("github_myrepos.csv", "w", newline="")
        wr = csv.writer(file)
        wr.writerow(["Name", "Language", "Date"])

        for i in self.myRepos_ :
            wr.writerow([i[0], i[1], i[2]])
        file.close

    def run(self) :
        try :
            url = "https://github.com/qudwns2052?tab=repositories"

            while True :    
                self.driver.get(url)
                self.driver.implicitly_wait(10)
                html = self.driver.page_source    
                bs = BeautifulSoup(html, "html.parser")
                repos = bs.find_all("li", class_ = "col-12")

                for repo in repos :
                    name = (repo.find("h3", class_ = "wb-break-all").find("a")["href"].split("/")[-1])
                    lang = (repo.find("span", itemprop = "programmingLanguage").text)
                    date = (repo.find("relative-time").text)
                    self.myRepos_.append([name, lang, date])
                
                if(bs.find("button", class_ = "btn btn-outline BtnGroup-item") == None) :
                    break
                if(bs.find("button", class_ = "btn btn-outline BtnGroup-item").text == "Next") :
                    break
                else :
                    url = bs.find("a", class_ = "btn btn-outline BtnGroup-item")["href"]

            self.writeCSV()
    

        finally :
            self.driver.quit()


github = Github()
github.run()