# dash_oop_components
> `dash_oop_components` is a small helper library with OOP dashboard building blocks for the plotly dash library


## Install

`pip install dash_oop_components`

## Purpose

This library allows you to write clean, modular, composable, re-usable and fully configurable dash code.

It includes:
- `DashFigureFactory`: a wrapper for your data/plotting functionality.
- `DashComponent`: a self-contained, modular, configurable unit of code that combines a layout with callbacks.
    - These components are composable, meaning that other `DashComponent`s can consist of multiple subcomponents.
    - Makes use of a `DashFigureFactory` for plots or other data output
- `DashApp`: Build a dashboard out of `DashComponent` and run it.

All the components:
- Automatically store all params to attributes and to a ._stored_params dict
- Allow you to store its' config to a `.yaml` file, including import details, and can then  
    be fully reloaded from a config file.

This allows you to:
- Seperate the data/plotting logic from the dashboard interactions logic, by putting all 
    the plotting functionality inside a `DashFigureFactory`. 
- Build self-contained, configurable, re-usable `DashComponents`
- Compose dashboards that consists of multiple `DashComponents` that each may 
    consists of multiple `DashComponents`, etc.
- Store all the configuration needed to rebuild and run a particular dashboard to 
    a single configuration `.yaml` file
- Parametrize your dashboard so that you (or others) can make change to the dashboard
    without having to edit the code.

## Example:

```python
#!pip install pandas plotly-express
```

```python
import dash_html_components as html
import dash_core_components as dcc
import dash_bootstrap_components as dbc

from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate

import pandas as pd
import plotly.express as px
```

### CovidPlots: a DashFigureFactory

A basic `DashFigureFactory` that loads a covid dataset, and provides a single plotting functionality: `plot_time_series()`.

```python
class CovidPlots(DashFigureFactory):
    def __init__(self, datafile="covid.csv"):
        super().__init__()
        self.df = pd.read_csv(datafile)
        
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
```

### CovidTimeSeries: a DashComponent

A `DashComponent` that takes a plot_factory and build a layout with two dropdowns and a graph:

```python
class CovidTimeSeries(DashComponent):
    def __init__(self, plot_factory, 
                 hide_country_dropdown=False, countries=None, 
                 hide_metric_dropdown=False, metric='cases'):
        super().__init__()
        
        if not self.countries:
            self.countries = self.plot_factory.countries
        
    def layout(self):
        return dbc.Container([
            dbc.Row([
                dbc.Col([
                    html.H3("Covid Time Series"),
                    self.make_hideable(
                        dcc.Dropdown(
                            id='timeseries-metric-dropdown-'+self.name,
                            options=[{'label': metric, 'value': metric} for metric in ['cases', 'deaths']],
                            value=self.metric,
                        ), hide=self.hide_metric_dropdown),
                    self.make_hideable(
                        dcc.Dropdown(
                            id='timeseries-country-dropdown-'+self.name,
                            options=[{'label': country, 'value': country} for country in self.plot_factory.countries],
                            value=self.countries,
                            multi=True,
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
            if countries and metric:
                return self.plot_factory.plot_time_series(countries, metric)
            raise PreventUpdate
```

### DuoPlots: a composition of two subcomponents
A `DashComponent` that combines two `CovidTimeSeries` into a single layout. 
Both subcomponents are assigned different initial values.

```python
class DuoPlots(DashComponent):
    def __init__(self, plot_factory):
        super().__init__()
        self.plot_left = CovidTimeSeries(plot_factory, 
                                         countries=['China', 'Vietnam', 'Taiwan'], 
                                         metric='cases')
        self.plot_right = CovidTimeSeries(plot_factory, 
                                          countries=['Italy', 'Germany', 'Sweden'], 
                                          metric='deaths')
        
        self.register_components(self.plot_left, self.plot_right)
        
    def layout(self):
        return dbc.Container([
            dbc.Row([
                dbc.Col([
                    self.plot_left.layout()
                ]),
                dbc.Col([
                    self.plot_right.layout()
                ])
            ])
        ], fluid=True)
```

### Start dashboard:

Load the plot_factory and show its config:

```python
plot_factory = CovidPlots(datafile="covid.csv")
print(plot_factory.to_yaml())
```

    dash_figure_factory:
      name: CovidPlots
      module: __main__
      params:
        datafile: covid.csv
    


Load the `CovidDashboard`, by passing the `plot_factory` and accepting the default parameters for `europe_countries` and `asia_countries`:

```python
dashboard_component = DuoPlots(plot_factory)
print(dashboard_component.to_yaml())
```

    dash_component:
      name: DuoPlots
      module: __main__
      params:
        plot_factory:
          dash_figure_factory:
            name: CovidPlots
            module: __main__
            params:
              datafile: covid.csv
    


Pass the `dashboard_component` to the `DashApp`, and add the bootstrap stylesheet that is needed to correctly display all the `dbc.Row`s and `dbc.Col`s:

```python
app = DashApp(dashboard_component, external_stylesheets=[dbc.themes.BOOTSTRAP])
print(app.to_yaml())
```

    dash_app:
      name: DashApp
      module: dash_oop_components.core
      params:
        dashboard_component:
          dash_component:
            name: DuoPlots
            module: __main__
            params:
              plot_factory:
                dash_figure_factory:
                  name: CovidPlots
                  module: __main__
                  params:
                    datafile: covid.csv
        port: 8050
        mode: dash
        kwargs:
          external_stylesheets:
          - https://stackpath.bootstrapcdn.com/bootstrap/4.5.0/css/bootstrap.min.css
    


(turn cell below into codecell to actually run)

```python
app2.run()
```

### reload dashboard from config:

```python
app.to_yaml("covid_dashboard.yaml")
```

```python
app2 = DashApp.from_yaml("covid_dashboard.yaml")
```

We can check that the configuration of this new `app2` is indeed the same as `app`:

```python
print(app2.to_yaml())
```

    dash_app:
      name: DashApp
      module: dash_oop_components.core
      params:
        dashboard_component:
          dash_component:
            name: DuoPlots
            module: __main__
            params:
              plot_factory:
                dash_figure_factory:
                  name: CovidPlots
                  module: __main__
                  params:
                    datafile: covid.csv
        port: 8050
        mode: dash
        kwargs:
          external_stylesheets:
          - https://stackpath.bootstrapcdn.com/bootstrap/4.5.0/css/bootstrap.min.css
    


And if we run it it still works!

(turn into code cell to actually run)

```python
app2.run()
```
