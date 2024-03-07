import streamlit as st
import altair as alt
import pandas as pd
from main import *

@st.cache_data
def setup():
    df = pd.DataFrame(columns = ['Station', 'Date', 'Hour','LVLTYP1', 'LVLTYP2', 'ETIME', 'PRESS', 'PFLAG', 'GPH', 'ZFLAG', 'TEMP', 'TFLAG', 'RH', 'DPDP', 'WDIR', 'WSPD'])
    for station_name in station_names:
        temp_df = data_loading(station_name)
        temp_df['Station'] = station_name
        df = pd.concat([df,temp_df], ignore_index= True)
    df = preprocess(df)
    df = process_convention(df)
    df = add_new_features(df)
    return df

st.title("Dashboard for ISSR conditions")
df = setup()
issr_df = df[(df['TEMP']<= -40) & (df['RH_ice'] >= 100)]
#fl_df = df[(issr_df['PRESS_ALT'] >=30000) & (df['PRESS_ALT'] <=43000) ]
fl_df = df
station = st.selectbox(
        "Select the station name",
        station_names,
        #label_visibility=st.session_state.visibility,
        #disabled=st.session_state.disabled,
    )

years = df['Year'].unique()
year = st.selectbox(
        "Select the Year",
        years,
        #label_visibility=st.session_state.visibility,
        #disabled=st.session_state.disabled,
    )
months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
obs = []
orig = []
for i in range(1,13):
    obs.append(issr_df[(issr_df['Station']==station) & (issr_df['Year']==year) & (issr_df['Month'].astype(int) == i)]['Date'].nunique())
    orig.append(df[(df['Station']==station) & (df['Year']==year) & (df['Month'].astype(int)==i)]['Date'].nunique())
month_df = pd.DataFrame(columns = ['Months', 'No of Days', 'No of obs'])
month_df['Months'] = months
month_df['No of Days'] = orig
month_df['No of obs'] = obs
month_df_long = month_df.melt(id_vars='Months', var_name='Value_Type', value_name='Days')
#print(month_df_long)
#st.bar_chart(data = month_df, x='Months', y=['No of Days', 'No of obs'])
chart = alt.Chart(month_df_long, title = f"Monthly distribution of ISSR occurances in {year} in {station}").mark_bar().encode(
        x=alt.X('Months:O', sort=months),
        y= 'Days',
        color = 'Value_Type',
        tooltip=['Months', 'Value_Type', 'Days']
            
    ).properties(
    width=800,
    height=400
)

st.altair_chart(chart)

hours = df['Hour'].unique()
print(hours)


start_date = df['Date'].min()
end_date = df['Date'].max()

d= None
chart_container1 = st.container()
col1, col2 = st.columns(2)
with col1:
    d = st.date_input('pick a date',start_date, min_value=start_date, max_value=end_date)
with col2:
    h = st.selectbox('select hour', hours)

chart_container2 = st.container()
col1, col2 = st.columns(2)
with chart_container2:

    if d:
        sample = fl_df[(fl_df['Station']== station) &(fl_df['Date']==pd.to_datetime(d))& (fl_df['Hour']==h) & (fl_df['PRESS_ALT'] <=43000)]
        with col1:
            st.scatter_chart(sample, x="RH_ice", y="PRESS_ALT")
            base_chart = alt.Chart(sample).mark_point().encode(
                x='RH_ice',
                y='PRESS_ALT'
            )
            
            vertical_line = alt.Chart(pd.DataFrame({'RH_ice': [100]})).mark_rule(color='red').encode(
                x='RH_ice:Q'
            )
            chart = (base_chart + vertical_line).properties(
                title='Scatter Plot with Vertical Line'
            )

            st.altair_chart(chart, use_container_width=True)
        with col2:

            st.scatter_chart(sample, x = "TEMP_F", y = "PRESS_ALT", color= "#ffaa00" )
            base_chart = alt.Chart(sample).mark_point().encode(
                x='TEMP_F',
                y='PRESS_ALT'
            )
            
            vertical_line = alt.Chart(pd.DataFrame({'TEMP_F': [42]})).mark_rule(color='red').encode(
                x='TEMP_F:Q'
            )
            chart = (base_chart + vertical_line).properties(
                title='Scatter Plot with Vertical Line'
            )

            st.altair_chart(chart, use_container_width=True)


st_fl_df = fl_df[(fl_df['Station']==station) &  
(fl_df['TEMP']<= -40) & (fl_df['RH_ice'] >= 100) & (fl_df['PRESS_ALT'] >=30000) & 
(fl_df['PRESS_ALT'] <=43000) & (fl_df['Hour']==h) & (fl_df['Year']== year)]
st_fl_df['bins'] = pd.cut(st_fl_df['PRESS_ALT'], bins=range(30000, int(st_fl_df['PRESS_ALT'].max()) + 1000, 1000), right=False, labels= list(range(30000, int(st_fl_df['PRESS_ALT'].max()), 1000)))
result = st_fl_df.groupby('bins')['Date'].nunique().reset_index(name='days_count')
print(result)
st.bar_chart(result, x= "bins", y= "days_count")


