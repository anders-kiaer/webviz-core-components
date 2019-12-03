import copy
import inspect

import dash_core_components as dcc


# dash-core-components provide their own plotly javascript bundle,
# which is not needed since webviz-core-components does the same
# (however a smaller plotly bundle without the `eval` function)
#
# The whole webviz_core_components.Graph component is only necessary as
# long as https://github.com/plotly/dash-core-components/issues/462 is
# open. When that is closed, changing default plotly variables can be
# done purely in Python by inheriting from `dcc.Graph`.

dcc._js_dist = [
    js for js in dcc._js_dist if not js["relative_package_path"].startswith("plotly-")
]


class Graph(dcc.Graph):
    def __init__(self, *args, plotly_layout=None, **kwargs):

        config_input = Graph.get_input_value(args, kwargs, "config")
        Graph.change_arguments(args, kwargs, "config",Graph.populate_config(config_input))

        if plotly_layout is not None:
            figure_input = copy.deepcopy(Graph.get_input_value(args, kwargs, "figure"))

            if "layout" not in figure_input:
                figure_input["layout"] = {}

            figure_input["layout"].update(plotly_layout)
            Graph.change_arguments(args, kwargs, "figure", figure_input)

        super().__init__(*args, **kwargs)

    @staticmethod
    def get_input_value(args, kwargs, argument_name):
        arg_index = inspect.getfullargspec(dcc.Graph).args.index(argument_name)

        if len(args) > arg_index:  # config given as positional argument
            return args[arg_index]
        elif argument_name in kwargs:  # config given as keyword argument
            return kwargs[argument_name]
        else:
            return None

    @staticmethod
    def change_arguments(args, kwargs, argument_name, new_value):
        arg_index = inspect.getfullargspec(dcc.Graph).args.index(argument_name)

        if len(args) > arg_index:  # config given as positional argument
            args = (
                args[:arg_index]
                + (new_value,)
                + args[arg_index + 1 :]
            )

        elif argument_name in kwargs:  # config given as keyword argument
            kwargs[argument_name] = new_value

        else:  # config not given - give with only default values
            kwargs[argument_name] = new_value

    @staticmethod
    def populate_config(input_config=None):
        """Populates an optionally given plotly config with default values
        """

        if input_config is None:
            config = {}
        else:
            config = copy.deepcopy(input_config)

        if "modeBarButtonsToRemove" not in config:
            config["modeBarButtonsToRemove"] = ["sendDataToCloud", "toImage"]

        if "displaylogo" not in config:
            config["displaylogo"] = False

        if "responsive" not in config:
            config["responsive"] = True

        return config
