from dash import Dash, dcc, html, Input, Output, no_update, State, dash_table
from dash.dependencies import Input, Output
from dash_bootstrap_templates import load_figure_template
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd
import warnings
import numpy as np
import datetime as dt
import locale as lo

warnings.simplefilter(action = "ignore", category = FutureWarning)
load_figure_template("LUX") 
lo.setlocale(lo.LC_ALL, "french")

app = Dash(__name__, external_stylesheets = [dbc.themes.LUX, dbc.icons.BOOTSTRAP])

LOGO = "https://corentinducloux.fr/dossier_img/icons8-diskette-32.png"
url = dcc.Location(id = "url", pathname = "/")

df = pd.read_csv("depenses.csv")
df2 = df.copy(deep = True)
df2["mois"] = pd.to_datetime(df["date"], format = "%Y-%m-%d").dt.strftime("%B").str.capitalize()
df2["jour"] = pd.to_datetime(df["date"], format = "%Y-%m-%d").dt.strftime("%d")

table = dash_table.DataTable(
        id = "tableau",
        columns = [{"name": i, "id": i} for i in df.columns],
        data = df.to_dict("rows"),
        sort_action = "native",
        sort_mode = "multi",
        page_action = "native",
        page_current = 0,
        page_size = 10,
        
        style_header = {
        "backgroundColor": "rgb(30, 30, 30)",
        "color": "white"
    },
    style_data = {
        "backgroundColor": "rgb(50, 50, 50)",
        "color": "white"
    },
    )

reset_button = dbc.Button(id = "reset-button",className = "bi bi-arrow-counterclockwise py-0 px-1",
                          size = "lg", n_clicks = 0)

navbar = dbc.Navbar(
    dbc.Container(
        [
            html.A(
                dbc.Row(
                    [
                        dbc.Col(html.Img(src = LOGO, height = "30px")),
                        dbc.Col(dbc.NavbarBrand("Gestion des dépenses mensuelles", className = "ms-2")),
                    ],
                    align = "center",
                    className = "g-0",
                ),
                href = "https://corentinducloux.fr",
                style = {"textDecoration": "none"},
            ),
            reset_button,
            url,
        ]
    ),
    color = "dark",
    dark = True,
)

SIDEBAR_STYLE = {
    "position": "fixed",
    "top": 80,
    "left": 0,
    "right":0,
    "bottom": 0,
    "width": "24rem",
    "padding": "1rem 1.5rem",
    "background-color": "#f8f9fa",
}

sidebar = html.Div(
    [
        html.H2("Ajout de nouvelles dépenses"),
        html.Hr(),
        html.P(
            "Ajoute de nouvelles dépenses et met à jour le tableau associé", className = "lead"
        ),
        dbc.Nav(
            [
                dcc.Input(id = "input-df1", type = "number", placeholder = " Nouvelle dépense (en €)"),
                
                dcc.Input(id = "input-df2", type = "text", placeholder = " Intitulé de la dépense"),
                
                dcc.Dropdown(id = "input-df3", placeholder = "Catégorie de la dépense", options = [
                    {"label": "Courses", "value" : "Courses"},
                    {"label": "Factures", "value" : "Factures"},
                    {"label": "Transport", "value" : "Transport"},
                    {"label": "Médical", "value" : "Médical"},
                    {"label": "Loisirs", "value" : "Loisirs"},
                    {"label": "Autre", "value" : "Autre"},
                ]),
                
                html.Div([html.A("Date : "), 
                          dcc.DatePickerSingle(
                              id = "input-df4", date = dt.datetime.now().strftime("%Y-%m-%d"))], 
                        style = {"display": "inline-block"}),
                
                dcc.RadioItems(["Individu A","Individu B"], id = "input-df5", 
                               labelStyle = {"margin-right": "25px"},
                               inputStyle = {"margin-right": "5px"},
                               style = {"margin-left" : "15px",
                                        "padding" : "5px",
                                        "margin-right" : "20px"}),
            ],
            vertical = True,
            pills = True,
        ),
        html.Br(),
        dbc.Button("Ajouter une ligne", id = "bouton_ajout"),
    ],
    style = SIDEBAR_STYLE,
)

select_mois = dcc.Dropdown(id = "list_mois",
                           placeholder = "Choisir un mois",
                           options = [{"label": month, "value": month} for month in df2["mois"].unique()],
                           value = "Janvier")

somme_totale = html.Div([html.Br(),
                         html.H5(id = "somme", children = "Selected option: {{list_mois}}"),
                        ])

