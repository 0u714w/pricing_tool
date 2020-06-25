import requests
import argparse
from bs4 import BeautifulSoup, SoupStrainer
import sys
import re
import pandas as pd
import numpy as np
import getpass

def create_csv_sold(keyword):
    item_name = []
    prices = []
    average_price = []
    prices_stripped = []
    outliers = []
    url = "https://www.ebay.com/sch/i.html?_from=R40&_nkw={}&_in_kw=1&_ex_kw=&_sacat=0&LH_Sold=1&_udlo=&_udhi=&_samilow=&_samihi=&_sadis=15&_stpos=46201&_sargn=-1%26saslc%3D1&_salic=1&_sop=12&_dmd=1&_ipg=50&LH_Complete=1&_fosrp=1".format(keyword)
    res = requests.get(url)
    soup = BeautifulSoup(res.text.encode('utf-8').decode('ascii', 'ignore'), 'html.parser')
    listings = soup.find_all('li')
    for listing in listings:
        prod_name = " "
        prod_price = " "
        listing.encode('utf-8')
        for name in listing.find_all('a', attrs={'class': "vip"}):
            if(str(name.find(text=True, recursive=False)) != "None"):
                prod_name = str(name.find(text=True, recursive=False))
                item_name.append(prod_name)
            if(prod_name != " "):
                price = listing.find('span', attrs={'class': "bold bidsold"})
                price_to = listing.find('span', attrs={'class': "prRange"})
                prod_price = str(price.find(text=True, recursive=False))
                match = re.search(r'\b\$?[\d,.]+\b', str(prod_price))
                match_2 = re.search(r'\b\$?[\d,.]+\b', str(price_to))
                if match_2 == 'None':
                    pass
                elif match_2:
                    prices.append(str(match_2.group()))
                if match:
                    prices.append(str(match.group()))

    for i in prices:
        prices_stripped.append(int(float(i.replace('$', '').replace(',', '').replace('None', '0'))))

    for num in range(len(prices)):
        average_price.append(str(round(generate_average(prices), 2)))
        outliers.append(detect_outlier(prices_stripped))

    if len(average_price) < len(outliers):
        average_price.append(generate_average(prices_stripped))
    print(len(item_name), len(prices))
    username = getpass.getuser()
    a = {"Name": item_name, "Prices": prices, "Average Price": remove_outlier_from_average(outliers, average_price), "Outliers": outliers}
    chart = pd.DataFrame.from_dict(a, orient='columns')
    chart.transpose()
    chart.to_csv(r'/Users/{}/Desktop/{}-sold.csv'.format(username, '-'.join(keyword)), index=False)
    


def create_csv_active(keyword):
    item_name = []
    prices = []
    average_price = []
    prices_stripped = []
    outliers = []
    url = "https://www.ebay.com/sch/i.html?_from=R40&_trksid=p2380057.m570.l1311.R1.TR12.TRC2.A0.H0.X&_nkw={}&_sacat=0".format(keyword)
    res = requests.get(url)
    soup = BeautifulSoup(res.text.encode('utf-8').decode('ascii', 'ignore'), 'html.parser')
    listings = soup.find_all('li', attrs={'class': 's-item'})
    for listing in listings:
        prod_name = " "
        prod_price = " "
        for name in listing.find_all('h3', attrs={'class': "s-item__title"}):
            if(str(name.find(text=True, recursive=False)) != "None"):
                prod_name = str(name.find(text=True, recursive=False))
                item_name.append(prod_name)
            if(prod_name != " "):
                price = listing.find('span', attrs={'class': "s-item__price"})
                prod_price = str(price.find(text=True, recursive=False))
                prices.append(prod_price)

    for i in prices:
        prices_stripped.append(int(float(i.replace('$', '').replace(',', '').replace('None', '0'))))

    for num in range(len(prices)):
        average_price.append(str(round(generate_average(prices), 2)))
        outliers.append(detect_outlier(prices_stripped))

    if len(average_price) < len(outliers):
        average_price.append(generate_average(prices_stripped))

    username = getpass.getuser()
    a = {"Name": item_name, "Prices": prices, "Average Price": remove_outlier_from_average(outliers, average_price), "Outliers": outliers}
    chart = pd.DataFrame.from_dict(a, orient='columns')
    chart.transpose()
    chart.to_csv(r'/Users/{}/Desktop/{}-active.csv'.format(username, '-'.join(keyword)), index=False)

def generate_average(list_to_average):
    sum_num = 0
    for i in list_to_average:
        if i == 'None':
            i = 0
        else:
            sum_num = sum_num + int(float(i.replace('$', '').replace(',', '')))
    avg = sum_num / len(list_to_average)
    return avg


def detect_outlier(data_1):
    outliers_list = []
    threshold = 3
    mean_1 = np.mean(data_1)
    std_1 = np.std(data_1)
    
    for y in data_1:
        z_score = (y - mean_1) / std_1 
        if np.abs(z_score) > threshold:
            outliers_list.append(y)
    return outliers_list
    

def remove_outlier_from_average(outlier_list, average_list):
    for num in average_list:
        for i in outlier_list:
            if i == num:
                generate_average(average_list.remove(num))
                
    return average_list

        
def create_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('keyword', nargs="+", help='keyword to scrape')
    parser.add_argument('-s', '--sold', action='store_true', help='search for sold listings')
    parser.add_argument('-a', '--active', action='store_true', help='search for sold listings')
    return parser

def main(args):
    parser = create_parser()
    args = parser.parse_args(args)
    key = args.keyword
    
    if args.sold:
        return create_csv_sold(key)
    elif args.active:
        return create_csv_active(key)
    else:
        print(key)
    

if __name__ == '__main__':
    main(sys.argv[1:])