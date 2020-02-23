import requests
from bs4 import BeautifulSoup
import pandas as pd
from urllib.parse import quote

# Input Search Query
SEARCH_QUERY = 'tv'

PROXY_CRAWL_TOKEN = 'K-9nDJsiR1tb0vbXVAaSOQ'
def get_proxy(url):
    quoted_url = quote(url)
    res = requests.get(f'https://api.proxycrawl.com/?token={PROXY_CRAWL_TOKEN}&url={quoted_url}')
    res.raise_for_status() # Raise error if it fails
    return res.content

#### A function to get the content of the page of required query
def search_in_amazon(search_query):
    url = f"https://www.amazon.com/s?k={search_query}"
    return get_proxy(url)

#### A function to get the contents of individual product pages using 'data-asin' number (unique identification number)
def search_asin(asin):
    url = f"https://www.amazon.com/dp/{asin}"
    return get_proxy(url)

#### A function to pass on the link of 'see all reviews' and extract the content
def search_reviews(review_link):
    url = "https://www.amazon.com{review_link}"
    return get_proxy(url)

### Product Name extraction

print("Start to extract product names")

product_names = []
data_asin = []
LAST_PAGE = 21
for i in range(1,LAST_PAGE):
    print(f"Iteration {i}/{LAST_PAGE}")
    html = search_in_amazon(SEARCH_QUERY+'&page='+str(i))
    soup = BeautifulSoup(html)
    for i in soup.findAll("span",{'class':'a-size-medium a-color-base a-text-normal'}):
        product_names.append(i.text) # adding the product names to the list

    for i in soup.findAll("div", {"class":"s-result-item"}):
        if i['data-asin']:
            data_asin.append(i['data-asin'])

print("Finished extract product names")
print(product_names)

'''
When scrawling the all pages of product list in specific search query, I could discover that there are same products in the list. <br>
Therefore, I needed to remove the same product in the list of ASIN.
'''

asin_list = list(dict.fromkeys(data_asin) )
data_asin = asin_list

link=[]
for i in range(len(data_asin)):
    print(i)
    html = search_asin(data_asin[i])
    soup = BeautifulSoup(html)
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
        html = search_reviews(link[j]+'&pageNumber='+str(k))
        soup = BeautifulSoup(html)
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

writer= pd.ExcelWriter(SEARCH_QUERY+'_review.xlsx')
df.to_excel(writer, 'Sheet1', index=False)
writer.save()