graphs = html.Div([
    dbc.Row([
    dbc.Col(dcc.Graph(id = "graph-1", config = {"displayModeBar": False}), width = 6),
    dbc.Col(dcc.Graph(id = "graph-2", config = {"displayModeBar": False}), width = 6),
    ]),
    html.Hr(),
    dbc.Row(dcc.Graph(id = "graph-3")),
])

app.layout = html.Div([
    dbc.Row(navbar), dbc.Row([
        dbc.Col(sidebar), dbc.Col(width = 8, children = [
            dcc.Tabs(id = "tabs", children = [
                dcc.Tab(label = "Données", children = [
                    html.Div([dbc.Col(table, width = 12)], id = "tab_1")
                ]),
                dcc.Tab(label = "Graphiques et infos", children = [
                    html.Div([select_mois, somme_totale, graphs], id = "tab_2")
                ]),
            ]),
        ]),
    ]),
])

@app.callback(Output("tableau", "data"), [Input("bouton_ajout", "n_clicks")], [
    State("input-df1", "value"),
    State("input-df2", "value"),
    State("input-df3", "value"),
    State("input-df4", "date"),
    State("input-df5", "value")
])

def add_row(n_clicks, depenses, intitule, categorie, date, qui):
    df.loc[len(df)] = [depenses, intitule, categorie, date, qui]
    df.dropna(axis = 0, how = "any", thresh = None, subset = None, inplace = True)
    df.to_csv("depenses.csv", index = False)
    return df.to_dict("rows")

@app.callback(
    Output("graph-1", "figure"),
    [Input("list_mois", "value")]
)

def update_pie_chart(selected_month):
    month_df = df2[df2["mois"] == selected_month]
    fig1 = px.pie(month_df, values = "depenses", names = "qui", hole = 0.4,
                  color_discrete_sequence = px.colors.sequential.Darkmint,
                  title = f"Répartition des dépenses en {selected_month}")
    fig1.update_traces(hovertemplate = "%{label} : %{value} €")
    return fig1

@app.callback(
    Output("graph-2", "figure"),
    [Input("dropdown", "value")]
)

def update_line_chart(selected_month):
    month_df = df2[df2["mois"] == selected_month]
    dep_jour =  pd.DataFrame(month_df.groupby("jour")["depenses"].sum()).reset_index()
    fig2 = px.line(dep_jour,
                   x = "jour", y = "depenses",
                   title = f"Dépenses par jour en {selected_month}",
                   color_discrete_sequence = px.colors.sequential.Purples_r,
                   labels = {"depenses": "Dépenses (en €)", "jour": "Jour du mois"})
    dep_jour_sort = dep_jour.sort_values("depenses", ascending = False)
    fig2.update_traces(hovertemplate = "%{y} €") 
    return fig2

@app.callback(
    Output("graph-3", "figure"),
    [Input("list_mois", "value")]
)

def update_bar_chart(selected_month):
    if selected_month != None:
        titre = f"Dépenses par catégorie en {selected_month}"
        month_df = df2[df2["mois"] == selected_month]
        dep_cat = pd.DataFrame(month_df.groupby("categorie")["depenses"].sum()).reset_index()
        fig3 = px.bar(dep_cat.sort_values("depenses", ascending = False),
            x = "categorie", y = "depenses", 
            title = titre,
            labels = {"depenses": "Dépenses (en €)", "categorie": "Catégorie"},
            color = "depenses", color_continuous_scale = "darkmint")
        dep_cat_sort = dep_cat.sort_values("depenses", ascending = False)
        fig3.update_traces(
            customdata = np.stack((dep_cat_sort.depenses, dep_cat_sort.categorie), axis = -1),
            hovertemplate = """%{customdata[0]:.2f} €""")
    else:    
        titre = "/!\ - Pas de mois sélectionné"
        fig3 = px.bar(title = titre)
    return fig3

@app.callback(
    Output("somme", "children"),
    [Input("list_mois", "value")]
)

def update_sum(selected_month):
    if selected_month == None:
        return "Veuillez sélectionner un mois pour afficher les graphiques"
    month_df = df2[df2["mois"] == selected_month]
    total_sum = round(month_df["depenses"].sum(),2)
    ratio = round((total_sum/576.5)*100,2)
    return f"| Dépenses totales pour le mois de {selected_month} : {total_sum} € - ({ratio} %)"

@app.callback(
    Output("url", "pathname"),
    [Input("reset-button", "n_clicks")],
)
def reset_application(n_clicks):
    return "/"

app.run_server(port = "8052")