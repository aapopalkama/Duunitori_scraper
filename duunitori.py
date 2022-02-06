import pandas as pd
from bs4 import BeautifulSoup 
import requests
import re 
from pymongo import MongoClient



def main():
#   Connect to mongoDb
    client = MongoClient("mongodb+srv://palkaap:Nillaniemi123@cluster0.cslgm.mongodb.net/myFirstDatabase?retryWrites=true&w=majority")   
    db = client["Duunitori"]
    col = db["duunitori_1"]
    #   Duunitori url
    url = "https://duunitori.fi/tyopaikat/uusimaa?sivu=1"

    soup = BeautifulSoup(requests.get(url).content, "html.parser")
   
    pages = []
#   Parsing page wiht bs4 and examine how many pages there are in total
    for para in soup.find_all("a",{"class":"pagination__pagenum"}):
        pages.append(para.get_text())
#   Page numbers to list
    list_of_urls = []
#   We only need the last number
    n = (int(pages[-1])-1)
   
#   Let's build urls from which we retrieve information
    for i in range(1,n):
        url = "https://duunitori.fi/tyopaikat/uusimaa?sivu="
        url2 = str(i)
        list_of_urls.append(url+url2)

    length = len(list_of_urls) +1

    for url in list_of_urls[0:length]:
#       Parsing page wiht bs4
        soup = BeautifulSoup(requests.get(url).content, "html.parser")
        s  = soup.find("script",text=re.compile("impressions:")).text.split("[", 10)[2]
        
#       lets use Regular expression operations (re) to find data 
#       retrieve all data surrounded by "data"
        pattern = "'(.*?)'"
        sub = re.findall(pattern,s)
#       keys for dictionary/dataframe
        keys = ["id","name","category","brand","variant","list","position"]
        n=7
#       split the list to list of lists
        output=[sub[i:i + n] for i in range(0, len(sub), n)]
#       To pandas dataframe
        df = pd.DataFrame(output,columns = keys)

#       Data to mongoDb
        data_dict = df.to_dict("records")
        col.insert_many(data_dict)

if __name__ == "__main__":
    main()