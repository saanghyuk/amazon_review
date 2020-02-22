import requests
from bs4 import BeautifulSoup
import pandas as pd
import time

# Input Search Query
search_query="tv"

base_url="https://www.amazon.com/s?k="

url=base_url+search_query

header={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36'}
search_response=requests.get(url,headers=header)

#### A function to get the content of the page of required query
cookie={} # insert request cookies within{}
def getAmazonSearch(search_query):
    url="https://www.amazon.com/s?k="+search_query
    print(url)
    page=requests.get(url,cookies=cookie,headers=header)
    if page.status_code==200:
        print("yes")
        return page
    else:
        print("No")
        return "Error"


#### A function to get the contents of individual product pages using 'data-asin' number (unique identification number)

def Searchasin(asin):
    url="https://www.amazon.com/dp/"+asin
    print(url)
    page=requests.get(url,cookies=cookie,headers=header)
    print(page)
    if page.status_code==200:
        return page
    else:
        return "Error"

#### A function to pass on the link of 'see all reviews' and extract the content
def Searchreviews(review_link):
    url="https://www.amazon.com"+review_link
    print(url)
    page=requests.get(url,cookies=cookie,headers=header)
    if page.status_code==200:
        return page
    else:
        return "Error"

### Product Name extraction
product_names=[]
data_asin = []


product_names=[]
data_asin = []
for i in range(1,21):
    response=getAmazonSearch(search_query+'&page='+str(i))
    time.sleep(1)
    soup=BeautifulSoup(response.content)
    print("hello")
    for i in soup.findAll("span",{'class':'a-size-medium a-color-base a-text-normal'}):
        print("hi")
        product_names.append(i.text) #adding the product names to the list

    for i in soup.findAll("div", {"class":"s-result-item"}):
        print("bye")
        if i['data-asin']:
            data_asin.append(i['data-asin'])

'''
When scrawling the all pages of product list in specific search query, I could discover that there are same products in the list. <br>
Therefore, I needed to remove the same product in the list of ASIN. 
'''

asin_list = list(dict.fromkeys(data_asin) )
data_asin = asin_list 

link=[]
for i in range(len(data_asin)):
    print(i)
    response=Searchasin(data_asin[i])
    soup=BeautifulSoup(response.content)
    time.sleep(1)
    for i in soup.findAll("a",{'data-hook':"see-all-reviews-link-foot"}):
        print(i['href'])
        link.append(i['href'])
    
#     if soup.find("a",{'data-hook':"see-all-reviews-link-foot"}):
#         link.append(soup.find("a",{'data-hook':"see-all-reviews-link-foot"})['href'])
#         print("There is a button")
#     else:
#         print("There is no see all button")

# The number of link and the number of ASIN can be different, because there are many products which have no review. 

# urls=[]
# titles = []
search_query_list = []
reviews=[]
# ratings=[]
# dates=[]

for j in range(len(link)):
    print(j, 'th started')
    for k in range(1, 2):
        response=Searchreviews(link[j]+'&pageNumber='+str(k))
        soup=BeautifulSoup(response.content)
        if soup.find('div', 
                     {"class" : "a-section a-spacing-top-large a-text-center no-reviews-section"}):
            print('No review, Pass')
            break
        
        else: 
            print('There is review')
#           for i in soup.findAll("span",{'data-hook':"review-body"}):
            for i in soup.findAll("span",{'data-hook':"a-size-base review-text review-text-content"}):
            
                reviews.append(i.text)
                search_query_list.append(search_query) 


# rev={'dates':dates, 'titles':titles, 'ratings':ratings, 'reviews':reviews, 'url':urls} #converting the reviews list into a dictionary

rev={'search_query':search_query_list, 'reviews' :reviews} #converting the reviews list into a dictionary
review_data=pd.DataFrame.from_dict(rev) #converting this dictionary into a dataframe

df = review_data.replace('\n','', regex=True)

writer= pd.ExcelWriter(search_query+'_review.xlsx')
df.to_excel(writer, 'Sheet1', index=False)
writer.save()
