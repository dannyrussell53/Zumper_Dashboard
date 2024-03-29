import pandas as pd
import dash
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import plotly.express as px
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash import Dash, dcc, html, Input, Output
import plotly.express as px
import matplotlib.cm as cm

df_imported = pd.read_csv('df_rents.csv')
df_imported['Date'] = pd.to_datetime(df_imported['Date'],format='%Y-%m-%d')
df_imported['City'] = df_imported['RegionName'].astype(str)

#get state code last two of each city
df_imported['state'] = df_imported['City'].str[-2:]

#get updated date
dates_unique = df_imported['Date'].unique()
last_updated = dates_unique[-1]
#get list of states
cities_unique = df_imported['City'].unique()

df_yoy = df_imported[df_imported['Date']==last_updated][['Date','Longitude','Latitude','Rent','City','Pct_Chg_12M_3M_Rolling_Average_Rents','Rolling_3_Month_Average_Rent']]
#get scaled
df_yoy['YoY_3M_Avg_Rent_Pct_Change_Scaled'] = (df_yoy['Pct_Chg_12M_3M_Rolling_Average_Rents'] - df_yoy['Pct_Chg_12M_3M_Rolling_Average_Rents'].min()) / (df_yoy['Pct_Chg_12M_3M_Rolling_Average_Rents'].max() - df_yoy['Pct_Chg_12M_3M_Rolling_Average_Rents'].min())
#add text field
df_yoy['Text'] = df_yoy['City'] + ' YoY Pcg Change 3 Month Avg Rents: ' + (df_yoy['Pct_Chg_12M_3M_Rolling_Average_Rents']).map('{:.2%}'.format)

# print(df_imported['Region'].unique())
# Region_Selector_Test = 'Northeast'

#regions
#df_regions = df_imported[df_imported['Region']==Region_Selector_Test][['Date','Rent','City','Rolling_3_Month_Average_Rent','Region']]

#regions dataframe
df_regions = df_imported[['Date','Rent','City','Rolling_3_Month_Average_Rent','Region']]


colors = {
    'background': '#004a5d',
    'text': '#7FDBFF',
    'graph_background': '#e6faff'
}

map_fig = go.Figure(data=go.Scattergeo(
        locationmode = 'USA-states',
        lon = df_yoy['Longitude'].values,
        lat = df_yoy['Latitude'].values,
        text = df_yoy['Text'],
        mode = 'markers',
        marker = dict(
            size = 6,
            opacity = 0.99,
            reversescale = True,
            autocolorscale = True,
            symbol = 'circle',
            line = dict(
                width=1,
                color='rgba(102, 102, 102)'
            ),
            colorscale = 'edge',
            cmin = 0,
            color = df_yoy['YoY_3M_Avg_Rent_Pct_Change_Scaled'],
            cmax = df_yoy['YoY_3M_Avg_Rent_Pct_Change_Scaled'].max(),
            colorbar_title="3 Month Avg Rent" + " YoY % Change Scaled",


        )))

#map_fig.layout.coloraxis.colorbar.titlefont.size = 12
#map_fig.update_layout(coloraxis_colorbar_y=0.05)
#map_fig.update_layout(coloraxis_colorbar_x=0.8)

map_fig.update_layout(
        title = 'Normalized 3 Month Average Rents YoY Percent Change (Hover Over for actual change)',
        geo = dict(
            scope='usa',
            projection_type='albers usa',
            showland = True,
            landcolor = "rgb(0, 74, 93)",
            subunitcolor = "rgb(217, 217, 217)",
            countrycolor = "rgb(217, 217, 217)",
            countrywidth = 0.5,
            subunitwidth = 0.5,
            bgcolor= "rgb(0, 74, 93)",
            oceancolor="rgb(0, 74, 93)"
        ),
    )
#update paper color (background color) of figure
map_fig.update_layout(paper_bgcolor="rgb(0, 74, 93)")

#update font color
map_fig.update_layout(
    #font_family="Courier New",
    font_color="White",
    title_font_family="Times New Roman",
    title_font_color="White",
    legend_title_font_color="White"
)

map_fig.add_annotation(dict(font=dict(color='white',size=8),
                                        x=.8,
                                        y=-0.12,
                                        showarrow=False,
                                        text="Data provided by Zillow and updated monthly",
                                        textangle=0,
                                        xanchor='left',
                                        xref="paper",
                                        yref="paper"))





color_scale = ['#02b5e3', '#a2d0d4']

# Create a colormap based on the color scale
colormap = cm.colors.LinearSegmentedColormap.from_list('custom_colormap', color_scale)





