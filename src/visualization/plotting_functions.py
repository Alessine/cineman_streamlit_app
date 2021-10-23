import pandas as pd
import plotly.graph_objects as go


def select_by_hour(df, hour="All"):
    if hour == "All":
        df = df
    elif hour == "9-12am":
        df = df[df["dt_showtime"].between('09:00:00', '12:00:00')]
    elif hour == "12-3pm":
        df = df[df["dt_showtime"].between('12:00:00', '15:00:00')]
    elif hour == "3-6pm":
        df = df[df["dt_showtime"].between('15:00:00', '18:00:00')]
    elif hour == "6-9pm":
        df = df[df["dt_showtime"].between('18:00:00', '21:00:00')]
    else:
        df = df[df["dt_showtime"].between('21:00:00', '23:59:00')]

    return df


def fetch_movie_desc(df, movie):
    if movie in list(df["original_title"]):
        overview = df[df["original_title"] == movie]["overview"].values[0]
        if pd.isnull(overview):
            overview = ""
        else:
            overview = f'<b>Movie Description:</b><br>{overview}'
    else:
        overview = ""
    return overview

# Plotly scattermapbox
def create_plotly_map(df, access_token, hour="All", movie="All"):
    df = select_by_hour(df, hour=hour)

    if movie == "All":
        df = df
    else:
        df = df[df["movie"] == movie]

    fig = go.Figure(go.Scattermapbox(
        lat=df["latitude"],
        lon=df["longitude"],
        mode='markers',
        marker=go.scattermapbox.Marker(
            size=10, color="crimson"
        ),
        text=df["cinema"],
        hoverinfo="text"
    ))

    fig.update_layout(
        hovermode='closest',
        width=500,
        height=500,
        margin={"r": 0, "t": 0, "l": 0, "b": 0},
        mapbox=dict(
            accesstoken=access_token,
            center=go.layout.mapbox.Center(
                lat=47.374,
                lon=8.535
            ),
            zoom=12.5,
            style="streets"
        )
    )
    return fig
