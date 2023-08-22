import json

from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import requests
import re


from data_file import DATA, URLS


def parse_addresses_with_coordinates(url):
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto(url)

        ''' Извлекаем элементы списка адресов '''
        address_elements = page.query_selector_all('.container.container--shops.addressList li')

        addresses = []
        latlons = []

        for element in address_elements:
            address = element.inner_text()
            latitude = element.get_attribute('data-latitude')
            longitude = element.get_attribute('data-longitude')

            addresses.append(address)
            latlons.append(f'{latitude}, {longitude}')

        browser.close()

    return addresses, latlons


def parse_data(url):
    res = requests.get(url)
    if res.status_code == 200:
        soup = BeautifulSoup(res.text, 'html.parser')

        data_list = []

        ''' вытягиваем имя сайта '''
        head_teg = str(soup.title)
        name_pattern = r'<title>[^>]+ - (.*?)</title>'
        name_match = re.search(name_pattern, head_teg)
        name_site = name_match.group(1)
        DATA["name"] = f'{name_site}'

        ''' вытягиваем номер телефона '''
        number = soup.find('div', class_='contacts__phone').find('a', class_='link link--black link--underline')
        phone_numbers = []
        for phone in number:
            phone_text = phone.get_text()
            phone_numbers.append(phone_text)
        DATA["phones"] = phone_numbers

        ''' вытягиваем адреса ресторанов по городам и их координаты '''
        current_address = soup.select_one('.city-select > a').text
        addresses, latlons = parse_addresses_with_coordinates(url)
        for address, latlon in zip(addresses, latlons):
            DATA["address"] = f'{current_address}, {address}'
            DATA["latlon"] = f'{latlon}'
            data_list.append(DATA.copy())

        ''' к сожалению, у меня не вышло вытянуть с этого сайта время работы без селениума '''

        return data_list

    else:
        print("Failed to access")


parse_list = (
        parse_data(URLS[0]) + parse_data(URLS[1]) + parse_data(URLS[2])
        + parse_data(URLS[3]) + parse_data(URLS[4]) + parse_data(URLS[5])
)


''' записываем даннные в json '''
with open('data_japonchik.txt', 'w') as json_file:
    json.dump(parse_list, json_file, ensure_ascii=False, indent=4)
