import random
import time

import br as br
import gspread
from oauth2client.service_account import ServiceAccountCredentials

import wget
import os

scopes = [
    'https://www.googleapis.com/auth/spreadsheets.readonly',
    'https://www.googleapis.com/auth/drive'
]

#creds = ServiceAccountCredentials.from_json_keyfile_name("\\Users\\kantemirtemirkanov\\PycharmProjects\\WB_parser\\key.json", scopes=scopes)
creds = ServiceAccountCredentials.from_json_keyfile_name("/Users/kantemirtemirkanov/PycharmProjects/WB_parser/key.json", scopes= scopes )

file = gspread.authorize(creds)
work_book = file.open("WB_pars")
#constants
SYMB = " ABCDEFGHIJKLMNOPQRSTUVWXYZ"
ind_start = "C4"
ind_end = "F30"
count_of_sellers = 4
# sheet = work_book.sheet1
count = 0
lists = ["SiliCase", "Мандала", "Бабочка"]
try:
    for lst in lists:
        if (lst == "Мандала"):
            time.sleep(10)

        sheet = work_book.worksheet(lst)
    #print(sheet.range('C4:C10').value)


        k=0
        time_start = time.time()
        value = ""
        for cell in sheet.range(f'{ind_start}:{ind_end}'):
            count +=1
            end = time.time() - time_start

            if count > 60:
                count = 0
                time.sleep(60 - end % 60)
            k += 1
            string = str(cell)
            start_of_row = string.find("R") + 1
            end_of_row = string.find("C",2)
            start_of_col = string.find("C",2) + 1
            end_of_col = string.find("'") - 1
            # print(string)
            # print(SYMB[int(string[start_of_col:end_of_col])], end = "")
            # print(int(string[start_of_row:end_of_row]))
            # print()
            #[7] [9] первая отвечает за цифру вторая за букву
            # 1-А, 2-В

            p = wget.download(
                f'https://card.wb.ru/cards/detail?spp=31&regions=80,64,83,4,38,33,70,68,69,86,75,30,40,48,1,66,31,22,71&pricemarginCoeff=1.0&reg=1&appType=1&emp=0&locale=ru&lang=ru&curr=rub&couponsGeo=12,3,18,15,21&sppFixGeo=4&dest=-1029256,-102269,-2162196,-2162195&nm={cell.value}',
                f'wbs{k}.html')

            # wget.download()
            filename = f'wbs{k}.html'
            f = open(filename, 'r')
            result = f.read()
            os.remove(f"wbs{k}.html")
            # try:
            value = ""
            start_pos = result.find('"salePriceU":')
            end_pos = result.find(',"logisticsCost"')
            status = result.find('time1')
            if status < 1:
                 value = "Нет в наличии"
            if (len(result) == 79):
                value = "Артикула не существует"
            if (cell.value == ""):
                value = " "

            #print(result.find('time1'))
            if (value == ""):
                start_pos = result.index(":", start_pos, end_pos) + 1
            # except ValueError:
            #     continue
            # print(start_pos,"   ", end_pos)
            #print(cell.value, '   ', result[start_pos:end_pos - 2])
            # sheet.update_acell(f'{SYMB[int(string[start_of_col:end_of_col])],int(string[start_of_row:end_of_row])}', result[start_pos:end_pos - 2])
            # print(cell.value, value)
            if (value == "Нет в наличии") or (value == "Артикула не существует"):
                sheet.update_acell(f'{SYMB[int(string[start_of_col:end_of_col]) + count_of_sellers]}{int(string[start_of_row:end_of_row])}', value)
            else:
                sheet.update_acell(f'{SYMB[int(string[start_of_col:end_of_col])+count_of_sellers]}{int(string[start_of_row:end_of_row])}',
                               result[start_pos:end_pos - 2])
            #print(cell.value, len(result))
except gspread.exceptions.APIError:
    print("error 465")
    print(cell.value)
    time.sleep(10)


#print(sheet.acell("A5").value)
#print(sheet.row_values(3))
#print(sheet.col_values(3))

#update data

# sheet.update_acell('G4', 991)
#sheet.update_cell(4,7,992)
#prices = [[1],[2],[3],[4],[5],[6],[7]]
#sheet.update("G4:G10", prices)
#sheet.delete_row(7)
#print(sheet)

