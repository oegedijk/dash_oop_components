# dash_oop_components
> `dash_oop_components` is a small helper library with OOP dashboard building blocks for the plotly dash library


## Install

`pip install dash_oop_components`

# Purpose

This library allows you to write clean, modular, composable, re-usable and fully configurable dash code.

It includes:
- 'DashFigureFactory`: a wrapper for your data/plotting functionality.
- `DashComponent`: a self-contained, modular, configurable unit of code that combines a layout with callbacks.
    - These components are composable, meaning that other `DashComponent`s can consist of multiple subcomponents.
    - Makes use of a `DashFigureFactory` for plots or other data output
- `DashApp`: Build a dashboard out of `DashComponent` and run it.

All these components allow you to store its' config to a `.yaml` file, and can be fully reloaded
from that same config file.



    - Store a component config to yaml, and reload the same component from yaml
It allows you to:
    - Seperate the data/plotting logic from the dashboard interactions logic, by putting all 
        the plotting functionality inside a `DashFigureFactory`. The configuration (e.g. filenames, etc), 
        
    - Build self-contained re-usable `DashComponents`

# Example:

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

## Start dashboard:

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
dashboard_component = CovidTimeSeries(plot_factory)
print(dashboard_component.to_yaml())
```

    dash_component:
      name: CovidTimeSeries
      module: __main__
      params:
        plot_factory:
          dash_figure_factory:
            name: CovidPlots
            module: __main__
            params:
              datafile: covid.csv
        hide_country_dropdown: false
        countries: null
        hide_metric_dropdown: false
        metric: cases
    


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
            name: CovidTimeSeries
            module: __main__
            params:
              plot_factory:
                dash_figure_factory:
                  name: CovidPlots
                  module: __main__
                  params:
                    datafile: covid.csv
              hide_country_dropdown: false
              countries: null
              hide_metric_dropdown: false
              metric: cases
        port: 8050
        mode: dash
        kwargs:
          external_stylesheets:
          - https://stackpath.bootstrapcdn.com/bootstrap/4.5.0/css/bootstrap.min.css
    


Uncomment o run the dashboard:

```python
# app.run()
```

## reload dashboard from config:

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
            name: CovidTimeSeries
            module: __main__
            params:
              plot_factory:
                dash_figure_factory:
                  name: CovidPlots
                  module: __main__
                  params:
                    datafile: covid.csv
              hide_country_dropdown: false
              countries: null
              hide_metric_dropdown: false
              metric: cases
        port: 8050
        mode: dash
        kwargs:
          external_stylesheets:
          - https://stackpath.bootstrapcdn.com/bootstrap/4.5.0/css/bootstrap.min.css
    


And if we run it it still works!

(uncomment to run)

```python
#app2.run()
```
