import requests
from bs4 import BeautifulSoup
import time
import pandas as pd

def information_extractor(url):
    info = {}
    response = requests.get(f"https://search.earth911.com/{url}")
    soup = BeautifulSoup(response.content, "html.parser")
    # Extract last verified date

    date_tag = soup.find("span", class_="last-verified")
    date = date_tag.text.strip().replace("Updated ","") if date_tag else "Date not found"

    name = soup.find("h1",class_ = "back-to noprint").text.strip(" ").replace("&#xFEFF"," ")
    name.replace(f"- {date}","")

    # Extract address elements 
    address_tags = soup.select("div p.addr")
    addresses = " ".join([tag.get_text(separator=' ', strip=True).replace("ï»¿"," ") for tag in address_tags])
    
    # Extract materials
    matrial = [li.text.strip(" ").replace("\ufeff"," ") for li in soup.find_all("span", class_="material no-link")]

    info["name"] = name
    info['date'] = date
    info['addresses'] = addresses
    info['matrial'] = matrial

    return info

def get_urls():
    urls = []
    currnt_page = 1
    while True:
        url = "https://search.earth911.com/?what=Electronics&where=10001&max_distance=25&country=US&province=NY&city=New+York&region=New+York&postal_code=10001&latitude=40.74807084035&longitude=-73.99234262099&sponsor=&list_filter=all&page={current_page}&sort=distance&sort_direction=asc&search_type=facility&search_type=event&search_type=dropoff&search_type=collection&search_type=retailer&search_type=manufacturer"
        response = requests.get(url)
        soup = BeautifulSoup(response.content, "html.parser")   
        # Find the next page linkpr
        links = soup.select(".title a[href]")
        urls += [link['href'] for link in links if link['href']]
        currnt_page += 1
        print(f"Current page: {currnt_page}, URLs found: {len(urls)}")
        if currnt_page == 21:
            break
    return urls    

def save_to_csv(data, filename="recycling_facilities.csv"):
    """
    Save the collected data to a CSV file.
    
    :param data: List of dictionaries containing facility information.
    :param filename: Name of the output CSV file.
    """
    df = pd.DataFrame(data)
    df.to_csv(filename, index=False)
    print(f"Data saved to {filename}")

if __name__ == "__main__":
    print("Initiating Earth911 recycling facility scraper...")
    urls = get_urls()
    print(f"Total URLs collected: {len(urls)}")
    all_data = []
    for i,url in enumerate(urls):
        print(f"Index: {i+1}/{len(urls)}")
        data = information_extractor(url)
        all_data.append(data)
        time.sleep(1) 
    # To avoid overwhelming the server
    print(f"Total data collected: {len(all_data)}")
    save_to_csv(all_data)
    print("Scraping process completed.")