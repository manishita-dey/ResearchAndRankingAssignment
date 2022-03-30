import requests
import pandas
from openpyxl.workbook import Workbook


def extract_close_price(start_date: str, end_date: str, email_mode : bool):
    # Extracting Nifty50 fincodes
    response_nifty = requests.get("https://api.informedinvestorr.com/assignment/python/niftyList")
    nifty_fincode_lst = response_nifty.json()['fincode_list']

    #Extracting closing stock price on start_date
    param_start = {
        'selected_date' : {start_date}
    }
    response_start = requests.get(url = "https://api.informedinvestorr.com/assignment/python/dailyPrices", params = param_start)
    start_date_data = pandas.DataFrame(response_start.json()['data_list'])
    # Extracting only those stocks present in nifty50
    start_data_nifty = start_date_data[start_date_data.fincode.isin(nifty_fincode_lst)]

    #Extracting closing stock price on end_date
    param_end = {
        'selected_date': {end_date}
    }
    response_end = requests.get(url = "https://api.informedinvestorr.com/assignment/python/dailyPrices", params = param_end)
    end_date_data = pandas.DataFrame(response_end.json()['data_list'])
    # Extracting only those stocks present in nifty50
    end_data_nifty = end_date_data[end_date_data.fincode.isin(nifty_fincode_lst)]

    # Merging both dataframes on symbol and fincode(Inner Join)
    merged_df = pandas.merge(
        start_data_nifty,
        end_data_nifty,
        how = 'inner',
        on = ('fincode','symbol'), left_on=None,
        right_on=None,
        left_index=False,
        right_index=False,
        sort=True,
        suffixes=("_start", "_end"),
        copy=True,
        indicator=False,
        validate=None,
    )
    # Adding a new column to our merged dataframe to calculate stock performance
    merged_df["performance"] = round(((merged_df["close_end"] - merged_df["close_start"]) / merged_df['close_start']) * 100, 2).astype(str) + '%'

    # Returning data according to email_mode
    if email_mode == "True":
        return merged_df.to_excel("result_1.xlsx")
    else:
        result_df = merged_df.swapaxes('index', 'columns')
        result_dict = result_df.to_dict()
        result_lst = [result_dict[key] for key in result_dict]
        return result_lst


# print(extract_close_price('2022-01-09', '2022-01-29', True))
# print(extract_close_price('2022-01-09', '2022-01-29', False))
# Input statements
start_date = str(input("The start date to calculate(YYYY-MM-DD)"))
end_date = str(input("The end date to calculate (YYYY-MM-DD)"))
email = bool(input("True/False"))

print(extract_close_price(start_date, end_date, email))



