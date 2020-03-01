import inspect
from math import exp, log
import matplotlib.pyplot as plt
from me_calculator_decorators import argument_checker

# Some parameters that are not settable:
mortgage_payment_range_min = 10.         # in dollars
mortgage_duration_range_min = 1.         # in years (>=1)
mortgage_principal_range_min = 1000.     # in dollars
mortgage_interest_rate_range_min = 0.0   # as a fraction of principal
mortgage_interest_range_min = 0.0        # in dollars
time_range_min = 1.                      # in years
mortgage_payment_range_max = 100000.     # in dollars
mortgage_duration_range_max = 30.        # in years
mortgage_principal_range_max = 1500000.  # in dollars
mortgage_interest_rate_range_max = 0.2   # as a fraction of principal
mortgage_interest_range_max = 1500000.   # in dollars
time_range_max = 30.                     # in years


class me_calculator:
    def __init__(self, mortgage_payment, mortgage_duration, mortgage_principal, mortgage_interest_rate, escrow_rate):
        self.mortgage_parameters = {"mortgage_payment": [mortgage_payment, mortgage_payment_range_min, mortgage_payment_range_max, " [$]"],
                                    "mortgage_duration": [mortgage_duration, mortgage_duration_range_min, mortgage_duration_range_max, " [years]"],
                                    "mortgage_principal": [mortgage_principal, mortgage_principal_range_min, mortgage_principal_range_max, " [$]"],
                                    "mortgage_interest_rate": [mortgage_interest_rate, mortgage_interest_rate_range_min, mortgage_interest_rate_range_max, " [fraction of principal]"],
                                    "time": [None, time_range_min, time_range_max, " [years]"]}
        self.mortgage_plottables = {"mortgage_payment": [" [$]"],
                                    "mortgage_duration": [" [years]"],
                                    "mortgage_principal": [" [$]"],
                                    "mortgage_interest_rate": [" [fraction of principal]"],
                                    "mortgage_interest": [" [$]"],
                                    "mortgage_escrow": [" [$]"],
                                    "mortgage": [" [$]"],
                                    "mortgage_principal_residual": [" [$]"],
                                    "mortgage_principal_paid": [" [$]"],
                                    "mortgage_interest_residual": [" [$]"],
                                    "mortgage_interest_paid": [" [$]"],
                                    "mortgage_escrow_residual": [" [$]"],
                                    "mortgage_escrow_paid": [" [$]"],
                                    "mortgage_residual": [" [$]"],
                                    "mortgage_paid": [" [$]"]}
        self.functions = me_calculator_functions(escrow_rate)
        self.plot_colors = ['red', 'blue', 'black', 'green', 'cyan', 'orange']

    @argument_checker
    def plot_1d(self, x_parameter, y_plottables):
        plottable_functions = [getattr(self.functions, y_plottable) for y_plottable in y_plottables]
        for i, y_plottable in enumerate(y_plottables):
            parameters = inspect.getfullargspec(plottable_functions[i]).args[1:]
            x_parameter_index = parameters.index(x_parameter)
            parameter_values = [self.mortgage_parameters[parameter][0] for parameter in parameters]
            x = []
            y = []
            x_parameter_range = self.mortgage_parameters[x_parameter][2] - self.mortgage_parameters[x_parameter][1]
            for x_parameter_step in range(0, 1000):
                x_parameter_value = (x_parameter_step * x_parameter_range / 1000.) + self.mortgage_parameters[x_parameter][1]
                parameter_values[x_parameter_index] = x_parameter_value
                plottable = 0.
                try:
                    plottable = getattr(self.functions, y_plottable)(*parameter_values)
                except ValueError:
                    continue
                x.append(x_parameter_value)
                y.append(plottable)
            plt.plot(x, y, lw=1.5, color=self.plot_colors[i], label=y_plottable + self.mortgage_plottables[y_plottable][0])
        plt.xlabel(x_parameter + self.mortgage_parameters[x_parameter][3], labelpad=8)
        plt.xticks(fontsize=8)
        plt.yticks(fontsize=8)
        plt.grid()
        plt.legend()
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

    def mortgage_interest(self, mortgage_payment, mortgage_principal, mortgage_interest_rate):
        escrow_expenses = self.escrow_rate * mortgage_principal if self.include_escrow_expenses else 0.
        corrected_payment = mortgage_payment - escrow_expenses
        return (corrected_payment / mortgage_interest_rate) * log(corrected_payment / (corrected_payment - mortgage_interest_rate * mortgage_principal)) - mortgage_principal

    def mortgage_escrow(self, mortgage_payment, mortgage_principal, mortgage_interest_rate):
        duration = self.mortgage_duration(mortgage_payment, mortgage_principal, mortgage_interest_rate)
        escrow_expenses = self.escrow_rate * mortgage_principal if self.include_escrow_expenses else 0.
        return duration * escrow_expenses

    def mortgage(self, mortgage_payment, mortgage_principal, mortgage_interest_rate):
        duration = self.mortgage_duration(mortgage_payment, mortgage_principal, mortgage_interest_rate)
        return duration * mortgage_payment

    def mortgage_principal_residual(self, mortgage_payment, mortgage_principal, mortgage_interest_rate, time):
        duration = self.mortgage_duration(mortgage_payment, mortgage_principal, mortgage_interest_rate)
        if time > duration:
            raise ValueError
        escrow_expenses = self.escrow_rate * mortgage_principal if self.include_escrow_expenses else 0.
        corrected_payment = mortgage_payment - escrow_expenses
        return (corrected_payment / mortgage_interest_rate) * (1. - exp(mortgage_interest_rate * time)) + mortgage_principal * exp(mortgage_interest_rate * time)

    def mortgage_principal_paid(self, mortgage_payment, mortgage_principal, mortgage_interest_rate, time):
        duration = self.mortgage_duration(mortgage_payment, mortgage_principal, mortgage_interest_rate)
        if time > duration:
            raise ValueError
        residual_principal = self.mortgage_principal_residual(mortgage_payment, mortgage_principal, mortgage_interest_rate, time)
        return mortgage_principal - residual_principal

    def mortgage_interest_residual(self, mortgage_payment, mortgage_principal, mortgage_interest_rate, time):
        duration = self.mortgage_duration(mortgage_payment, mortgage_principal, mortgage_interest_rate)
        if time > duration:
            raise ValueError
        residual_principal = self.mortgage_principal_residual(mortgage_payment, mortgage_principal, mortgage_interest_rate, time)
        escrow_expenses = self.escrow_rate * mortgage_principal if self.include_escrow_expenses else 0.
        mortgage_total = duration * (mortgage_payment - escrow_expenses)
        amount_paid_to_date = time * (mortgage_payment - escrow_expenses)
        residual_interest = mortgage_total - amount_paid_to_date - residual_principal
        return residual_interest

    def mortgage_interest_paid(self, mortgage_payment, mortgage_principal, mortgage_interest_rate, time):
        duration = self.mortgage_duration(mortgage_payment, mortgage_principal, mortgage_interest_rate)
        if time > duration:
            raise ValueError
        residual_principal = self.mortgage_principal_residual(mortgage_payment, mortgage_principal, mortgage_interest_rate, time)
        escrow_expenses = self.escrow_rate * mortgage_principal if self.include_escrow_expenses else 0.
        amount_paid_to_date = time * (mortgage_payment - escrow_expenses)
        paid_interest = amount_paid_to_date - mortgage_principal + residual_principal
        return paid_interest

    def mortgage_escrow_residual(self, mortgage_payment, mortgage_principal, mortgage_interest_rate, time):
        duration = self.mortgage_duration(mortgage_payment, mortgage_principal, mortgage_interest_rate)
        if time > duration:
            raise ValueError
        escrow_expenses = self.escrow_rate * mortgage_principal if self.include_escrow_expenses else 0.
        return (duration - time) * escrow_expenses

    def mortgage_escrow_paid(self, mortgage_payment, mortgage_principal, mortgage_interest_rate, time):
        duration = self.mortgage_duration(mortgage_payment, mortgage_principal, mortgage_interest_rate)
        if time > duration:
            raise ValueError
        escrow_expenses = self.escrow_rate * mortgage_principal if self.include_escrow_expenses else 0.
        return time * escrow_expenses

    def mortgage_residual(self, mortgage_payment, mortgage_principal, mortgage_interest_rate, time):
        duration = self.mortgage_duration(mortgage_payment, mortgage_principal, mortgage_interest_rate)
        if time > duration:
            raise ValueError
        return (duration - time) * mortgage_payment

    def mortgage_paid(self, mortgage_payment, mortgage_principal, mortgage_interest_rate, time):
        duration = self.mortgage_duration(mortgage_payment, mortgage_principal, mortgage_interest_rate)
        if time > duration:
            raise ValueError
        return time * mortgage_payment

calculator = me_calculator(mortgage_payment=88000.,
                           mortgage_duration=30.,
                           mortgage_principal=600000.,
                           mortgage_interest_rate=0.12,
                           escrow_rate=0.015)
calculator.plot_1d("time", ["mortgage_principal_paid", "mortgage_interest_paid", "mortgage_escrow_paid", "mortgage_paid"])
# calculator.plot_1d("mortgage_duration", ["mortgage_payment"])
