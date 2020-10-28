# AUTOGENERATED! DO NOT EDIT! File to edit: 00_core.ipynb (unless otherwise specified).

__all__ = ['DashComponentBase', 'DashFigureFactory', 'DashComponent', 'concat_docstring', 'parse_url_to_params',
           'parse_url_to_qs_and_vals', 'encode_querystring_params_to_url', 'update_url_with_new_params', 'DashApp']

# Cell

import sys
from abc import ABC
import inspect
import types
from importlib import import_module

import shortuuid
import oyaml as yaml
from urllib.parse import urlparse, parse_qs, urlencode
import ast

import dash
import jupyter_dash

import dash_bootstrap_components as dbc

# Cell
import dash_core_components as dcc
import dash_html_components as html

from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate

# Cell
class DashComponentBase(ABC):
    """Base class for all dash_oop_components classes.

    Stores parameter of child classes to attributes and ._stored_params.
    Proved .to_config(), to_yaml(), .from_config() and .from_yaml() methods
    """
    def __init__(self, no_store=None, no_attr=None, no_config=None, child_depth=3):
        """
        Args:
            no_store {list, bool}: either a list of parameters not to store or True, in which
                case no parameters gets stored.
            no_attr {list, bool}: either a list of parameter not to assign to attribute or True,
                in which case no parameters get assigned to attributes
            no_config {list, bool}: either a list of parameter not to store to ._stored_params
                or True, in which case no parameters get saved to ._stored_params
            child_depth (int): how deep the child is from which parameters will be read.
                Defaults to 3 (i.e. The child of the child of DashComponentBase)
        """
        self._store_child_params(no_store, no_attr, no_config, child_depth)

    def _store_child_params(self, no_store=None, no_attr=None, no_config=None, child_depth=3):
        """
        Args:
            no_store {list, bool}: either a list of parameters not to store or True, in which
                case no parameters gets stored.
            no_attr {list, bool}: either a list of parameter not to assign to attribute or True,
                in which case no parameters get assigned to attributes
            no_config {list, bool}: either a list of parameter not to store to ._stored_params
                or True, in which case no parameters get saved to ._stored_params
            child_depth (int): how deep the child is from which parameters will be read.
                Defaults to 3 (i.e. The child of the child of DashComponentBase)
        """

        if not hasattr(self, '_stored_params'):
            self._stored_params = {}

        child_frame = sys._getframe(child_depth)
        child_args = child_frame.f_code.co_varnames[1:child_frame.f_code.co_argcount]
        child_dict = {arg: child_frame.f_locals[arg] for arg in child_args}
        if 'kwargs' in child_frame.f_locals:
            child_dict['kwargs'] = child_frame.f_locals['kwargs']

        if isinstance(no_store, bool) and no_store:
            return
        else:
            if no_store is None: no_store = tuple()

        if isinstance(no_attr, bool) and no_attr: dont_attr = True
        else:
            if no_attr is None: no_attr = tuple()
            dont_attr = False

        if isinstance(no_config, bool) and no_param: dont_config = True
        else:
            if no_config is None: no_config= tuple()
            dont_config = False

        for name, value in child_dict.items():
            if name in {'dash_component', 'dash_figure_factory', 'dash_app'}:
                raise ValueError(f"Please do not use {name} as a parameter name, "
                                 "as this results in a confusing and hard to parse config.")
            if not dont_attr and name not in no_store and name not in no_attr:
                setattr(self, name, value)
            if not dont_config and name not in no_store and name not in no_config:
                self._stored_params[name] = value

    def to_config(self):
        """
        returns a dict with class name, module and params
        """
        return dict(dash_component=dict(
            class_name=self.__class__.__name__,
            module=self.__class__.__module__,
            params=self._stored_params))

    def to_yaml(self, filepath=None):
        """
        stores a yaml configuration to disk.

        If no filepath is given, returns a str of the yaml config.
        """
        yaml_config = self.to_config()
        if filepath is not None:
            yaml.dump(yaml_config, open(filepath, "w"))
            return
        return yaml.dump(yaml_config)

    def dump(self, filepath=None):
        """store the object to disk.

        Default serializer is pickle, however depending on file suffix,
        dill or joblib will be used."""
        filepath = str(filepath)
        if filepath.endswith(".pkl") or filepath.endswith(".pickle"):
            import pickle
            pickle.dump(self, open(filepath, "wb"))
        elif filepath.endswith(".dill"):
            import dill
            dill.dump(self, open(filepath, "wb"))
        elif str(filepath).endswith(".joblib"):
            import joblib
            joblib.dump(self, filepath)
        else:
            filepath = filepath + ".pkl"
            import pickle
            pickle.dump(self, open(filepath, "wb"))

    @classmethod
    def from_config(cls, config, **update_params):
        """
        Loads a dash_oop_component class from a configuration dict.

        Args:
            config (dict): configuration dict, generated from .to_config()
            update_params: a dict of parameters to be overridden by update_params

        Returns:
            Instance of the class defined in the config.
        """
        if 'dash_component' in config:
            config = config['dash_component']
        elif 'dash_figure_factory' in config:
            config = config['dash_figure_factory']
        elif 'dash_app' in config:
            config = config['dash_app']
        else:
            raise ValueError("I only know how to build dash_component, "
                             "dash_figure_factory and dash_app from config!", str(config))

        params = config['params']
        if not params: params = {}

        for k, v in update_params.items():
            if k in params:
                params[k] = v
            elif 'kwargs' in params:
                params['kwargs'][k]=v
            else:
                raise ValueError(f"This dash_oop_component does not take {k} as an argument, "
                                "nor does it take **kwargs!")

        for k, v in params.items():
            if isinstance(v, dict) and ('dash_figure_factory' in v or 'dash_component' in v):
                params[k] = DashComponentBase.from_config(v)

        component_class = getattr(import_module(config['module']), config['class_name'])
        if 'kwargs' in params:
            kwargs = params.pop('kwargs')
        else:
            kwargs = {}

        if "name" in params:
            name = params.pop('name')
        else:
            name = None

        comp = component_class(**params, **kwargs)
        if name is not None:
            comp.name = name
        return comp

    @classmethod
    def from_yaml(cls, yaml_filepath, **update_params):
        """
        Loads a dash_oop_component class from a yaml file.

        Args:
            yaml_filepath (str, Path): filepath of a .yaml file, generated from .to_yaml()
            update_params: a dict of parameters to be overridden by update_params

        Returns:
            Instance of the class defined in the yaml file.
        """
        config = yaml.safe_load(open(str(yaml_filepath), "r"))
        return cls.from_config(config, **update_params)

    @classmethod
    def from_file(cls, filepath):
        """Load a DashComponentBase from file. Depending on the suffix of the filepath
        will either load with pickle ('.pkl'), dill ('.dill') or joblib ('joblib').

        If no suffix given, will try with pickle (and try adding ''.pkl')

        Args:
            filepath {str, Path} the location of the stored component

        returns:
            DashComponentBase
        """
        filepath = str(filepath)
        if filepath.endswith(".pkl") or str(filepath).endswith(".pickle"):
            import pickle
            return pickle.load(open(filepath, "rb"))
        elif filepath.endswith(".dill"):
            import dill
            return dill.load(open(filepath, "rb"))
        elif filepath.endswith(".joblib"):
            import joblib
            return joblib.load(filepath)
        else:
            from pathlib import Path
            filepath = Path(filepath)
            if not filepath.exists():
                if (filepath.parent / (filepath.name + ".pkl")).exists():
                    filepath = filepath.parent / (filepath.name + ".pkl")
                else:
                    raise ValueError(f"Cannot find file: {str(filepath)}")
            import pickle
            return pickle.load(open(str(filepath), "rb"))


