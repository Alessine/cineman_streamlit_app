import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import date

# Header and text
st.title("Movies in Zurich")

st.sidebar.header(f"{date.today()}")

st.sidebar.subheader("including movie ratings")

st.sidebar.write("scraped from www.cineman.ch")

cineman_df = pd.read_csv(f"./data/{date.today()}_showtimes_zurich.csv", index_col=0)

st.table(cineman_df.head())

left, right = st.columns([1, 1])

# Maps
# Basic
left.map(cineman_df)
right.bar_chart(cineman_df['showtime'].value_counts())

# With pydeck
import pydeck as pdk
from matplotlib import cm

color_list = cm.get_cmap('plasma', 24).colors*255

#cineman_df['plot_color'] = cineman_df['rating'].apply(lambda x: list(color_list[x]))
st.pydeck_chart(pdk.Deck(
     map_style='mapbox://styles/mapbox/light-v9',
     initial_view_state=pdk.ViewState(
         latitude=cineman_df["latitude"].mean(),
         longitude=cineman_df['longitude'].mean(),
         zoom=9,
         pitch=0,
     ),layers=[pdk.Layer(
             'ScatterplotLayer',
             data=cineman_df,
             get_position='[longitude, latitude]',
       #      get_color='plot_color',
           #  get_radius='[car_hours]/5',
         ),
     ]))

# Plotly will also render
#fig = dict({
#    "data": [{"type": "bar",
#              "x": [1, 2, 3],
#              "y": [1, 3, 2]}],
#    "layout": {"title": {"text": "A Figure Specified By Python Dictionary"}}
#})


#st.sidebar.write(name)

# Widgets
# selectBox

#option = st.sidebar.selectbox(
#    'Select Peak Hour',
#    sorted(pd.unique(df['peak_hour']))
#)
#st.sidebar.write(option)
# There are many more!!




