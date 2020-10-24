# dash_oop_components
> small library for OOP dashboard building blocks 


## Install

`pip install dash_oop_components`

## Example of use

```python
import dash_html_components as html
import dash_core_components as dcc
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate

import pandas as pd
import plotly.express as px
```

## CovidPlots

```python
class CovidPlots(DashFigureFactory):
    def __init__(self, datafile="covid.csv", include_countries=[]):
        super().__init__()
        self.df = pd.read_csv(datafile)
        if include_countries:
            self.df = self.df[self.df.countriesAndTerritories.isin(include_countries)]
        self.countries = self.df.countriesAndTerritories.unique().tolist()
        self.metrics = ['cases', 'deaths']
        
    def plot_time_series(self, countries, metric):
        return px.line(
            data_frame=self.df[self.df.countriesAndTerritories.isin(countries)],
            x='dateRep',
            y=metric,
            color='countriesAndTerritories',
            labels={'countriesAndTerritories':'Countries', 'dateRep':'date'},
            )
    
    def plot_pie_chart(self, countries, metric):
        return px.pie(
            data_frame=self.df[self.df.countriesAndTerritories.isin(countries)],
            names='countriesAndTerritories',
            values=metric,
            hole=.3,
            labels={'countriesAndTerritories':'Countries'}
            ) 
```

## CovidTimeSeries

```python
class CovidTimeSeries(DashComponent):
    def __init__(self, plot_factory, 
                 hide_country_dropdown=False, countries=[], 
                 hide_metric_dropdown=False, metric='cases'):
        super().__init__()
        
        if not self.countries:
            self.countries = self.plot_factory.countries[:5]
        
    def layout(self):
        return dbc.Container([
            dbc.Row([
                dbc.Col([
                    html.H3("Covid Time Series"),
                    self.make_hideable(
                        dcc.Dropdown(
                            id='timeseries-metric-dropdown-'+self.name,
                            options=[{'label': metric, 'value': metric} for metric in self.plot_factory.metrics],
                            value=self.metric,
                            clearable=False,
                        ), hide=self.hide_metric_dropdown),
                    self.make_hideable(
                        dcc.Dropdown(
                            id='timeseries-country-dropdown-'+self.name,
                            options=[{'label': metric, 'value': metric} for metric in self.plot_factory.countries],
                            value=self.countries,
                            multi=True,
                            clearable=False,
                        ), hide=self.hide_country_dropdown),
                    dcc.Graph(id='timeseries-figure-'+self.name)
                ]),
            ])
        ])
    
    def _register_callbacks(self, app):
        @app.callback(
            Output('timeseries-figure-'+self.name, 'figure'),
            Input('timeseries-country-dropdown-'+self.name, 'value'),
            Input('timeseries-metric-dropdown-'+self.name, 'value')
        )
        def update_timeseries_plot(countries, metric):
            if countries:
                return self.plot_factory.plot_time_series(countries, metric)
            raise PreventUpdate
```

## CovidPieChart

```python
class CovidPieChart(DashComponent):
    def __init__(self, plot_factory, 
                 hide_country_dropdown=False, countries=[], 
                 hide_metric_dropdown=False, metric='cases'):
        super().__init__()
        
        if not self.countries:
            self.countries = self.plot_factory.countries[:5]
        
    def layout(self):
        return dbc.Container([
            dbc.Row([
                dbc.Col([
                    html.H3("Covid Pie Chart"),
                    self.make_hideable(
                        dcc.Dropdown(
                            id='piechart-metric-dropdown-'+self.name,
                            options=[{'label': metric, 'value': metric} for metric in self.plot_factory.metrics],
                            value=self.metric,
                            clearable=False,
                        ), hide=self.hide_metric_dropdown),
                    self.make_hideable(
                        dcc.Dropdown(
                            id='piechart-country-dropdown-'+self.name,
                            options=[{'label': metric, 'value': metric} for metric in self.plot_factory.countries],
                            value=self.countries,
                            multi=True
                            #clearable=False,
                        ), hide=self.hide_country_dropdown),
                    dcc.Graph(id='piechart-figure-'+self.name)
                ]),
            ])
        ])
    
    def _register_callbacks(self, app):
        @app.callback(
            Output('piechart-figure-'+self.name, 'figure'),
            Input('piechart-country-dropdown-'+self.name, 'value'),
            Input('piechart-metric-dropdown-'+self.name, 'value')
        )
        def update_timeseries_plot(countries, metric):
            if countries:
                return self.plot_factory.plot_pie_chart(countries, metric)
            raise PreventUpdate
```

## CovidDashboard

