# dash_oop_components
> `dash_oop_components` is a small helper library with OOP dashboard building blocks for the plotly dash library


## Install

`pip install dash_oop_components`

## Purpose

Plotly's [dash](dash.plotly.com) is an awesome library that allows you to build rich interactive data driven web apps with pure python code. However the default style of dash apps quite declarative, which for large projects can lead to code that become unwieldy and hard to maintain.

This library provides three object-oriented wrappers for organizing your dash code that allow you to write clean, modular, composable, re-usable and fully configurable dash code.

It includes:
- `DashFigureFactory`: a wrapper for your data/plotting functionality.
- `DashComponent`: a self-contained, modular, configurable unit that combines a layout with callbacks.
    - Makes use of a `DashFigureFactory` for plots or other data output
    - DashComponents are composable, meaning that other `DashComponent`s can consist of multiple subcomponents.
- `DashApp`: Build a dashboard out of `DashComponent` and run it.

All three wrappers:
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

## To import:

```python
from dash_oop_components import DashFigureFactory, DashComponent, DashApp
```

## Example:

A similar dashboard has been deployed to [https://dash-oop-demo.herokuapp.com/](https://dash-oop-demo.herokuapp.com/)

### CovidPlots: a DashFigureFactory

First we define a basic `DashFigureFactory` that loads a covid dataset, and provides a single plotting functionality, namely `plot_time_series(countries, metric)`. Make sure to call `super().__init__()` in order to params to attributes (that's why datafile gets automatically assigned to self.datafile), and store them to a `._stored_params` dict so that they can be exported to a config file.

```python
class CovidPlots(DashFigureFactory):
    def __init__(self, datafile="covid.csv"):
        super().__init__()
        self.df = pd.read_csv(self.datafile)
        
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
    
figure_factory = CovidPlots("covid.csv")
print(figure_factory.to_yaml())
```

    dash_figure_factory:
      name: CovidPlots
      module: __main__
      params:
        datafile: covid.csv
    


### CovidTimeSeries: a DashComponent

Then we define a `DashComponent` that takes a plot_factory and build a layout with two dropdowns and a graph:

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

Callbacks of subcomponents get automatically registered. Additional callbacks should be defined under `self._register_callbacks(app)` (**note the underscore!**)

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
    
dashboard = DuoPlots(figure_factory)
print(dashboard.to_yaml())
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
    


### Start dashboard:

Pass the `dashboard` to the `DashApp`, and add the bootstrap stylesheet that is needed to correctly display all the `dbc.Row`s and `dbc.Col`s:

```python
app = DashApp(dashboard, external_stylesheets=[dbc.themes.BOOTSTRAP])
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
if not True:
    app.run()
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


```python
if not True: # remove to run
    app2.run()
```
