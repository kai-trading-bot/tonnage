import numpy as np
import pandas as pd
import ipywidgets as widgets
import plotly.offline as py
import plotly.graph_objs as go

py.init_notebook_mode(connected=True)

__author__ = 'kqureshi'

DATA_PATH = '/Users/kq/Downloads/DSNY_Monthly_Tonnage_Data.csv'


def fetch_data() -> pd.DataFrame:
    """
    Fetch and process data
    """
    data = pd.read_csv(DATA_PATH).drop('BOROUGH_ID', axis=1)
    data['YEAR'] = data.MONTH.str.split(' / ').str[0]
    data['MONTH'] = data.MONTH.str.split(' / ').str[1]
    data = data.groupby(['YEAR', 'BOROUGH']).sum().reset_index()
    data.YEAR = data.YEAR.astype(str)
    return data


def update_plot(slider_year: int) -> py.iplot:
    """
    Use slider to query for year and create diagram
    """
    data = fetch_data()
    df = data.query('YEAR=="{year}"'.format(year=slider_year)).set_index('BOROUGH').drop('YEAR', axis=1)
    links = []
    for borough in list(df.index):
        for target in df.loc[borough].reset_index().values:
            links.append({'source': borough, 'target': target[0], 'value': target[1]})

    df = pd.DataFrame(links)
    nodes = np.unique(df[["source", "target"]], axis=None)
    nodes = pd.Series(index=nodes, data=range(len(nodes)))
    fig = go.Figure(
        go.Sankey(
            node={"label": nodes.index},
            link={
                "source": nodes.loc[df["source"]],
                "target": nodes.loc[df["target"]],
                "value": df["value"],
            },
        )
    )
    fig.update_layout(title=dict(text="{year} Collection Distribution".format(year=slider_year), font=dict(size=25)))
    py.iplot(fig, filename='HISTORICAL COLLECTION RATES')


data = fetch_data()
years = sorted(data.YEAR.unique())
min_year, max_year = int(years[0]), int(years[-1])