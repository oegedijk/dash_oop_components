# Release Notes

## Version 0.0.7:
### Breaking Changes
- 
- 

### New Features
-
-

### Bug Fixes
-
-

### Improvements
-
-

### Other Changes
-
-


## Version 0.0.6:
### Breaking Changes
- 
- 

### New Features
- If you add a parameter `filepath` to your `DashFigureFactory` you can `.dump()` without specifying a filepath as it defaults to the filepath  parameter.
    - If that `DashFigureFactory` is parameter for a `DashComponent` (or`DashApp`), you can 
    then load the pickled object instead of rebuilding the `DashFigureFactory` from scratch. 
    This is useful for when you have a computationally expensive build process
    for your `DashFigureFactory`. You can indicate that you would like 
    to try to load from pickles or only wish to load from pickles by 
    passing `try_pickles=True` or `force_pickles=True` when loading from config:
     ```python
     DashApp.from_yaml("dashboard.yaml", try_pickles=True)`
     ```
- `DashComponentTabs`: generate a `dcc.Tabs` wrapper with a list of `dcc.Tab` children based on a list of `DashComponent` subcomponents.
    - This allows `dash_oop_components` to keep track of which querystring parameters belong to which tab in `._tab_params`.
    - So this `DashApp` the possibility  only keeping track of querystring parameters of the specific tab that you are currently on.
    - Documentation [here](https://oegedijk.github.io/dash_oop_components/querystrings.html#Addendum:-Tracking-querystring-params-of-current-tab-only) and [here](https://oegedijk.github.io/dash_oop_components/querystrings.html#Addendum:-Tracking-querystring-params-of-current-tab-only)
- `DashConnector`: a `Connector` can generate callbacks between 
    `DashComponent` instances. This makes connections between components
    also modular and re-usable.
    - Documentation [here](https://oegedijk.github.io/dash_oop_components/core.html#DashConnector)

### Bug Fixes
- Cleaned up querystring code
-

### Improvements
- 
-

### Other Changes
- `DashApp` now ta
-


## Template:
### Breaking Changes
- 
- 

### New Features
-
-

### Bug Fixes
-
-

### Improvements
-
-

### Other Changes
-
-