```python
class CovidDashboard(DashComponent):
    def __init__(self, plot_factory, 
                 hide_country_dropdowns=False, countries=[], 
                 hide_metric_dropdowns=False, metric='cases'):
        super().__init__(title="Covid Dashboard")
        
        if not self.countries:
            self.countries = self.plot_factory.countries[:5]
        
        self.timeseries = CovidTimeSeries(
                plot_factory, 
                hide_country_dropdown=hide_country_dropdowns,
                hide_metric_dropdown=hide_metric_dropdowns)
        
        self.piechart = CovidPieChart(
                plot_factory, 
                hide_country_dropdown=hide_country_dropdowns,
                hide_metric_dropdown=hide_metric_dropdowns)
        
        self.register_components(self.timeseries, self.piechart)
        
    def layout(self):
        return dbc.Container([
            dbc.Row([
                dbc.Col([
                    html.H1(self.title),
                    dcc.Dropdown(
                        id='dashboard-metric-dropdown-'+self.name,
                        options=[{'label': metric, 'value': metric} for metric in self.plot_factory.metrics],
                        value=self.metric,
                        clearable=False,
                    ),
                    dcc.Dropdown(
                        id='dashboard-country-dropdown-'+self.name,
                        options=[{'label': metric, 'value': metric} for metric in self.plot_factory.countries],
                        value=self.countries,
                        multi=True,
                        clearable=False,
                    ),
                ], md=6),
            ], justify="center"),
            dbc.Row([
                dbc.Col([
                    self.timeseries.layout(),
                ], md=6),
                dbc.Col([
                    self.piechart.layout(),
                ], md=6)
            ])
        ], fluid=True)
    
    def _register_callbacks(self, app):
        @app.callback(
            Output('timeseries-country-dropdown-'+self.timeseries.name, 'value'),
            Output('piechart-country-dropdown-'+self.piechart.name, 'value'),
            Input('dashboard-country-dropdown-'+self.name, 'value'),
        )
        def update_timeseries_plot(countries):
            return countries, countries
        
        @app.callback(
            Output('timeseries-metric-dropdown-'+self.timeseries.name, 'value'),
            Output('piechart-metric-dropdown-'+self.piechart.name, 'value'),
            Input('dashboard-metric-dropdown-'+self.name, 'value'),
        )
        def update_timeseries_plot(metric):
            return metric, metric
        
```

## Start app

```python
plot_factory = CovidPlots(datafile="covid.csv", include_countries=[
        'United_States_of_America', 'Italy', 'China', 'Spain',
        'Germany', 'France', 'Iran', 'United_Kingdom', 'Switzerland',
        'Netherlands', 'South_Korea', 'Belgium', 'Austria', 
        'Canada', 'Portugal', 'Brazil', 'Norway', 'Australia', 'Israel'])
```

```python
db = CovidDashboard(plot_factory, hide_country_dropdowns=True, countries=['Netherlands', 'Belgium', 'Germany'])
```

```python
app = DashApp(db, external_stylesheets=[dbc.themes.BOOTSTRAP])
```

```python
print(app.to_yaml())
```

    dash_app:
      name: DashApp
      module: dash_oop_components.core
      params:
        dashboard_component:
          dash_component:
            name: CovidDashboard
            module: __main__
            params:
              plot_factory:
                dash_figure_factory:
                  name: CovidPlots
                  module: __main__
                  params:
                    datafile: covid.csv
                    include_countries:
                    - United_States_of_America
                    - Italy
                    - China
                    - Spain
                    - Germany
                    - France
                    - Iran
                    - United_Kingdom
                    - Switzerland
                    - Netherlands
                    - South_Korea
                    - Belgium
                    - Austria
                    - Canada
                    - Portugal
                    - Brazil
                    - Norway
                    - Australia
                    - Israel
              hide_country_dropdowns: true
              countries:
              - Netherlands
              - Belgium
              - Germany
              hide_metric_dropdowns: false
              metric: cases
        port: 8050
        mode: dash
        kwargs:
          external_stylesheets:
          - https://stackpath.bootstrapcdn.com/bootstrap/4.5.0/css/bootstrap.min.css
    


```python
#app.run()
```

    Dash is running on http://127.0.0.1:8050/
    
    Dash is running on http://127.0.0.1:8050/
    
    Dash is running on http://127.0.0.1:8050/
    
     * Serving Flask app "__main__" (lazy loading)
     * Environment: production
    [31m   WARNING: This is a development server. Do not use it in a production deployment.[0m
    [2m   Use a production WSGI server instead.[0m
     * Debug mode: off


     * Running on http://127.0.0.1:8050/ (Press CTRL+C to quit)
    127.0.0.1 - - [24/Oct/2020 22:37:01] "[37mGET /_reload-hash HTTP/1.1[0m" 200 -
    127.0.0.1 - - [24/Oct/2020 22:37:03] "[37mGET / HTTP/1.1[0m" 200 -
    127.0.0.1 - - [24/Oct/2020 22:37:04] "[37mGET /_dash-layout HTTP/1.1[0m" 200 -
    127.0.0.1 - - [24/Oct/2020 22:37:04] "[37mGET /_dash-dependencies HTTP/1.1[0m" 200 -
    127.0.0.1 - - [24/Oct/2020 22:37:04] "[37mGET /_reload-hash HTTP/1.1[0m" 200 -
    127.0.0.1 - - [24/Oct/2020 22:37:04] "[37mPOST /_dash-update-component HTTP/1.1[0m" 200 -
    127.0.0.1 - - [24/Oct/2020 22:37:04] "[37mPOST /_dash-update-component HTTP/1.1[0m" 200 -
    127.0.0.1 - - [24/Oct/2020 22:37:05] "[37mPOST /_dash-update-component HTTP/1.1[0m" 200 -
    127.0.0.1 - - [24/Oct/2020 22:37:05] "[37mPOST /_dash-update-component HTTP/1.1[0m" 200 -
    127.0.0.1 - - [24/Oct/2020 22:37:07] "[37mGET /_reload-hash HTTP/1.1[0m" 200 -
    127.0.0.1 - - [24/Oct/2020 22:37:10] "[37mGET /_reload-hash HTTP/1.1[0m" 200 -


## Store App config and reload

```python
app.to_yaml("covid_dashboard.yaml")
```

```python
app2 = DashApp.from_yaml("covid_dashboard.yaml")
```

```python
#app2.run()
```
