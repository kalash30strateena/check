
import pandas as pd
from tabs_data.credentials import cred # type: ignore
import plotly.graph_objects as go

def fetch_categories(category_type):
    engine = cred()
    query = """
        SELECT category_id, category_name FROM indicator_categories
        WHERE category_type = %s
    """
    return pd.read_sql(query, engine, params=(category_type,))

def fetch_indicators(category_id):
    engine = cred()
    query = """
        SELECT indicator_name, indicator_year, value_index
        FROM indicators
        WHERE category_id = %s
    """
    return pd.read_sql(query, engine, params=(category_id,))

def plotly_indicators(df):
    df = df.sort_values(by="indicator_year", ascending=True)
    plots = []
    colors = [
        "#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd",
        "#8c564b", "#e377c2", "#7f7f7f", "#bcbd22", "#17becf"
    ]
    color_index = 0
    for name in df['indicator_name'].unique():
        sub_df = df[df['indicator_name'] == name]
        color = colors[color_index % len(colors)]

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=sub_df['indicator_year'],
            y=sub_df['value_index'],
            mode="lines+markers",
            name=name,
            line=dict(color=color)
        ))
        fig.update_layout(
            title=name,
            xaxis_title="Year",
            yaxis_title="Value"
        )
        plots.append(fig)
        color_index += 1
    return plots
