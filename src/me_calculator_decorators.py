import inspect
from .me_calculator_errors import UnknownParameter, UnknownPlottable, PlottableNotDependentOnParameter


def argument_checker(func):
    def wrapper(self, *args):
        argument_names = inspect.getfullargspec(func).args[1:]
        for i, argument_name in enumerate(argument_names):
            if argument_name == "x_parameter":
                _check_parameter(self, args[i])
            if argument_name == "y_parameter":
                _check_parameter(self, args[i])
            if argument_name == "y_plottable":
                if "x_parameter" not in argument_names:
                    raise KeyError
                _check_plottable(self, args[argument_names.index("x_parameter")], args[i])
            if argument_name == "z_plottable":
                if "x_parameter" not in argument_names or "y_parameter" not in argument_names:
                    raise KeyError
                _check_plottable(self, args[argument_names.index("x_parameter")], args[i])
                _check_plottable(self, args[argument_names.index("y_parameter")], args[i])
            if argument_name == "y_plottables":
                if "x_parameter" not in argument_names:
                    raise KeyError
                _check_plottables(self, args[argument_names.index("x_parameter")], args[i])
        return func(self, *args)
    return wrapper


def _check_parameter(self, parameter):
    if parameter not in self.mortgage_parameters:
        raise UnknownParameter


def _check_plottable(self, parameter, plottable):
    if plottable not in self.mortgage_plottables:
        raise UnknownPlottable
    argument_names = inspect.getfullargspec(getattr(self.functions, plottable)).args[1:]
    if parameter not in argument_names:
        raise PlottableNotDependentOnParameter


def _check_plottables(self, parameter, plottables):
    if not isinstance(plottables, list):
        raise TypeError
    for plottable in plottables:
        _check_plottable(self, parameter, plottable)
