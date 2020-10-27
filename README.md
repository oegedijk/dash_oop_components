# dash_oop_components
> `dash_oop_components` is a small helper library with OOP dashboard building blocks for the plotly dash library


## Install

`pip install dash_oop_components`

## Documentation

Documentation can be found at: [https://oegedijk.github.io/dash_oop_components/](https://oegedijk.github.io/dash_oop_components/)

## Purpose

Plotly's [dash](dash.plotly.com) is an awesome library that allows you to build rich interactive data driven web apps with pure python code. However the default style of dash apps is quite declarative, which for large projects can lead to code that becomes unwieldy and hard to maintain.

This library provides three object-oriented wrappers for organizing your dash code that allow you to write clean, modular, composable, re-usable and fully configurable dash code.

It includes:
- `DashFigureFactory`: a wrapper for your data/plotting functionality.
- `DashComponent`: a self-contained, modular, configurable unit that combines a dash layout with dash callbacks.
    - Makes use of a `DashFigureFactory` for plots or other data output
    - `DashComponents` are composable, meaning that you can nest them into new composite components.
- `DashApp`: Build a dashboard out of `DashComponent` and run it.

All three wrappers:
- Automatically store all params to attributes and to a ._stored_params dict
- Allow you to store its' config to a `.yaml` file, including import details, and can then  
    be fully reloaded from a config file.

This allows you to:
- Seperate the data/plotting logic from the dashboard interactions logic, by putting all 
    the plotting functionality inside a `DashFigureFactory` and all the dashboard layout and callback logic into `DashComponents`.
- Build self-contained, configurable, re-usable `DashComponents`
- Compose dashboards that consists of multiple `DashComponents` that each may 
    consists of multiple nested `DashComponents`, etc.
- Store all the configuration needed to rebuild and run a particular dashboard to 
    a single configuration `.yaml` file
- Parametrize your dashboard so that you (or others) can make change to the dashboard
    without having to edit the code.
- Plus: track the state of your dashboard with querystrings and reload the state from url!

## To import:

```python
from dash_oop_components import DashFigureFactory, DashComponent, DashApp
```

## Example:

An example dashboard can be found at [github.com/oegedijk/dash_oop_demo](https://github.com/oegedijk/dash_oop_demo) and has been deployed to [https://dash-oop-demo.herokuapp.com/](https://dash-oop-demo.herokuapp.com/)

Below is the code for similar but slightly simpler example. Full explanation for the `dash_oop_demo` dashboard can be found [in the documentation](https://oegedijk.github.io/dash_oop_components/Example.html).

The example is a rewrite of this [Charming Data dash instruction video](https://www.youtube.com/watch?v=dgV3GGFMcTc) (go check out his other vids, they're awesome!).

### CovidPlots: a DashFigureFactory

First we define a basic `DashFigureFactory` that loads a covid dataset, and provides a single plotting functionality, namely `plot_time_series(countries, metric)`. Make sure to call `super().__init__()` in order to store params to attributes (that's how the datafile parameters gets automatically assigned to self.datafile for example), and store them to a `._stored_params` dict so that they can later be exported to a config file.

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
      class_name: CovidPlots
      module: __main__
      params:
        datafile: covid.csv
    


### CovidTimeSeries: a DashComponent

Then we define a `DashComponent` that takes a plot_factory and build a layout with two dropdowns and a graph.

- By calling `super().__init__()` all parameters are automatically stored to attributes (so that we can access 
    e.g. `self.hide_country_dropdown`), and to a `._stored_params` dict.
- This layout makes use of the `make_hideable()` staticmethod, to conditionally 
    wrap certain layout elements in a hidden div.
- We track the state of the dropdowns "value" attribute by wrapping it in 
    `self.querystring(params)(dcc.Dropdown)(..)`, and passing the params down to the layout function.
- Note that the layout element id's add `+self.name` to ensure they are unique in every layout
    - `self.name` gets assigned a uuid random string of length 10 by `super().__init__()`.
- Note that the callbacks are registered using `_register_callbacks(self, app)` (**note the underscore!**)
- Note that the callback uses the `plot_factory` for the plotting logic.

```python
class CovidTimeSeries(DashComponent):
    def __init__(self, plot_factory, 
                 hide_country_dropdown=False, countries=None, 
                 hide_metric_dropdown=False, metric='cases', name=None):
        super().__init__()
        
        if not self.countries:
            self.countries = self.plot_factory.countries
        
    def layout(self, params=None):
        return dbc.Container([
            dbc.Row([
                dbc.Col([
                    html.H3("Covid Time Series"),
                    self.make_hideable(
                        self.querystring(params)(dcc.Dropdown)(
                            id='timeseries-metric-dropdown-'+self.name,
                            options=[{'label': metric, 'value': metric} for metric in ['cases', 'deaths']],
                            value=self.metric,
                        ), hide=self.hide_metric_dropdown),
                    self.make_hideable(
                        self.querystring(params)(dcc.Dropdown)(
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
            if countries and metric is not None:
                return self.plot_factory.plot_time_series(countries, metric)
            raise PreventUpdate
```

### DuoPlots: a composition of two subcomponents
A composite `DashComponent` that combines two `CovidTimeSeries` into a single layout. 
Both subcomponents are passed the same `plot_factory` but assigned different initial values.

- The layouts of subcomponents can be included in the composite layout with 
    `self.plot_left.layout(params)` and `self.plot_right.layout(params)`
- Composite callbacks should again be defined under `self._register_callbacks(app)` (**note the underscore!**)
    - calling `.register_callbacks(app)` first registers all callbacks of subcomponents, 
        and then calls `_register_callbacks(app)`.
    - composite callbacks can access elements of subcomponents by using the `subcomponent.name` fields in the ids.
- When tracking the state of the dashboard in the querystring it is important to name your components, so that 
    the next time you start the dashboard the elements will have the same id's. In this case we 
    pass `name="left"` and `name="right"`.
- Make sure to pass the params parameter of the layout down to the subcomponent layouts!

```python
class DuoPlots(DashComponent):
    def __init__(self, plot_factory):
        super().__init__()
        self.plot_left = CovidTimeSeries(plot_factory, 
                                         countries=['China', 'Vietnam', 'Taiwan'], 
                                         metric='cases', name='left')
        self.plot_right = CovidTimeSeries(plot_factory, 
                                          countries=['Italy', 'Germany', 'Sweden'], 
                                          metric='deaths', name='right')
        
    def layout(self, params=None):
        return dbc.Container([
            dbc.Row([
                dbc.Col([
                    self.plot_left.layout(params)
                ]),
                dbc.Col([
                    self.plot_right.layout(params)
                ])
            ])
        ], fluid=True)
    
dashboard = DuoPlots(figure_factory)
print(dashboard.to_yaml())
```

    dash_component:
      class_name: DuoPlots
      module: __main__
      params:
        plot_factory:
          dash_figure_factory:
            class_name: CovidPlots
            module: __main__
            params:
              datafile: covid.csv
        name: 7HmT3rgLrM
    


### Build and start `DashApp`:

Pass the `dashboard` to the `DashApp` to create a dash flask application.

- You can pass `mode='inline'`, `'external'` or `'jupyterlab'` when you are working in a notebook in order to keep
    the notebook interactive while the app is running
- By passing `querystrings=True` you automatically keep track of the state of the dashboard int the url querystring
- You can pass a `port` and any other dash parameters in the `**kwargs` (e.g. here we include the bootstrap css from `dash_bootstrap_components`)

```python
app = DashApp(dashboard, querystrings=True, external_stylesheets=[dbc.themes.BOOTSTRAP])
print(app.to_yaml())
```

    dash_app:
      class_name: DashApp
      module: dash_oop_components.core
      params:
        dashboard_component:
          dash_component:
            class_name: DuoPlots
            module: __main__
            params:
              plot_factory:
                dash_figure_factory:
                  class_name: CovidPlots
                  module: __main__
                  params:
                    datafile: covid.csv
              name: 7HmT3rgLrM
        port: 8050
        mode: dash
        querystrings: true
        kwargs:
          external_stylesheets:
          - https://stackpath.bootstrapcdn.com/bootstrap/4.5.0/css/bootstrap.min.css
          suppress_callback_exceptions: true
    


```python
if run_app:
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
      class_name: DashApp
      module: dash_oop_components.core
      params:
        dashboard_component:
          dash_component:
            class_name: DuoPlots
            module: __main__
            params:
              plot_factory:
                dash_figure_factory:
                  class_name: CovidPlots
                  module: __main__
                  params:
                    datafile: covid.csv
              name: 69CtSVuHee
        port: 8050
        mode: dash
        querystrings: true
        kwargs:
          external_stylesheets:
          - https://stackpath.bootstrapcdn.com/bootstrap/4.5.0/css/bootstrap.min.css
          suppress_callback_exceptions: true
    


And if we run it it still works!


```python
if run_app: 
    app2.run()
```
