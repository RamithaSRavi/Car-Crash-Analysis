import streamlit as st
import pandas as pd 
import numpy as np
import pydeck as pdk 
import plotly.express as px
#pylint: disable=E1120

data_file = ('/Users/priya/Documents/carcrash/crashes.csv')
st.title('Motor Vehicle Collision in NYC')
st.markdown('This application is a Streamlit dashboard that can be used to analyze motor vehicle collision in NYC')

@st.cache(persist = True)
def load_data(rownum):
    data_df = pd.read_csv(data_file, nrows = rownum, parse_dates = {'CRASH_DATE_CRASH_TIME' : ['CRASH_DATE','CRASH_TIME']})
    data_df.dropna(subset = ['LATITUDE', 'LONGITUDE'], inplace = True)
    lowercase = lambda x : str(x).lower()
    data_df.rename(lowercase, axis = 'columns', inplace = True)
    data_df.rename(columns = {'crash_date_crash_time' : 'date/time'}, inplace = True)
    return data_df


data_df = load_data(100000)
original_data = data_df 

st.header('Where are the most people injured in NYC?')
injured_people = st.slider('Number of persons injured in vehicle collisions', 0, 19)
st.map(data_df.query('injured_persons >= @injured_people')[['latitude', 'longitude']].dropna(how = 'any'))

st.header('How many collisions occur during a given time of day?')
hour = st.slider('Hour to look at', 0, 23)
data_df = data_df[data_df['date/time'].dt.hour == hour]

st.markdown('Vehicle collisions between %i:00 and %i:00' % (hour, (hour+1) %24))
midpoint = (np.average(data_df['latitude']), np.average(data_df['longitude']))
st.write(pdk.Deck(
	map_style = 'mapbox://styles/mapbox/light-v9',
    initial_view_state = {
        'latitude' : midpoint[0],
        'longitude' : midpoint[1],
        'zoom' : 11,
        'pitch' : 50  
    },
    layers = [
        pdk.Layer(
        'HexagonLayer',
        data = data_df[['date/time', 'latitude', 'longitude']],
        get_position = ['longitude', 'latitude'],
        radius = 100,   
        extruded = True, #extruded makes the map 3D
        pickable = True, 
        elevation_scale = 4, 
        elevation_range = [0,1000]
        )
    ]
))

st.subheader('Breakdown by minute between %i:00 and %i:00' % (hour, (hour +1)))
filtered = data_df[
    (data_df['date/time'].dt.hour >= hour) & (data_df['date/time'].dt.hour < (hour +1))
]

hist = np.histogram(filtered['date/time'].dt.minute, bins = 60, range = (0,60))[0]
chart_data = pd.DataFrame({'minute' : range(60), 'crashes': hist})
fig = px.bar(chart_data, x='minute', y='crashes', hover_data=['minute', 'crashes'], height = 400)
st.write(fig)

st.header('Top 5 dangerous streets by affected type')
select = st.selectbox('Affected type of people', ['Pedestrians', 'Cyclists', 'Motorists'])

if select == 'Pedestrians':
    st.write(original_data.query('injured_pedestrians >= 1')[['on_street_name', 'injured_pedestrians']].sort_values(by = ['injured_pedestrians'], ascending = False).dropna(how = 'any')[:5])
elif select == 'Cyclists':
    st.write(original_data.query('injured_cyclists >= 1')[['on_street_name', 'injured_cyclists']].sort_values(by = ['injured_cyclists'], ascending = False).dropna(how = 'any')[:5])
else:
    st.write(original_data.query('injured_motorists >= 1')[['on_street_name', 'injured_motorists']].sort_values(by = ['injured_motorists'], ascending = False).dropna(how = 'any')[:5])



if(st.checkbox('Show Raw Data'), False):
    st.subheader('Raw Data')
    st.write(data_df)

