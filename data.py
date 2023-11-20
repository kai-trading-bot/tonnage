import numpy as np
import pandas as pd
import ipywidgets as widgets
import plotly.offline as py
import plotly.graph_objs as go
import warnings

py.init_notebook_mode(connected=True)
warnings.simplefilter(action='ignore', category=FutureWarning)


__author__ = 'kqureshi'

DATA_PATH = '/Users/kq/Downloads/aggregated_Tonnage_byYear_cleaned.csv'

def fetch_data() -> pd.DataFrame:
    """
    Fetch and process data
    """
    data = pd.read_csv(DATA_PATH)
    data.YEAR = data.YEAR.astype(str)
    data.DISTRICT = data.DISTRICT.astype(str)    
    return data


def update_plot(slider_year: int) -> py.iplot:
    """
    Use slider to query for year and create diagram
    """

    links = []
    data = fetch_data()
    data = data[data.YEAR == str(slider_year)]
    grouper = data.groupby(['YEAR', 'BOROUGH', 'DISTRICT']).sum()
    years = sorted(grouper.index.levels[0])
    boroughs = sorted(grouper.index.levels[1])
    districts = sorted(grouper.index.levels[2])

    for year in years:
        year_level = grouper.xs(year, level=0)    
        borough_level = year_level.sum(level=0)
        sum_borough = borough_level.sum(axis=1)
        for borough in sorted(sum_borough.index.unique()):
            links.append({'source': year,
                                  'target': borough,
                                  'value': sum_borough.loc[borough]})

        for borough in sorted(borough_level.index.unique()):
            district_level = year_level.xs(borough)
            sum_district = district_level.sum(axis=1)
            for district in sorted(sum_district.index):
                links.append({'source': borough,
                                      'target': district,
                                      'value': sum_district.loc[district]})
            for district in sorted(district_level.index.unique()):
                target_district = district_level.loc[district]
                for style in sorted(target_district.index):
                    links.append({'source': district,
                                  'target': style,
                                  'value': target_district.loc[style]})

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
    fig.update_layout(title=dict(text="{year} Collection Distribution".format(year=slider_year), font=dict(size=12)), width=2000, height=2000)
    py.iplot(fig, filename='HISTORICAL COLLECTION RATES')
   

def fetch_figure() -> None:
    data = fetch_data()
    years = sorted(data.YEAR.unique())
    min_year, max_year = int(years[0]), int(years[-1])
    widgets.interact(update_plot, slider_year=(min_year, max_year))
    
