import time
import wget
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os
from dotenv import load_dotenv
import requests
import logging
import re

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Загрузка переменных окружения
load_dotenv()

# Константы
SYMB = " ABCDEFGHIJKLMNOPQRSTUVWXYZ"
ind_start = "B3"

# Аутентификация и открытие Google Sheets
scopes = [
    'https://www.googleapis.com/auth/spreadsheets.readonly',
    'https://www.googleapis.com/auth/drive'
]
creds = ServiceAccountCredentials.from_json_keyfile_name("/root/WB/key.json", scopes=scopes)
file = gspread.authorize(creds)
work_book = file.open("WB_KAN")
sheet = work_book.sheet1

# Получение токена API Wildberries
wb_api_token = os.getenv('wb_api_token')

class WildberriesAPI:
    def __init__(self, api_token):
        self.api_token = api_token

    def fetch_wb_data(self, nm_id):
        url = f'https://card.wb.ru/cards/detail?spp=31&regions=80,64,83,4,38,33,70,68,69,86,75,30,40,48,1,66,31,22,71&pricemarginCoeff=1.0&reg=1&appType=1&emp=0&locale=ru&lang=ru&curr=rub&couponsGeo=12,3,18,15,21&sppFixGeo=4&dest=-1029256,-102269,-2162196,-2162195&nm={nm_id}'
        filename = wget.download(url, f'wbs.html')
        with open(filename, 'r') as f:
            result = f.read()
        os.remove(filename)
        return result

    def parse_wb_data(self, result):
        value = ""
        sale_price_pattern = re.compile(r'"salePriceU":\s*(\d+)')
        logistics_cost_pattern = re.compile(r',"logisticsCost"')
        time1_pattern = re.compile(r'time1')

        sale_price_match = sale_price_pattern.search(result)
        logistics_cost_match = logistics_cost_pattern.search(result)
        time1_match = time1_pattern.search(result)

        if time1_match:
            value = "Нет в наличии"
        elif len(result) == 79:
            value = "Артикула не существует"
        elif sale_price_match and logistics_cost_match:
            value = sale_price_match.group(1)

        return value

    def fetch_goods_data(self, filter_nm_id, limit=1):
        url = 'https://discounts-prices-api.wildberries.ru/api/v2/list/goods/filter'
        headers = {
            'Authorization': self.api_token
        }
        params = {
            'limit': limit,
            'filterNmID': filter_nm_id
        }
        res = requests.get(url, headers=headers, params=params)
        response_data = res.json()

        # Логирование ответа API
        logging.info(f"API Response: {response_data}")

        # Проверка на наличие ошибок
        if 'error' in response_data and response_data['error']:
            return None, f"Error: {response_data['errorText']}"

        # Проверка на наличие данных
        if 'data' not in response_data or 'listGoods' not in response_data['data']:
            return None, "Error: Invalid response structure"

        # Извлечение данных
        goods_list = response_data['data']['listGoods']
        extracted_data = []
        for goods in goods_list:
            nmID = goods['nmID']
            price = goods['sizes'][0]['price']
            discountedPrice = goods['sizes'][0]['discountedPrice']
            discount = goods['discount']
            extracted_data.append({
                'nmID': nmID,
                'price': price,
                'discountedPrice': discountedPrice,
                'discount': discount
            })

        return extracted_data, None

class GoogleSheetUpdater:
    def __init__(self, sheet):
        self.sheet = sheet

    def update_cells(self, row, data, value):
        self.sheet.update_acell(f'F{row}', value)
        self.sheet.update_acell(f'C{row}', data['price'])
        self.sheet.update_acell(f'D{row}', data['discountedPrice'])
        self.sheet.update_acell(f'E{row}', data['discount'])
        spp_value = self.spp_calc(data['discountedPrice'], int(value)) if value.isdigit() else -1
        self.sheet.update_acell(f'G{row}', spp_value)
        logging.info(f"Updated cells C{row}, D{row}, E{row}, F{row}, G{row} with values: {data['price']}, {data['discountedPrice']}, {data['discount']},{value}, {spp_value}")

    def spp_calc(self, price, discounted_price):
        return int((1 - discounted_price / price) * 100)

def main():
    count = 0
    api = WildberriesAPI(wb_api_token)
    updater = GoogleSheetUpdater(sheet)

    try:
        # Проверка наличия токена авторизации
        if not wb_api_token:
            logging.error("Error: WB API token is missing or invalid.")
            return

        column_values = sheet.col_values(2)  # Столбец B
        for i, nm_id in enumerate(column_values[2:], start=3):
            if nm_id == "":
                break 

            #данные о товаре
            data, error = api.fetch_goods_data(nm_id)
            if error:
                logging.error(error)
                continue

            # Записываем данные в Google Sheets
            for item in data:
                count += 5
                if count > 60:
                    count = 0
                    time.sleep(60)  # Пауза на 35 секунд, чтобы не превысить лимиты API
                result = api.fetch_wb_data(nm_id)
                value = api.parse_wb_data(result)
                updater.update_cells(i, item, value)
    except gspread.exceptions.APIError as e:
        logging.error(f"API Error: {e}")
        time.sleep(10)

if __name__ == "__main__":
    main()