# Cell

class DashFigureFactory(DashComponentBase):
    """
    Helper class to store data for a dashboard and provide e.g. plotting functions.

    You should seperate the datastorage/plotting logic from the dashboard logic.
    All data/plotting logic goes into a DashFigureFactory.

    All dashboard logic goes into a DashComponent.

    Stores to config under key 'dash_figure_factory'
    """
    def __init__(self, no_store=None, no_attr=None, no_config=None):
        super().__init__(no_store=None, no_attr=None, no_config=None)

    def to_config(self):
        return dict(dash_figure_factory=dict(
            class_name=self.__class__.__name__,
            module=self.__class__.__module__,
            params=self._stored_params))



# Cell

class DashComponent(DashComponentBase):
    """DashComponent is a bundle of a dash layout and callbacks that
    can make use of DashFigureFactory objects.

    A DashComponent can have DashComponent subcomponents, that
    you register with register_components().

    DashComponents allow you to:

    1. Write clean, re-usable, composable code for your dashboard
    2. Store your dashboard to config files
    3. Load your dashboard from config files

    Each DashComponent should have a unique .name so that dash id's don't clash.
    If no name is given, DashComponent generates a unique uuid name. This allows
    for multiple instance of the same component type in a single layout.
    But remember to add `+self.name` to all id's.

    Important:
        define your callbacks in `_register_callbacks()` (note underscore!) and
        DashComponent will register callbacks of subcomponents in addition
        to _register_callbacks() when calling register_callbacks()
    """
    def __init__(self, title="Dash", name=None,
                 no_store=None, no_attr=None, no_config=None):
        """initialize the DashComponent

        Args:
            title (str, optional): Title of component. Defaults to "Dash".
            name (str, optional): unique name to add to Component elements.
                        If None then random uuid is generated to make sure
                        it's unique. Defaults to None.
        """
        super().__init__(no_store, no_attr, no_config)
        self._convert_ff_config_params()

        self.title = title
        if not hasattr(self, "name"):
            self.name = name
        if self.name is None:
            self.name = str(shortuuid.ShortUUID().random(length=10))
        self._stored_params["name"] = self.name

        self._components = []
        self._compute_querystring_params(whole_tree=False)

    def _convert_ff_config_params(self):
        """convert any DashFigureFactory in the ._stored_params dict to its config"""
        for k, v in self._stored_params.items():
            if isinstance(v, DashFigureFactory):
                self._stored_params[k] = self._stored_params[k].to_config()

    @staticmethod
    def make_hideable(element, hide=False):
        """helper function to optionally not display an element in a layout.

        Example:
            make_hideable(dbc.Col([cutoff.layout()]), hide=hide_cutoff)

        Args:
            hide(bool): wrap the element inside a hidden html.div. If the element
                        is a dbc.Col or a dbc.FormGroup, wrap element.children in
                        a hidden html.Div instead. Defaults to False.
        """
        if hide:
            if isinstance(element, dbc.Col) or isinstance(element, dbc.FormGroup):
                return html.Div(element.children, style=dict(display="none"))
            else:
                return html.Div(element, style=dict(display="none"))
        else:
            return element

    def querystring(self, params, *attrs):
        """
        wrapper function that applies params loaded from querystrings
        to the underlying dash layout function's attributes attrs. By
        default it only applies to the "value" attribute.

        Use:
            To only track the value attribute:
                self.querystring(params)(dcc.Input)(id="input-"+self.name, value=1)

            To track specific attribute(s):

                self.querystring(params, "value", "min", "max")(dcc.Slider)(id="input-"+self.name)

        if params=='_store_querystring_params':
            stores a list of tuple(id, attribute) to be tracked in the querystring
            to self._querystring_params. All (nested) querystring parameters can
            be accessed with .get_querystring_params()

        """
        def move_value_to_front(attrs):
            """the value attribute gets encoded with a single querystring, e.g. '?param=1'
                    gets parsed as param.value=1.
                All other attributes get encoded with two querystrings,  e.g.
                    '?param=max&param=10' gets parsed as param.max=10.
                Therefore an uneven number of attributes implies that the value attribute
                has been encoded. By always putting value first, we can simply take the
                first querystring param as value, and then parse the rest."""
            if not attrs:
                # if not attributes passed: encode value attribute
                return tuple(['value'])
            if not 'value' in attrs:
                # if 'value' not in attributes then can keep the order as passed
                return attrs
            else:
                # if 'value' in attributes, then make sure it's first in the list:
                attrs_list = list(attrs)
                attrs_list.insert(0, attrs_list.pop(attrs_list.index('value')))
                return tuple(attrs_list)

        if params=="_store_querystring_params":
            attrs = move_value_to_front(attrs)
            def wrapper(func):
                def apply_value(*args, **kwargs):
                    for attr in attrs:
                        self._querystring_params.append(tuple([kwargs['id'], attr]))
                    return func(*args, **kwargs)
                return apply_value
            return wrapper
        if params is None:
            def wrapper(func):
                def apply_value(*args, **kwargs):
                    return func(*args, **kwargs)
                return apply_value
            return wrapper
        else:
            def wrapper(func):
                def apply_value(*args, **kwargs):
                    if 'id' in kwargs and kwargs['id'] in params:
                        param_values = params[kwargs['id']]
                        for pv in param_values:
                            kwargs[pv[0]] = pv[1]
                    return func(*args, **kwargs)
                return apply_value
            return wrapper

    def get_querystring_params(self):
        """
        Returns a list of tuple(id, attribute) of all element attributes
        in all (sub-)components that have been wrapped by self.querystring()
        and should be tracked in the url querystring."""

        _params = []
        _params.extend(self._querystring_params)

        self.register_components()
        for comp in self._components:
            _params.extend(comp.get_querystring_params())
        return _params

    def _clear_querystring_params(self, whole_tree=True):
        """clears the querystring params.

        Args:
            whole_tree (bool): if True, clear all _querystring_prams\
                in all subcomponents."""
        self._querystring_params = []

        if whole_tree:
            self.register_components()
            for comp in self._components:
                comp._clear_querystring_params(whole_tree)

    def _compute_querystring_params(self, whole_tree=True):
        """compute ._querystring_params.

        Args:
            whole_tree (bool): if True, compute all _querystring_prams\
                in all subcomponents."""
        self._querystring_params = []

        try:
            self.layout("_store_querystring_params")
        except:
            pass

        if whole_tree:
            self.register_components()
            for comp in self._components:
                comp._compute_querystring_params(whole_tree)

    def get_unreachable_querystring_params(self):
        """returns all element (id, attr) querystring parameters
        that have a self.querystring() wrapper but because params
        has not been passed correctly down to subcomponents .layout()
        function, will not actually get updated.
        """
        try:
            _ = self.layout(None)
        except:
            return self.get_querystring_params()

        all_params = self.get_querystring_params()

        self._clear_querystring_params(whole_tree=True)
        _ = self.layout("_store_querystring_params")
        reachable_params = self.get_querystring_params()

        unreachable_params = [param for param in all_params if param not in reachable_params]
        self._compute_querystring_params(whole_tree=True)
        return unreachable_params

    def register_components(self):
        """register subcomponents so that their callbacks will be registered

        Searches self.__dict__, finds all DashComponents and adds them to self._components
        """
        if not hasattr(self, '_components'):
            self._components = []
        for k, v in self.__dict__.items():
            if k != '_components' and isinstance(v, DashComponent) and v not in self._components:
                self._components.append(v)

    def layout(self, params=None):
        """layout to be defined by the particular ExplainerComponent instance.
        All element id's should append +self.name to make sure they are unique."""
        return None

    def _register_callbacks(self, app):
        """register callbacks specific to this ExplainerComponent."""
        pass

    def register_callbacks(self, app):
        """First register callbacks of all subcomponents, then call
        _register_callbacks(app)
        """
        self.register_components()
        for comp in self._components:
            comp.register_callbacks(app)
        self._register_callbacks(app)

