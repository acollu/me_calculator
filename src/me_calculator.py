import inspect
from math import exp, log
import matplotlib.pyplot as plt

# Some parameters that are not settable:
mortgage_payment_range_max = 100000.     # in dollars
mortgage_duration_range_max = 30.        # in years
mortgage_principal_range_max = 1500000.  # in dollars
mortgage_interest_rate_range_max = 0.2   # as a fraction of principal


class me_calculator:
    def __init__(self, mortgage_payment, mortgage_duration, mortgage_principal, mortgage_interest_rate, escrow_rate):
        self.mortgage_parameters = {"mortgage_payment": [mortgage_payment, mortgage_payment_range_max, " [$]"],
                                    "mortgage_duration": [mortgage_duration, mortgage_duration_range_max, " [years]"],
                                    "mortgage_principal": [mortgage_principal, mortgage_principal_range_max, " [$]"],
                                    "mortgage_interest_rate": [mortgage_interest_rate, mortgage_interest_rate_range_max, " [fraction of principal]"]}
        self.mortgage_plottables = {"mortgage_payment": [" [$]"],
                                    "mortgage_duration": [" [years]"],
                                    "mortgage_principal": [" [$]"],
                                    "mortgage_interest_rate": [" [fraction of principal]"],
                                    "mortgage_total_interest": [" [$]"]}
        self.functions = me_calculator_functions(escrow_rate)

    def plot_1d(self, x_parameter, y_plottable):
        if not isinstance(x_parameter, str) or not isinstance(y_plottable, str):
            raise TypeError
        if (x_parameter not in self.mortgage_parameters) or (y_plottable not in self.mortgage_plottables):
            raise KeyError

        plottable_function = getattr(self.functions, y_plottable)
        parameters = inspect.getfullargspec(plottable_function).args[1:]
        x_parameter_index = parameters.index(x_parameter)
        parameter_values = [self.mortgage_parameters[parameter][0] for parameter in parameters]
        x = []
        y = []
        for x_parameter_step in range(1, 1000):
            x_parameter_value = x_parameter_step * self.mortgage_parameters[x_parameter][1] / 1000.
            parameter_values[x_parameter_index] = x_parameter_value
            plottable = 0.
            try:
                plottable = getattr(self.functions, y_plottable)(*parameter_values)
            except ValueError:
                continue
            x.append(x_parameter_value)
            y.append(plottable)
        plt.plot(x, y, lw=1.5, color='red')
        plt.xlabel(x_parameter + self.mortgage_parameters[x_parameter][2], labelpad=8)
        plt.xticks(fontsize=8)
        plt.ylabel(y_plottable + self.mortgage_plottables[y_plottable][0], labelpad=8)
        plt.yticks(fontsize=8)
        plt.grid()
        plt.show()

class me_calculator_functions:
    def __init__(self, escrow_rate=None):
        self.escrow_rate = escrow_rate
        self.include_escrow_expenses = self.escrow_rate is not None

    def mortgage_payment(self, mortgage_duration, mortgage_principal, mortgage_interest_rate):
        escrow_expenses = self.escrow_rate * mortgage_principal if self.include_escrow_expenses else 0.
        return mortgage_interest_rate * mortgage_principal * exp(mortgage_interest_rate * mortgage_duration) / (exp(mortgage_interest_rate * mortgage_duration) - 1.) + escrow_expenses

    def mortgage_principal(self, mortgage_payment, mortgage_duration, mortgage_interest_rate):
        escrow_rate = self.escrow_rate if self.include_escrow_expenses else 0.
        print(mortgage_payment, mortgage_duration, mortgage_interest_rate)
        return mortgage_payment * (1. - exp(-1 * mortgage_interest_rate * mortgage_duration)) / (mortgage_interest_rate + escrow_rate * (1. - exp(-1 * mortgage_interest_rate * mortgage_duration)))

    def mortgage_interest_rate(self, mortgage_payment, mortgage_duration, mortgage_principal):
        escrow_expenses = self.escrow_rate * mortgage_principal if self.include_escrow_expenses else 0.
        corrected_payment = mortgage_payment - escrow_expenses
        for interest_step in range(1, 20000):
            interest = interest_step * 0.001
            if exp(interest * mortgage_duration) - (corrected_payment / (corrected_payment - interest * mortgage_principal)) < 0.:
                return interest

    def mortgage_duration(self, mortgage_payment, mortgage_principal, mortgage_interest_rate):
        escrow_expenses = self.escrow_rate * mortgage_principal if self.include_escrow_expenses else 0.
        corrected_payment = mortgage_payment - escrow_expenses
        return (1. / mortgage_interest_rate) * log(corrected_payment / (corrected_payment - mortgage_interest_rate * mortgage_principal))

    def mortgage_total_interest(self, mortgage_payment, mortgage_principal, mortgage_interest_rate):
        escrow_expenses = self.escrow_rate * mortgage_principal if self.include_escrow_expenses else 0.
        corrected_payment = mortgage_payment - escrow_expenses
        return (corrected_payment / mortgage_interest_rate) * log(corrected_payment / (corrected_payment - mortgage_interest_rate * mortgage_principal)) - mortgage_principal


calculator = me_calculator(mortgage_payment=50000.,
                           mortgage_duration=15.,
                           mortgage_principal=750000.,
                           mortgage_interest_rate=0.05,
                           escrow_rate=0.015)
calculator.plot_1d(x_parameter="mortgage_interest_rate", y_plottable="mortgage_payment")
