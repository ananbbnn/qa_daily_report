import streamlit as st
import pandas as pd
from datetime import datetime
import plotly.graph_objects as go

st.title('QA')
members = ['ema.hong', 'Szi', 'weiren.yang', 'yuwei.dee', 
            'frank.huang', 'jiaying.cai', 'robin.wen', 
            'david.chen', 'jian.du','合計','待測試']

file = st.file_uploader('請上傳資料',['csv','xlsx','xls'])

report_date = st.sidebar.date_input('選擇日期')
if file:
    st.write(file.name)
    if file.name[-4:] == '.csv':
        df = pd.read_csv(file)
    if file.name[-5:] == '.xlsx':
        df = pd.read_excel(file)
  

    


    
    


    df['回報日期'] = pd.to_datetime(df['回報日期'], errors='coerce')
    df['已更新'] = pd.to_datetime(df['已更新'], errors='coerce')
    
    if report_date:
        report_date = datetime(
            report_date.year,
            report_date.month,
            report_date.day,
            0,
            0,
            0
        )
        today = pd.to_datetime('today').normalize()
        #st.dataframe(df['回報日期'])
    else:   
        today = pd.to_datetime(report_date, format='%Y%m%d')
    df = df.fillna('')
    # 各種統計
    fixed_keys = ['ema.hong', 'Szi', 'weiren.yang', 'yuwei.dee', 
        'frank.huang', 'jiaying.cai', 'robin.wen', 
        'david.chen', 'jian.du']
    people_results = {person: {} for person in fixed_keys}

    # 新問題
    new_issues = df[(df['狀態'] == '已分配') & (df['回報日期'] == report_date)]['分配給'].value_counts().to_dict()
    # 今日完成
    done_tested = df[(df['狀態'] == '已測試') & (df['已更新'] == report_date)]
    done_tested_count = done_tested['回報人'].value_counts().to_dict()
    done_assigned = df[(df['狀態'] == '待測試') & (df['已更新'] == report_date)]
    done_assigned_count = done_assigned['分配給'].value_counts().to_dict()
    combined_done = {**done_tested_count, **done_assigned_count}
    # 累積未完成
    cumulative_unfinished = df[df['狀態'] == '已分配']['分配給'].value_counts().to_dict()
    # 重要未處理
    important_unprocessed = df[(df['狀態'] == '已分配') & (df['嚴重性'] == '重要')]['分配給'].value_counts().to_dict()
    # 外部未處理
    external_unprocessed = df[(df['狀態'] == '已分配') & (df['類別'] == 'HAPCS疾管署_愛滋追管系統')]['分配給'].value_counts().to_dict()
    
    daily_results = {
        '新問題': new_issues,
        '今日完成': combined_done,
        '累積未完成': cumulative_unfinished,
        '重要未處理': important_unprocessed,
        '外部未處理': external_unprocessed
    }
    # 統計分類
    all_categories = list(daily_results.keys())
    # 補零
    for person in fixed_keys:
        for cat in all_categories:
            people_results[person][cat] = 0
    # 寫入統計
    for cat, data in daily_results.items():
        for person, count in data.items():
            if person in people_results:
                people_results[person][cat] = count
    # 合計
    people_results['合計'] = {}
    total_count = [sum(i.values()) for i in daily_results.values()]
    for i,key in  enumerate(daily_results.keys()):
        people_results['合計'][key] = total_count[i]
    # 待測試
    under_test = df['狀態'] == '待測試'
    under_test = int(under_test.sum())
    people_results['待測試'] = {'新問題':under_test}


    st.markdown(daily_results)
    
    select_col = st.sidebar.multiselect('請選擇',options=daily_results.keys())
    if select_col:
        fixed_daily_results = {}
        for i in select_col:
            fixed_daily_results[i] = daily_results[i]

        st.bar_chart(fixed_daily_results)
        
        
    
    
    