# Cell

def concat_docstring(source=None):
    "Decorator: `__doc__` from `source` to __doc__"
    def _f(f):
        if isinstance(f, types.FunctionType):
            from_f = f
        else:
            from_f = f.__init__

        if isinstance(source, types.FunctionType):
            source_f = source
        elif source.__init__.__doc__ is not None:
            source_f = source.__init__
        else:
            source_f = source
        from_f.__doc__ = (
            str(from_f.__doc__) + "\n\n\"" +
            f"Docstring from {source.__name__}" +
            "\n\n" +
            str(source_f.__doc__))
        return f
    return _f

# Cell
def parse_url_to_params(url):
    """
    Returns a dict that summarizes the state of the app at the time that the
    querystring url was generated. Lists are (somewhat hackily) detected
    by the first char=='['), get evaluated using ast. Numbers are
    appropriately cast as either int or float.

    Params:
        url (str): url to be parsed. The querystring parameters should
            come in pairs e.g.:?input-id=value&binput-id=1

    Returns:
        dict: dictionary with the component_id as key and a list
            of (param, value) pairs (e.g. {'input-id': [('value', 1)]}
    """

    parse_result = urlparse(url)

    statedict = parse_qs(parse_result.query)
    if statedict:
        for key, values in statedict.items():
            if len(values) % 2 == 0: # even length means no value attr
                new_value = list(map(list, zip(values[0::2], values[1::2])))
                statedict[key] = new_value
            else: # uneven length means value attr is the first element
                new_value = list([['value', values[0]]])
                new_value.extend(list(map(list, zip(values[1::2], values[2::2]))))
                statedict[key] = new_value

            # go through every parsed value pv and check whether it is a list
            # or a number and cast appropriately:
            for pv in statedict[key]:
                # if it's a list
                if isinstance(pv[1], str) and pv[1][0]=='[':
                    pv[1] = ast.literal_eval(pv[1])

                #if it's a number
                if (isinstance(pv[1], str) and
                    pv[1].lstrip('-').replace('.','',1).isdigit()):

                    if pv[1].isdigit():
                        pv[1] = int(pv[1])
                    else:
                        pv[1] = float(pv[1])
    else: #return empty dict
        statedict = dict()
    return statedict

