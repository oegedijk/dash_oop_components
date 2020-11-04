Other new features include:

- New `DashConnector` component for writing re-usable callback connectors between `DashComponents`:
  - ```python
    class DropdownConnector(DashConnector):
        """Connects the country and metric dropdown menus of a
        CovidComposite with the dropdowns of a CovidTimeSeries 
        and CovidPieChart respectively"""
        def __init__(self, composite, timeseries, piechart):
            super().__init__()
        
        def _register_callbacks(self, app):
            @app.callback(
                Output('timeseries-country-dropdown-'+self.timeseries.name, 'value'),
                Output('piechart-country-dropdown-'+self.piechart.name, 'value'),
                Input('dashboard-country-dropdown-'+self.composite.name, 'value'),
            )
            def update_timeseries_plot(countries):
                return countries, countries
        
            @app.callback(
                Output('timeseries-metric-dropdown-'+self.timeseries.name, 'value'),
                Output('piechart-metric-dropdown-'+self.piechart.name, 'value'),
                Input('dashboard-metric-dropdown-'+self.composite.name, 'value'),
            )
            def update_timeseries_plot(metric):
                return metric, metric
    ```


- When you pass `filepath` as an argument to a `DashFigureFactory` your can pickle it with `.dump()` it, and then have a DashComponent automatically reload it from the pickle file instead of the configuration by passing `try_pickles=True`:

  - ```python
    plot_factory = CovidPlots(datafile="covid.csv", filepath="plot_factory.pkl")
    plot_factory.dump()
    dashboard = CovidDashboard(plot_factory)
    app = DashApp(dashboard, querystrings=True, external_stylesheets=[FLATLY])
    app.to_yaml("dashboard.yaml")

    app2 = DashApp.from_yaml("dashboard.yaml", try_pickles=True)
    ```