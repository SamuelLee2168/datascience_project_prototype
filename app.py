import pandas as pd
import numpy as np
import streamlit as st
import datetime
pro = ts.pro_api('6a180387b6b81a6226a45be784d0162d4676af26348e285396a50f78')

basic_stock_data = pd.read_csv("data/basic_stock_data.csv")

def find_stock_name_given_code(ts_code,basic_stock_data):
    return list(basic_stock_data['name'].loc[basic_stock_data['ts_code']==ts_code])[0]

def find_stock_code_given_name(name,basic_stock_data):
    return list(basic_stock_data['ts_code'].loc[basic_stock_data['name']==name])[0]

def is_ts_code(ts_code_or_name):
    return "." in ts_code_or_name

def get_stock_df_given_ts_code(ts_code):
    return pd.read_csv("data/"+ts_code+".csv")

def int_to_date(date_int):
    date_string = str(date_int)
    return datetime.date(int(date_string[0:4]), int(date_string[4:6]), int(date_string[6:8]))

def calculate_stock_rating_1_for_stock(stock_ts_code,time_start,time_end):
    stock_df = get_stock_df_given_ts_code(stock_ts_code).sort_values('trade_date').reset_index(drop=True)
    stock_close_list = list(stock_df['close'])
    
    stock_rating_1 = 0
    stock_df_in_time_span = stock_df.loc[stock_df['trade_date'] >= time_start]
    stock_df_in_time_span = stock_df_in_time_span.loc[stock_df_in_time_span['trade_date'] <= time_end]
    
    for t in np.arange(stock_df_in_time_span.index[0],stock_df_in_time_span.index[-1]):
        stock_rating_1 += abs((stock_close_list[t]-stock_close_list[t-1])/(stock_close_list[t-1]))
    stock_rating_1 /= stock_df_in_time_span.shape[0]
    return stock_rating_1

def calculate_stock_rating_2_for_stock(stock_ts_code,time_start,time_end):
    stock_df = get_stock_df_given_ts_code(stock_ts_code).sort_values('trade_date').reset_index(drop=True)
    stock_close_list = list(stock_df['close'])
    
    stock_rating_2 = 0
    stock_df_in_time_span = stock_df.loc[stock_df['trade_date'] >= time_start]
    stock_df_in_time_span = stock_df_in_time_span.loc[stock_df_in_time_span['trade_date'] <= time_end]
    
    for t in np.arange(stock_df_in_time_span.index[0],stock_df_in_time_span.index[-1]):
        stock_rating_2 += (stock_close_list[t]-stock_close_list[t-1])/(stock_close_list[t-1])
    stock_rating_2 /= stock_df_in_time_span.shape[0]
    return stock_rating_2

def calculate_stock_rating_3_for_stock(stock_ts_code,time_start,time_end):
    stock_df = get_stock_df_given_ts_code(stock_ts_code).sort_values('trade_date').reset_index(drop=True)
    stock_close_list = list(stock_df['close'])
    
    stock_rating_3 = 0
    stock_df_in_time_span = stock_df.loc[stock_df['trade_date'] >= time_start]
    stock_df_in_time_span = stock_df_in_time_span.loc[stock_df_in_time_span['trade_date'] <= time_end]
    
    for t in np.arange(stock_df_in_time_span.index[0],stock_df_in_time_span.index[-1]):
        if stock_close_list[t]>stock_close_list[t-1]:
            stock_rating_3 += abs((stock_close_list[t]-stock_close_list[t-1])/(stock_close_list[t-1]))
        else:
            stock_rating_3 += abs((stock_close_list[t]-stock_close_list[t-1])/(stock_close_list[t-1]))/2
    stock_rating_3 /= stock_df_in_time_span.shape[0]
    return stock_rating_3

