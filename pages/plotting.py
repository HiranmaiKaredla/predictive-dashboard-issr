import streamlit as st
import numpy as np
from dashboard import alt_df
import plotly.express as px



altitude = st.selectbox('Pressure Altitude', list(range(30000, 44000, 500)))
h = st.selectbox('select hour', ["12", '00'])
alt_df = alt_df[(alt_df['Date'] >= "2024-01-01") & (alt_df['PRESS_ALT'] >=30000) & (alt_df['PRESS_ALT'] <= 44000)]
alt_df['PRESS_ALT'] = np.round(alt_df['PRESS_ALT'] / 500) * 500
alt_df = alt_df[['Date', 'Hour', 'PRESS_ALT','TEMP', 'RH_ice']].groupby(['Date', 'Hour', 'PRESS_ALT']).mean().reset_index()
#print(alt_df.head())
fig4 = px.line(alt_df[(alt_df['PRESS_ALT']==altitude) &(alt_df['Hour']==h)], x='Date', y="TEMP")
fig5 = px.line(alt_df[(alt_df['PRESS_ALT']==altitude) &(alt_df['Hour']==h)], x='Date', y="RH_ice")
st.plotly_chart(fig4)
st.plotly_chart(fig5)