# Cell
def parse_url_to_qs_and_vals(url):
    """
    Returns a dict that summarizes the state of the app at the time that the
    querystring url was generated. Lists are (somewhat hackily) detected
    by the first char=='['), get evaluated using ast. Numbers are
    appropriately cast as either int or float.

    Params:
        url (str): url to be parsed. The querystring parameters should
            come in pairs e.g.:?input-id=value&binput-id=1

    Returns:
        dict: dictionary with the component_id as key and a list
            of (param, value) pairs (e.g. {'input-id': [('value', 1)]}
    """

    parse_result = urlparse(url)

    statedict = parse_qs(parse_result.query)
    qs_params = []
    values = []

    if statedict:
        for key, vals in statedict.items():
            if len(vals) % 2 == 0: # even length means no value attr
                qs_params.extend(list(map(tuple, zip([key]*int(0.5*len(vals)), vals[0::2]))))
                values.extend(vals[1::2])
            else: # uneven length means value attr is the first element
                qs_params.append(tuple([key, "value"]))
                values.append(vals[0])

                qs_params.extend(list(map(tuple, zip([key]*int(0.5*(len(vals)-1)), vals[1::2]))))
                values.extend(vals[2::2])

    for i in range(len(values)):
        if isinstance(values[i], str) and values[i][0]=='[':
            values[i] = ast.literal_eval(values[i])

        #if it's a number
        if (isinstance(values[i], str) and
            values[i].lstrip('-').replace('.','',1).isdigit()):

            if values[i].isdigit():
                values[i] = int(values[i])
            else:
                values[i] = float(values[i])

    return qs_params, values

