import requests
from bs4 import BeautifulSoup
import csv

import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5 import QtGui, uic

form_class = uic.loadUiType("indeed.ui")[0]

class Scraper(QObject) :

    updated = pyqtSignal(int)

    def __init__(self, textBrowser) :
        super().__init__()
        self.url = "https://kr.indeed.com/jobs?q=python&limit=50"
        self.textBrowser = textBrowser

    def getHTML(self, cnt) :
        res = requests.get(self.url + "&start=" + str(cnt * 50))

        if res.status_code != 200 :
            print("request error : ", res.status_code)

        html = res.text

        soup = BeautifulSoup(html, "html.parser")

        return soup
    
    def getPages(self, soup) :
        pages = soup.select(".pagination > a")

        return len(pages)

    def getCards(self, soup, cnt) :
        jobCards = soup.find_all("div", class_ = "jobsearch-SerpJobCard")

        jobID = []
        jobTitle = []
        jobLocation = []

        for j in jobCards :
            jobID.append("http://kr.indeed.com/viewjob?jk=" + j["data-jk"])

            jobTitle.append(j.find("a").text.replace("\n", ""))
            if j.find("div", class_ = "location") != None :
                jobLocation.append(j.find("div", class_ = "location").text)
            elif j.find("span", class_ = "location") != None :
                jobLocation.append(j.find("span", class_ = "location").text)

        self.writeCSV(jobID, jobTitle, jobLocation, cnt)

    def writeCSV(self, jobID, jobTitle, jobLocation, cnt) :
        file = open("indeed.csv", "a", newline="")

        wr = csv.writer(file)

        for i in range(len(jobID)) :
            wr.writerow([str((i + 1) + (cnt * 50)), jobID[i], jobTitle[i], jobLocation[i]])

        file.close()

    def run(self) :
        file = open("indeed.csv", "w", newline="")
        wr = csv.writer(file)
        wr.writerow(["No.", "Link", "Title", "Location"])
        
        file.close()

        soupPage = self.getHTML(0)
        pages = self.getPages(soupPage)

        for i in range(pages) :
            soupCard = self.getHTML(i)
            self.getCards(soupCard, i)
#            print(i, "번쨰 페이지 Done")
            self.textBrowser.append("%d번째 페이지 Done" % (i + 1))
            self.updated.emit(int(((i+1) / pages) * 100))

class WindowClass(QMainWindow, form_class) :
    def __init__(self) :
        super().__init__()
        self.setupUi(self)

        # 자신의 크롤러 class 가져오기
        self.crawler = Scraper(self.textBrowser)

        # Thread 적용하기
        self.thread = QThread()
        self.crawler.moveToThread(self.thread)
        self.thread.start()

        # 푸쉬 버튼과 자신의 크롤러 실행을 연결
        self.pushButton.clicked.connect(self.crawler.run)

        # set window title
        self.setWindowTitle("indeed crawler")

        # progressBar를 위한 시그널이 발생했을 때
        self.crawler.updated.connect(self.progressBarValue)
        self.progressBarValue(0)
 
    
    def progressBarValue(self, value) :
        self.progressBar.setValue(value)


 
if __name__ == '__main__' :

    app = QApplication(sys.argv) 
    myWindow = WindowClass() 
    myWindow.show()
    app.exec_()