df_table = df_imported

# Convert the 'Date' column to datetime
df_table['Date'] = pd.to_datetime(df_table['Date'])

# Find the maximum date
max_date = df_table['Date'].max()

# Filter the DataFrame to include only rows with the maximum date
df_table = df_table[df_table['Date'] == max_date]


df_table = df_table[['RegionName','Pct_Chg_12M_3M_Rolling_Average_Rents']]


#filtered_df_table['Pct_Chg_12M_3M_Rolling_Average_Rents'] =(filtered_df_table['Pct_Chg_12M_3M_Rolling_Average_Rents'] * 100).round(2).astype(str) + "%"
#filtered
df_table = df_table.head(35)
df_table = df_table.reset_index(drop=True)

df_table = df_table.sort_values('Pct_Chg_12M_3M_Rolling_Average_Rents', ascending=False)




# Normalize the values
norm = cm.colors.Normalize(vmin=df_table['Pct_Chg_12M_3M_Rolling_Average_Rents'].min(),
                           vmax=df_table['Pct_Chg_12M_3M_Rolling_Average_Rents'].max())

# Convert values to colors based on the colormap
colors = [cm.colors.rgb2hex(colormap(norm(value))) for value in df_table['Pct_Chg_12M_3M_Rolling_Average_Rents']]

formatted_values = [f"{value:.2%}" for value in df_table['Pct_Chg_12M_3M_Rolling_Average_Rents']]

# Create the table trace
table_trace = go.Table(
    header=dict(values=list(df_table.columns), fill_color='#02b5e3', align='center'),
    cells=dict(
        values=[df_table['RegionName'], formatted_values],
        fill=dict(color=[colors, colors]),  # Same color for both columns
        align='center'
    )
)


app = dash.Dash(
    external_stylesheets=[dbc.themes.SOLAR]

)
server = app.server 

app.layout = html.Div(
    [
    html.H3("Zillow Rent by Month Dashboard",style={'textAlign': 'center'}),
    html.H5("Are rents really coming down?",style={'textAlign': 'center'}),
    dcc.Graph(figure=map_fig),
    dcc.Checklist(
        id="checklist",
        options=["Northeast", "Texas", "Southeast", "West", "Midwest"],
        value=["Texas"],
        inline=True,
        labelStyle= {'margin-right':'5px'},
        style={
            'textAlign': 'center',
            'padding':'5px',
            'margin-right':'80px'
            #'float':'left'

        }


    ),
    dcc.Graph(id="graph"),
    html.Br(),
    html.H5("Top Rent Changes by City",style={'textAlign': 'center'}),
    #dcc.Graph(figure=go.Figure(data=[table_trace])),


    dcc.Graph(
            figure=go.Figure(
                data=[table_trace],
                layout=go.Layout(
                    plot_bgcolor='#004a5d',  # Set the plot background color to match SOLAR theme
                    paper_bgcolor='#004a5d',  # Set the paper background color to match SOLAR theme
                    font=dict(color='#ffffff')  # Set the font color to match SOLAR theme
                )
            )
        ),
    html.A("Dashboard made by Danny Russell", href='https://www.linkedin.com/in/daniel-russell-iv-cfa-15681114/', target="_blank")
])


@app.callback(
    Output("graph", "figure"),
    Input("checklist", "value"))
def update_line_chart(continents):
    df = df_imported  # replace with your own data source
    mask = df.Region.isin(continents)
    fig = px.line(df[mask],
                  x="Date", y="Rent", color='City',color_discrete_sequence=px.colors.qualitative.Dark2,title='3 Month Average Rent By City')
    fig.update_layout(paper_bgcolor="rgb(0,74,93)")
    fig.update_layout(plot_bgcolor="rgb(0,74,93)")
    fig.update_yaxes(title_font_color="White")
    fig.update_xaxes(title_font_color="White")
    fig.update_yaxes(tickfont=dict(color='White'))
    fig.update_xaxes(tickfont=dict(color='White'))

    fig.update_layout(
        #font_family="Courier New",
        font_color="White",
        #title_font_family="Times New Roman",
        title_font_color="White",
        #legend_title_font_color="green"
    )

    fig.update_layout(
        legend=dict(
            traceorder="reversed",
            #title_font_family="Times New Roman",
            font=dict(
                #family="Courier",
                size=12,
                color="black"
            ),
            bgcolor="rgb(172, 238, 255)",
            bordercolor="Black",
            borderwidth=2
        ))
    return fig
if __name__ == "__main__":
    app.run_server()