# Cell
def encode_querystring_params_to_url(querystring_params, values):
    """encodes a list of querystring_params and a list of values to
    a url.

    Params:
        querystring_params (list[tuples]): format e.g.
            [('input-id', 'value'), ('input-id', 'type')]
        values (list): list of values to be encoded, e.g.
            [1, 'number']

    Returns:
        str: url of format ?input-id=value&binput-id=1&input-id=type&binput-id='number'
    """
    statelist = [(id, tuple([val])) if attr=="value" else (id, (attr, val))
                     for (id, attr), val
                         in zip(querystring_params, values) if val is not None]
    params = urlencode(statelist,  doseq=True)
    return f'?{params}'

# Cell
def update_url_with_new_params(old_url, qs_params, vals):
    old_qs_params, old_vals = parse_url_to_qs_and_vals(old_url)
    for qs_param, val in zip(qs_params, vals):
        if qs_param in old_qs_params:
            old_vals[old_qs_params.index(qs_param)] = val
        else:
            old_qs_params.append(qs_param)
            old_vals.append(val)
    return encode_querystring_params_to_url(old_qs_params, old_vals)


# Cell

class DashApp(DashComponentBase):
    """Wrapper class for dash apps. Assigns layout and callbacks from
    a DashComponent to a Dash app, and runs it.

    Can run both Dash and JupyterDash apps.

    """
    @concat_docstring(dash.Dash)
    def __init__(self, dashboard_component, port=8050, mode='dash', querystrings=False, **kwargs):
        """

        Args:
            dashboard_component (DashComponent): component to be run
            port (int): port to run the server
            mode ({'dash', 'external', 'inline', 'jupyterlab'}): type of dash server to start
            querystrings (bool): save state to querystring and load from querystring
            kwargs: all kwargs will be passed down to dash.Dash. See below the docstring of dash.Dash

        Returns:
            DashApp: simply start .run() to start the dashboard
        """
        super().__init__(child_depth=2)
        self._stored_params['dashboard_component'] = dashboard_component.to_config()
        self.app = self._get_dash_app()

    def _get_dash_app(self):
        if self.querystrings:
            self.kwargs["suppress_callback_exceptions"] = True
        if self.mode == 'dash':
            app = dash.Dash(**self.kwargs)
        elif self.mode in {'inline', 'external', 'jupyterlab'}:
            app = jupyter_dash.JupyterDash(**self.kwargs)

        if not self.querystrings:
            app.layout = self.dashboard_component.layout()

        else:
            try:
                self.dashboard_component.layout(None)
            except:
                raise ValueError("The layout method method of dashboard_component does not take "
                                 "a params parameter. Please rewrite as `def layout(self, params=None):` !")

            unreachable_params = self.dashboard_component.get_unreachable_querystring_params()
            if unreachable_params:
                print("Warning: The following elements will be tracked in the querystring, "
                     "but do not get passed as params to the (subcomponent) .layout(params) function, and so "
                      "will not be rebuilt when reloading from the url querystring! Please "
                      "make sure that you pass params down to the layout of all subcomponents! "
                      "e.g. def layout(self, params=None): return html.Div([self.sub_component.layout(params)]) \n\n",
                      unreachable_params)
            app.layout = html.Div([
                        dcc.Location(id='url', refresh=False),
                        html.Div(id='page-layout')
                    ])

            @app.callback(Output('page-layout', 'children'),
                  [Input('url', 'href')])
            def page_load(href):
                if not href:
                    return html.Div()
                params = parse_url_to_params(href)
                return self.dashboard_component.layout(params)

            @app.callback(Output('url', 'search'),
                          [Input(id, param) for (id, param)
                                  in self.dashboard_component.get_querystring_params()],
                         [State('url', 'search')],
                         prevent_initial_call=True
                 )
            def update_url_state(*values):
                old_url = values[-1]
                ctx = dash.callback_context
                params = [tuple(trigger['prop_id'].split('.')) for trigger in ctx.triggered]
                idxs = [self.dashboard_component.get_querystring_params().index(param)
                            for param in params]
                vals = list(map(values.__getitem__, idxs))
                return update_url_with_new_params(old_url, params, vals)

        self.dashboard_component.register_callbacks(app)

        app.title = self.dashboard_component.title
        return app

    def to_config(self):
        return dict(dash_app=dict(
            class_name=self.__class__.__name__,
            module=self.__class__.__module__,
            params=self._stored_params))

    def flask_server(self):
        """returns flask server inside self.app, for building wsgi apps"""
        return self.app.server

    def run(self, port=None):
        """Run the dash app"""
        self.app.run_server(port=port if port is not None else self.port)
