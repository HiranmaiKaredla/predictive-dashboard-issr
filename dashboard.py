import streamlit as st
import altair as alt
import pandas as pd
import numpy as np
from main import *
import plotly.express as px
import plotly.figure_factory as ff
import plotly.graph_objects as go
import matplotlib.pyplot as plt

st.set_page_config(
    page_title="Hello",
)

@st.cache_data
def setup():
    # df = pd.read_csv("data/all_stations_data.csv")
    # return df

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
alt_df = df
# df.to_csv("./data/all_stations_data.csv", na_rep= "NA",index=False)
# return 0

issr_df = df[(df['TEMP']<= -40) & (df['RH_ice'] >= 100)]
#fl_df = df[(issr_df['PRESS_ALT'] >=30000) & (df['PRESS_ALT'] <=43000) ]
fl_df = df
years = list(df['Year'].unique())
years.sort(reverse=True)
hours = ['00', '12']
# print(hours)
with st.sidebar:
    station = st.selectbox(
            "Select the station name",
            station_names,
        )


    year = st.selectbox(
            "Select the Year",
            years,
        )
    h = st.selectbox('select hour', hours)
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
# chart = alt.Chart(month_df_long, title = f"Monthly distribution of ISSR occurances in {year} in {station}").mark_bar().encode(
#         x=alt.X('Months:O', sort=months),
#         y= 'Days',
#         color = 'Value_Type',
#         #column = 'Value_Type',
#         tooltip=['Months', 'Value_Type', 'Days']
            
#     ).properties(
#     width=800,
#     height=400
# )

# st.altair_chart(chart)

fig = px.histogram(month_df_long, x="Months", y="Days",
             color='Value_Type', barmode='group',
             #histfunc='count',
             height=400, width=800)
st.plotly_chart(fig)

st_fl_df = fl_df[(fl_df['Station']==station) &  
(fl_df['TEMP']<= -40) & (fl_df['RH_ice'] >= 100) & (fl_df['PRESS_ALT'] >=30000) & 
(fl_df['PRESS_ALT'] <=43000) & (fl_df['Hour']==h) & (fl_df['Year']== year)]
st_fl_df['bins'] = pd.cut(st_fl_df['PRESS_ALT'], bins=range(30000, int(st_fl_df['PRESS_ALT'].max()) + 1000, 1000), right=False, labels= list(range(30000, int(st_fl_df['PRESS_ALT'].max()), 1000)))
result = st_fl_df.groupby('bins')['Date'].nunique().reset_index(name='days_count')
#print(result)



depth_df = st_fl_df.groupby(['Date', 'Hour']).agg({'PRESS_ALT': ['max', 'min']}).reset_index()
depth_df['diff'] = depth_df[('PRESS_ALT','max')] - depth_df[('PRESS_ALT','min')]
fig2 = px.histogram(depth_df[depth_df[('Hour', '')]== h], x="diff", nbins=24)



col01, col02 = st.columns(2)
chart_container1 = st.container()
tab1, tab2 = st.tabs(["ISSR days at FL30K - FL43K", "ISSR days with vertical depth"])

with tab1:
    st.bar_chart(result, x= "bins", y= "days_count", use_container_width=True)
    
with tab2:
    st.plotly_chart(fig2, use_container_width=True)
    #st.hist(depth_df[depth_df[('Hour', '')]== h], bins=24, color='skyblue', edgecolor='black')

#################



start_date = df['Date'].min()
end_date = df['Date'].max()

d= None

col1, col2 = st.columns(2)
with col1:
    d = st.date_input('pick a date',end_date, min_value=start_date, max_value=end_date)
with col2:
    pass
    #h = st.selectbox('select hour', hours)

chart_container2 = st.container()
col1, col2 = st.columns(2)
with chart_container2:

    if d:
        sample = fl_df[(fl_df['Station']== station) &(fl_df['Date']==pd.to_datetime(d))& (fl_df['Hour']==h) & (fl_df['PRESS_ALT'] <=43000)]
        with col1:
            #st.scatter_chart(sample, x="RH_ice", y="PRESS_ALT")
            base_chart = alt.Chart(sample).mark_circle().encode(
                x='RH_ice',
                y='PRESS_ALT'
            )
            
            vertical_line = alt.Chart(pd.DataFrame({'RH_ice': [100]})).mark_rule(color='red').encode(
                x='RH_ice:Q'
            )
            chart = (base_chart + vertical_line).properties(
                #title='Scatter Plot with Vertical Line'
            )

            st.altair_chart(chart, use_container_width=True)
        with col2:

            #st.scatter_chart(sample, x = "TEMP_F", y = "PRESS_ALT", color= "#ffaa00" )
            base_chart = alt.Chart(sample).mark_circle(size= 70,color='orange').encode(
                x='TEMP',
                y='PRESS_ALT',
                tooltip=['TEMP', 'PRESS_ALT']
            )
            
            vertical_line = alt.Chart(pd.DataFrame({'TEMP': [-40]})).mark_rule(color='red').encode(
                x='TEMP:Q'
            )
            chart = (base_chart + vertical_line).properties(
                #title='Scatter Plot with Vertical Line'
            )

            st.altair_chart(chart, use_container_width=True)


################################
#print(depth_df.columns)
vertical_depth = depth_df[depth_df[('Hour', '')]== h]
vertical_depth.rename(columns={('Date', ''): 'Date', ('Hour', ''): 'Hour', ('PRESS_ALT', 'min'): 'min', ('PRESS_ALT', 'max'): 'max', ('diff', ''): 'diff'}, inplace=True)

fig3, ax = plt.subplots(figsize=(10, 6))
for _, row in vertical_depth.iterrows(): 
    ax.plot([row[('Date', '')], row[('Date', '')]], [row[('PRESS_ALT', 'min')], row[('PRESS_ALT', 'max')]], color='blue')

ax.set_xlabel('Date')
ax.set_ylabel('Altitude')
ax.set_title('Min and Max Altitude for Each Date')
plt.xticks(rotation=45) 
plt.grid(True)
plt.tight_layout()
#plt.show()
#st.pyplot(plt.gcf())
st.pyplot(fig3)
######
#------------------------------------#

# vertical_depth = pd.DataFrame({
#     'Date': pd.date_range(start='2024-01-01', end='2024-01-10'),
#     'PRESS_ALT_min': [10, 15, 20, 25, 30, 35, 40, 45, 50, 55],
#     'PRESS_ALT_max': [20, 25, 30, 35, 40, 45, 50, 55, 60, 65]
# })

# # Convert DataFrame to long format suitable for Altair
# vertical_depth_long = vertical_depth.melt(id_vars='Date', var_name='PRESS_ALT', value_name='Altitude')

# # Create Altair chart
# chart = alt.Chart(vertical_depth_long).mark_rule(size=10).encode(
#     x='Date:T',
#     y='Altitude:Q',
#     color=alt.Color('PRESS_ALT:N', scale=alt.Scale(scheme='category10'))
# ).properties(
#     width=600,
#     height=400,
#     title='Min and Max Altitude for Each Date'
# ).configure_axis(
#     labelAngle=45
# )

# # Display the chart using Streamlit
# st.altair_chart(chart, use_container_width=True)

#-------------------#

