import requests
from bs4 import BeautifulSoup
import csv

# 1. 웹 사이트 접속
class Scraper() :
    def __init__(self):
        self.url = "https://kr.indeed.com/jobs?q=python&limit=50"

    def getHTML(self, cnt):
        res = requests.get(self.url + "&start=" + str(cnt * 50))
        print(res) #reponse 200 의미: 웹 페이지들은 각각 status code를 가지고 있음. 200번은 정상적으로 접근이 되었다는 의미. 
        if res.status_code != 200 :
            print("request error: ", res.status_code)  #오류 번호 출력
        html = res.text
        soup = BeautifulSoup(html, "html.parser")
        return soup


#2. 웹 사이트에서 html 받아오기 
# html = res.text

#3. 
# soup = BeautifulSoup(html, "html.parser")
# print(soup.prettify) #예쁘게 출력, 그래도 알기 어려움.
    def getPages(self, soup):
        pages = soup.select(".pagination > a") # .은 클래스 이름을 명시함
        return(len(pages)) #len()함수: 개수/길이 출력

    def getCards(self, soup, cnt):
        jobCards = soup.find_all("div", class_= "jobsearch-SerpJobCard")  #jobCards를 soup으로부터 전부 찾아준다

        jobID = []
        jobTitle = []
        jobLocation = []

        for j in jobCards :
            jobID.append("https://kr.indeed.com/viewjob?jk="+ j["data-jk"])
            jobTitle.append(j.find("a").text.replace("\n","")) #빈 배열에서는 값을 접근할 수 없음, append는 배열 마지막에 값 추가.
            if j.find("div", class_="location") != None :
                jobLocation.append(j.find("div", class_="location").text)
            elif j.find("span", class_="location") != None :
                jobLocation.append(j.find("span", class_="location").text)
        

        self.writeCSV(jobID, jobTitle, jobLocation, cnt)

    def writeCSV(self, jobID, jobTitle, jobLocation, cnt):
        file = open("indeed.csv", "a", newline="")

        wr = csv.writer(file)
        for i in range(len(jobID)) :
            wr.writerow([str(i + 1 + (cnt*50)), jobID[i], jobTitle[i], jobLocation[i]])
        file.close

    def scrap(self):
        soupPage = self.getHTML(0)
        pages = self.getPages(soupPage)

        file = open("indeed.csv", "w", newline="", encoding='UTF8') #scrap 호출이 되면 파이썬 파일이 한번 도니까, indeed.csv를 초기화시켜주면서..
        wr = csv.writer(file)
        wr.writerow(["No", "Link", "Title", "Location"])
        file.close

        for i in range(pages):
            soupCard = self.getHTML(i)
            self.getCards(soupCard, i)
            print(i, "번째 페이지 Done")

        
if __name__== "__main__" :
    s = Scraper()
    s.scrap()

#page 개수만큼 for 문을 돌려줘야함. 간단하게 하기 위해서 함수 형태로 제작. 