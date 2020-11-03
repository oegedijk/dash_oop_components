# Release Notes

## Version 0.6:
### Breaking Changes
- 
- 

### New Features
- try_pickles and force_pickles
- `DashComponentTabs`: generate a `dcc.Tabs` wrapper with a list of `dcc.Tab` children based on a list of `DashComponent` subcomponents.
    - This allows `dash_oop_components` to keep track of which querystring parameters belong to which tab in `._tab_params`.
    - So this `DashApp` the possibility  only keeping track of querystring parameters of the specific tab that you are currently on.
- `DashConnector`: a `Connector` can generate callbacks between 
    `DashComponent` instances. This makes connections between components
    also modular and re-usable.

### Bug Fixes
- Cleaned up querystring code
-

### Improvements
- Rewr
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