def calculate_stock_rating_5_for_stock(stock_ts_code,time_start,time_end):
    stock_df = get_stock_df_given_ts_code(stock_ts_code).sort_values('trade_date').reset_index(drop=True)
    stock_close_list = list(stock_df['close'])
    stock_high_list = list(stock_df['high'])
    stock_low_list = list(stock_df['low'])
    
    stock_rating_5 = 0
    stock_df_in_time_span = stock_df.loc[stock_df['trade_date'] >= time_start]
    stock_df_in_time_span = stock_df_in_time_span.loc[stock_df_in_time_span['trade_date'] <= time_end]
    
    for t in np.arange(stock_df_in_time_span.index[0],stock_df_in_time_span.index[-1]):
        if len(stock_close_list[t-4:t+1])!=5:
            print(t-4,t+1)
        moving_average_5 = np.average(stock_close_list[t-4:t+1])
        stock_rating_5 += (stock_high_list[t]-stock_low_list[t])/moving_average_5
    stock_rating_5 /= stock_df_in_time_span.shape[0]
    return stock_rating_5

def rank_stocks_by_rating_function(stock_code_or_names,time_start,time_end,ranking_functions_dict,function_to_sort_by,basic_stock_data,bigger_is_better=True):
    stock_ts_codes = []
    stock_names = []
    stocks_out_of_time_range = []
    
    for stock_code_or_name in stock_code_or_names:
        if is_ts_code(stock_code_or_name):
            stock_ts_code = stock_code_or_name
            stock_name = find_stock_name_given_code(stock_code_or_name,basic_stock_data)
        else:
            stock_ts_code = find_stock_code_given_name(stock_code_or_name,basic_stock_data)
            stock_name = stock_code_or_name
        
        #If stock was listed before the input starting time, then we can calculate the stock's rating
        if int_to_date(int(basic_stock_data["list_date"][basic_stock_data['ts_code']==stock_ts_code]))<=int_to_date(time_start):
            stock_ts_codes.append(stock_ts_code)
            stock_names.append(stock_name)
        else:
            stocks_out_of_time_range.append(stock_name)
    
    ranking_function_results = {}
    for column_name in ranking_functions_dict.keys():
        ranking_function_results[column_name] = []

    #First iterate and collect results using dictionary, AND THEN convert to dataframe, since dataframe's are inefficient
    #to add values one row at a time
    for ts_code in stock_ts_codes:
        for column_name in ranking_functions_dict.keys():
            ranking_function_results[column_name].append(ranking_functions_dict[column_name](ts_code,time_start,time_end))
        
    rankings_df = pd.DataFrame({"股票代码":stock_ts_codes,"股票名字":stock_names})
    
    for column_name in ranking_function_results:
        rankings_df[column_name] = ranking_function_results[column_name]
    
    rankings_df = rankings_df.sort_values(function_to_sort_by,ascending=(not bigger_is_better))
    
    return rankings_df, stocks_out_of_time_range

ts_codes = st.text_input("以下可输入想要排序的股票名字或者股票TS码。多个股票之间用逗号分割。",value="平安银行,873223.BJ,万科A,000006.SZ").split(",")
start_time = int(st.text_input("强势系数开始计算的时间",value="20220915"))
end_time = int(st.text_input("强势系数结束计算的时间",value="20230323"))
ranking_functions = {"强势系数1":calculate_stock_rating_1_for_stock,"强势系数2":calculate_stock_rating_2_for_stock,"强势系数3":calculate_stock_rating_3_for_stock,"强势系数5":calculate_stock_rating_5_for_stock}
function_to_sort_by = "强势系数1"
df_to_display, stocks_out_of_time_range = rank_stocks_by_rating_function(ts_codes,start_time,end_time,ranking_functions,function_to_sort_by,basic_stock_data)
st.dataframe(df_to_display)
if len(stocks_out_of_time_range)>0:
    st.markdown("以下股票因时间段不符从而没有被放入强势系数的比较中:")
    st.markdown(stocks_out_of_time_range)
