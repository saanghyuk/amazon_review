import requests
from bs4 import BeautifulSoup
import pandas as pd
from urllib.parse import quote

# Input Search Query
SEARCH_QUERY = 'tv'

PROXY_CRAWL_TOKEN = 'JNsGFIUa5_amNHUfiLkHPA'
# PROXY_CRAWL_TOKEN = 'K-9nDJsiR1tb0vbXVAaSOQ'

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
    url = f"https://www.amazon.com{review_link}"
    return get_proxy(url)

### Product Name extraction

print("Start to extract product names")

product_names = []
data_asin = []
LAST_PAGE = 21
for i in range(1,LAST_PAGE):
    print(f"Iteration {i}/{LAST_PAGE}")
    html = search_in_amazon(SEARCH_QUERY+'&page='+str(i))
    soup = BeautifulSoup(html, 'html5lib')
    items = soup.findAll("span",{'class':'a-size-medium a-color-base a-text-normal'})
    if len(items) == 0:
        print(f"Warning: No product name found in this page")
    for i in items:
        product_names.append(i.text) # adding the product names to the list

    for i in soup.findAll("div", {"class":"s-result-item"}):
        if i['data-asin']:
            data_asin.append(i['data-asin'])

print(f"Finished: {len(product_names)} product names found")

'''
When scrawling the all pages of product list in specific search query, I could discover that there are same products in the list. <br>
Therefore, I needed to remove the same product in the list of ASIN.
'''

print("Start to search asin")

data_asin = list(set(data_asin)) # Leave unique values only

links = []
for i in range(len(data_asin)):
    print(f"Searching asin {i}/{len(data_asin)}")
    html = search_asin(data_asin[i])
    soup = BeautifulSoup(html, 'html5lib')
    for i in soup.findAll("a",{'data-hook':"see-all-reviews-link-foot"}):
        links.append(i['href'])

#     if soup.find("a",{'data-hook':"see-all-reviews-link-foot"}):
#         link.append(soup.find("a",{'data-hook':"see-all-reviews-link-foot"})['href'])
#         print("There is a button")
#     else:
#         print("There is no see all button")

links = list(set(links))
print(f"Finished: {len(links)} links found")
# The number of link and the number of ASIN can be different, because there are many products which have no review.

print("Start to search reviews")
# urls=[]
# titles = []
search_query_list = []
reviews = []
ratings=[]
# dates=[]

print("Start to search reviews")


for j in range(0, len(links)):

        target = links[j]
        print(f"Searching reviews: {j}/{len(links)}, target is {target}")
        for k in range(1, 50000):
            html = search_reviews(f"{target}&pageNumber={k}")
            soup = BeautifulSoup(html, 'html5lib')
            if soup.find(
                'div',
                {"class" : "a-section a-spacing-top-large a-text-center no-reviews-section"}
            ):
                print(f'Page {k}: No more reviews, step to next link')
                break
            else:
                items = soup.select('span[data-hook="review-body"] > span')
                ratings_in_page = soup.select('div.reviews-content span.a-icon-alt')
                prev_reviews_cnt = len(reviews)
                prev_ratings_cnt = len(ratings)

                for i in items:
                    if i.text == '':
                        # Ignore blank elements
                        continue
                    else:
                        reviews.append(i.text)
                        search_query_list.append(SEARCH_QUERY)
                        
                for l in ratings_in_page:
                    if l.text == '':
                        # Ignore blank elements
                        continue
                    else:
                        ratings.append(l.text)
                
                print(f"Page {k}: {len(ratings) - prev_ratings_cnt} ratings found")
                print(f"Page {k}: {len(reviews) - prev_reviews_cnt} reviews found")
                print("---------------------------")

print(f"Finished: {len(reviews)} reviews found")

print("Start to generate report")
# rev={'dates':dates, 'titles':titles, 'ratings':ratings, 'reviews':reviews, 'url':urls} #converting the reviews list into a dictionary

rev={'search_query':search_query_list, 'reviews' :reviews} #converting the reviews list into a dictionary
review_data=pd.DataFrame.from_dict(rev) #converting this dictionary into a dataframe

df = review_data.replace('\n','', regex=True)

writer = pd.ExcelWriter(SEARCH_QUERY+'_review.xlsx')
df.to_excel(writer, 'Sheet1', index=False)
writer.save()
print("Success")
