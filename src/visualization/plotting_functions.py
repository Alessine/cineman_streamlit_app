import pandas as pd
import plotly.graph_objects as go


def select_by_hour(df, hour="All"):
    """
    This function takes in a string designating a time window and returns instances from a dataframe which fall
    within this time window.

    Required argument:
    - df: pandas dataframe, contains movie showtimes

    Optional argument:
    - hour: string, designates a time window; valid options are: "All", "9-12am", "12-3pm", "3-6pm", "6-9pm", "9-12pm".
    Defaults to "All".

    Returns:
    - df: pandas dataframe, the same as was fed into the function, but filtered to contain only those occurrences
    where the showtime is within the designated time window.
    """
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
    """
    This function takes in a dataframe with movie descriptions and a movie title.
    It returns the description for this movie or an empty string, if the description is not available.

    Required arguments:
    - df: pandas dataframe with movie titles and corresponding descriptions
    - movie: string, a movie title

    Returns:
    - overview: a string, the movie description corresponding to the movie title.
    """
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
def create_plotly_map(df, access_token_path, hour="All", movie="All"):
    """
    This function accepts a dataframe and three other arguments and returns a plotly map for Zurich.
    The longitude and latitude values in the dataframe are used to create a scatter plot.
    The hour and movie arguments serve as filters to display only specific showtimes or just one movie.

    Required arguments:
    - df: pandas dataframe, contains the data on movies and cinemas to be plotted.
    - access_token: a mapbox access token required for the customization of the map.
    - hour: string, designates a time window; valid options are: "All", "9-12am", "12-3pm", "3-6pm", "6-9pm", "9-12pm".
    Defaults to "All".
    - movie: string, a movie title

    Returns:
    - fig: plotly figure that can be used for plotting
    """
    df = select_by_hour(df, hour=hour)
    mapbox_access_token = open(access_token_path).read()

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
            accesstoken=mapbox_access_token,
            center=go.layout.mapbox.Center(
                lat=47.374,
                lon=8.535
            ),
            zoom=12.5,
            style="streets"
        )
    )
    return fig
