import streamlit as st
import pandas as pd
import plotly.graph_objects as go

st.title('練習')
st.sidebar.title('選單')

file = st.file_uploader('請上傳資料',['csv','xlsx','xls'])

fig = go.Figure(go.Indicator(
    mode = 'gauge+number',
    value = 450,
    title ={'text':'Speed'}
))

st.plotly_chart(fig)
if file:
    st.write(file.name)
    if file.name[-4:] == '.csv':
        df = pd.read_csv(file)
    if file.name[-5:] == '.xlsx':
        df = pd.read_excel(file)    

    st.dataframe(df)

    select_col = st.sidebar.selectbox('請選擇嚴重性',options=df['嚴重性'].unique().tolist())
    if select_col:
        filetred_df = df[df['嚴重性'] == select_col]
        count_df = filetred_df.groupby(by='回報日期').count().iloc[:,0]
        st.line_chart(data=count_df)