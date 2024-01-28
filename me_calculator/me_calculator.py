# Note: not using PMI insurance for now, which complicates the calculation and it has to be paid only
#       till the lender reaches 20% equity in the property, i.e. considerably inaccurate for downpayment << 20%

import inspect
from math import exp, log
from me_calculator.me_calculator_decorators import argument_checker

from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
from matplotlib import cm
from matplotlib.ticker import LinearLocator, FormatStrFormatter
import numpy as np


# Some parameters that are not settable:
points_min = 0.                          # number (of points that decrease mortgage interest)
downpayment_min = 0.                     # as a fraction of home price 
mortgage_payment_range_min = 30000.      # in dollars
mortgage_duration_range_min = 1.         # in years (>=1)
mortgage_principal_range_min = 100000.   # in dollars
mortgage_interest_rate_range_min = 0.0   # as a fraction of principal
mortgage_interest_range_min = 0.0        # in dollars
property_value_growth_rate_min = 0.0     # as a fraction of home price 
pmi_insurance_min = 0.                   # as a fraction of home price
time_range_min = 0.                      # in years
points_max = 12.                         # number (of points that decrease mortgage interest)
downpayment_max = 0.5                    # as a fraction of home price 
mortgage_payment_range_max = 100000.     # in dollars
mortgage_duration_range_max = 30.        # in years
mortgage_principal_range_max = 1500000.  # in dollars
mortgage_interest_rate_range_max = 0.2   # as a fraction of principal
mortgage_interest_range_max = 1500000.   # in dollars
property_value_growth_rate_max = 0.2     # as a fraction of home price 
pmi_insurance_max = 0.0001               # as a fraction of home price
time_range_max = 30.                     # in years


class MeCalculator:
    def __init__(self, points, cost_per_point, discount_per_point, downpayment, closing_costs, mortgage_payment, mortgage_duration, mortgage_principal,
                 mortgage_interest_rate, escrow_rate, property_value_growth_rate, pmi_insurance, price_to_rent_ratio, market_rate_of_return):
        self.mortgage_parameters = {"points": [points, points_min, points_max, "[number]"],
                                    "downpayment": [downpayment, downpayment_min, downpayment_max, " [fraction of home price]"],
                                    "mortgage_payment": [mortgage_payment, mortgage_payment_range_min, mortgage_payment_range_max, " [$]"],
                                    "mortgage_duration": [mortgage_duration, mortgage_duration_range_min, mortgage_duration_range_max, " [years]"],
                                    "mortgage_principal": [mortgage_principal, mortgage_principal_range_min, mortgage_principal_range_max, " [$]"],
                                    "mortgage_interest_rate": [mortgage_interest_rate, mortgage_interest_rate_range_min, mortgage_interest_rate_range_max, " [fraction of principal]"],
                                    "property_value_growth_rate": [property_value_growth_rate, property_value_growth_rate_min, property_value_growth_rate_max, " [fraction of home price]"],
                                    "pmi_insurance": [pmi_insurance, pmi_insurance_min, pmi_insurance_max, "[fraction of home price]"],
                                    "time": [None, time_range_min, time_range_max, " [years]"]}
        self.mortgage_plottables = {"mortgage_payment": [" [$]"],
                                    "mortgage_duration": [" [years]"],
                                    "mortgage_principal": [" [$]"],
                                    "mortgage_interest_rate": [" [fraction of principal]"],
                                    "mortgage_interest": [" [$]"],
                                    "mortgage_escrow": [" [$]"],
                                    "mortgage": [" [$]"],
                                    "property_value": [" [$]"],
                                    "mortgage_principal_residual": [" [$]"],
                                    "mortgage_principal_paid": [" [$]"],
                                    "mortgage_interest_residual": [" [$]"],
                                    "mortgage_interest_paid": [" [$]"],
                                    "mortgage_escrow_residual": [" [$]"],
                                    "mortgage_escrow_paid": [" [$]"],
                                    "mortgage_residual": [" [$]"],
                                    "mortgage_paid": [" [$]"],
                                    "total_cost": [" [$]"],
                                    "total_cost_residual": [" [$]"],
                                    "total_cost_paid": [" [$]"],
                                    "accrued_costs": [" [$]"],
                                    "home_purchase_total_return": [" [$]"],
                                    "home_purchase_net_return": [" [$]"],
                                    "no_home_purchase_total_return": [" [$]"]}
        self.functions = MeCalculatorFunctions(cost_per_point, discount_per_point, closing_costs, escrow_rate, property_value_growth_rate, pmi_insurance, price_to_rent_ratio, market_rate_of_return)
        self.plot_colors = ['red', 'blue', 'black', 'green', 'cyan', 'orange', 'purple']

    @argument_checker
    def plot_1d(self, x_parameter, y_plottables):
        for i, y_plottable in enumerate(y_plottables):
             selected_function = getattr(self.functions, y_plottable)
             x, y = self.data_1d(selected_function, x_parameter)
             plt.plot(x, y, lw=1.5, color=self.plot_colors[i], label=y_plottable + self.mortgage_plottables[y_plottable][0])
        plt.xlabel(x_parameter + self.mortgage_parameters[x_parameter][3], labelpad=8)
        plt.xticks(fontsize=8)
        plt.yticks(fontsize=8)
        plt.grid()
        plt.legend()
        plt.show()

    def data_1d(self, function, x_parameter):
        parameters = inspect.getfullargspec(function).args[1:]
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
                plottable = function(*parameter_values)
            except ValueError:
                continue
            x.append(x_parameter_value)
            y.append(plottable)
        return x, y

    @argument_checker
    def plot_2d(self, x_parameter, y_parameter, z_plottable):
        plottable_function = getattr(self.functions, z_plottable)
        parameters = inspect.getfullargspec(plottable_function).args[1:]
        x_parameter_index = parameters.index(x_parameter)
        y_parameter_index = parameters.index(y_parameter)
        parameter_values = [self.mortgage_parameters[parameter][0] for parameter in parameters]
        x_parameter_range = self.mortgage_parameters[x_parameter][2] - self.mortgage_parameters[x_parameter][1]
        y_parameter_range = self.mortgage_parameters[y_parameter][2] - self.mortgage_parameters[y_parameter][1]
        x = np.arange(self.mortgage_parameters[x_parameter][1], self.mortgage_parameters[x_parameter][2], x_parameter_range / 1000.)
        y = np.arange(self.mortgage_parameters[y_parameter][1], self.mortgage_parameters[y_parameter][2], y_parameter_range / 1000.)
        x, y = np.meshgrid(x, y)
        z = np.zeros((1000, 1000))
        for i in range(0, 1000):
            for j in range(0, 1000):
                x_parameter_value = x[i][j]
                parameter_values[x_parameter_index] = x_parameter_value
                y_parameter_value = y[i][j]
                parameter_values[y_parameter_index] = y_parameter_value
                plottable = 0.
                try:
                    plottable = getattr(self.functions, z_plottable)(*parameter_values)
                except ValueError:
                    continue
                z[i][j] = plottable

        fig = plt.figure()
        ax = fig.gca(projection='3d')
        surf = ax.plot_surface(x, y, z, linewidth=0, cmap=plt.cm.coolwarm, antialiased=False)
        ax.set_zlim(-1, np.amax(z) + 1)
        fig.colorbar(surf, shrink=0.5, aspect=5)
        plt.xlabel(x_parameter + self.mortgage_parameters[x_parameter][3], labelpad=8)
        plt.xticks(fontsize=7)
        plt.ylabel(y_parameter + self.mortgage_parameters[y_parameter][3], labelpad=8)
        plt.yticks(fontsize=7)
        plt.show()


class MeCalculatorFunctions:
    def __init__(self, cost_per_point=0.01, discount_per_point=0.0025, closing_costs=0.06, escrow_rate=None, property_value_growth_rate=0., pmi_insurance=0.000075, price_to_rent_ratio=20., market_rate_of_return=0.07):
        self.cost_per_point = cost_per_point
        self.discount_per_point = discount_per_point
        self.closing_costs = closing_costs
        self.escrow_rate = escrow_rate
        self.include_escrow_expenses = self.escrow_rate is not None
        self.property_value_growth_rate = property_value_growth_rate
        self.pmi_insurance = pmi_insurance
        self.price_to_rent_ratio = price_to_rent_ratio
        self.market_rate_of_return = market_rate_of_return

    def mortgage_payment(self, downpayment, mortgage_duration, mortgage_principal, mortgage_interest_rate):
        home_price = mortgage_principal / (1. - downpayment)
        escrow_expenses = self.escrow_rate * home_price if self.include_escrow_expenses else 0.
        base = 1. + mortgage_interest_rate
        return mortgage_interest_rate * mortgage_principal * pow(base, mortgage_duration) / (pow(base, mortgage_duration) - 1.) + escrow_expenses

    def mortgage_principal(self, downpayment, mortgage_payment, mortgage_duration, mortgage_interest_rate):
        escrow_rate = self.escrow_rate if self.include_escrow_expenses else 0.
        base = 1. + mortgage_interest_rate
        base_n = pow(base, mortgage_duration)
        a = (base_n - 1.) / mortgage_interest_rate
        b = 1. / (1. - downpayment)
        return mortgage_payment * a / (base_n + b * a * escrow_rate)

    def mortgage_interest_rate(self, downpayment, mortgage_payment, mortgage_duration, mortgage_principal):
        home_price = mortgage_principal / (1. - downpayment)
        escrow_expenses = self.escrow_rate * home_price if self.include_escrow_expenses else 0.
        corrected_payment = mortgage_payment - escrow_expenses
        for interest_step in range(1, 20000):
            interest = interest_step * 0.001
            base = 1. + interest
            base_n = pow(base, mortgage_duration)
            a = (base_n - 1.) / interest
            if mortgage_principal * base_n - corrected_payment * a > 0.:
                return interest

    def mortgage_duration(self, downpayment, mortgage_payment, mortgage_principal, mortgage_interest_rate):
        home_price = mortgage_principal / (1. - downpayment)
        escrow_expenses = self.escrow_rate * home_price if self.include_escrow_expenses else 0.
        corrected_payment = mortgage_payment - escrow_expenses
        return log(corrected_payment / (corrected_payment - mortgage_interest_rate * mortgage_principal)) / log(1. + mortgage_interest_rate)

    def mortgage_interest(self, downpayment, mortgage_payment, mortgage_principal, mortgage_interest_rate):
        home_price = mortgage_principal / (1. - downpayment)
        escrow_expenses = self.escrow_rate * home_price if self.include_escrow_expenses else 0.
        corrected_payment = mortgage_payment - escrow_expenses
        duration = self.mortgage_duration(downpayment, mortgage_payment, mortgage_principal, mortgage_interest_rate)
        return corrected_payment * duration - mortgage_principal 

    def mortgage_escrow(self, downpayment, mortgage_payment, mortgage_principal, mortgage_interest_rate):
        duration = self.mortgage_duration(downpayment, mortgage_payment, mortgage_principal, mortgage_interest_rate)
        home_price = mortgage_principal / (1. - downpayment)
        escrow_expenses = self.escrow_rate * home_price if self.include_escrow_expenses else 0.
        return duration * escrow_expenses

    def mortgage_no_closing(self, downpayment, mortgage_payment, mortgage_principal, mortgage_interest_rate):
        duration = self.mortgage_duration(downpayment, mortgage_payment, mortgage_principal, mortgage_interest_rate)
        return duration * mortgage_payment

    def mortgage_with_closing(self, downpayment, mortgage_payment, mortgage_principal, mortgage_interest_rate):
        return self.closing_costs * mortgage_principal + self.mortgage_no_closing(downpayment, mortgage_payment, mortgage_principal, mortgage_interest_rate)

    def total_cost(self, downpayment, mortgage_payment, mortgage_principal, mortgage_interest_rate):
        home_price = mortgage_principal / (1. - downpayment)
        return downpayment * home_price + self.mortgage_with_closing(downpayment, mortgage_payment, mortgage_principal, mortgage_interest_rate)

    def property_value(self, downpayment, mortgage_principal, property_value_growth_rate, time):
        home_price = mortgage_principal / (1. - downpayment)
        return (downpayment * home_price + mortgage_principal) * pow(1. + property_value_growth_rate, time)

    def mortgage_principal_residual(self, downpayment, mortgage_payment, mortgage_principal, mortgage_interest_rate, time):
        duration = self.mortgage_duration(downpayment, mortgage_payment, mortgage_principal, mortgage_interest_rate)
        if time > duration:
            raise ValueError
        home_price = mortgage_principal / (1. - downpayment)
        escrow_expenses = self.escrow_rate * home_price if self.include_escrow_expenses else 0.
        corrected_payment = mortgage_payment - escrow_expenses
        base = 1. + mortgage_interest_rate
        base_n = pow(base, time)
        return mortgage_principal * base_n - corrected_payment * (base_n - 1.) / mortgage_interest_rate

    def mortgage_principal_paid(self, downpayment, mortgage_payment, mortgage_principal, mortgage_interest_rate, time):
        duration = self.mortgage_duration(downpayment, mortgage_payment, mortgage_principal, mortgage_interest_rate)
        if time > duration:
            raise ValueError
        residual_principal = self.mortgage_principal_residual(downpayment, mortgage_payment, mortgage_principal, mortgage_interest_rate, time)
        return mortgage_principal - residual_principal

    def mortgage_interest_residual(self, downpayment, mortgage_payment, mortgage_principal, mortgage_interest_rate, time):
        duration = self.mortgage_duration(downpayment, mortgage_payment, mortgage_principal, mortgage_interest_rate)
        if time > duration:
            raise ValueError
        residual_principal = self.mortgage_principal_residual(downpayment, mortgage_payment, mortgage_principal, mortgage_interest_rate, time)
        home_price = mortgage_principal / (1. - downpayment)
        escrow_expenses = self.escrow_rate * home_price if self.include_escrow_expenses else 0.
        mortgage_total = duration * (mortgage_payment - escrow_expenses)
        amount_paid_to_date = time * (mortgage_payment - escrow_expenses)
        residual_interest = mortgage_total - amount_paid_to_date - residual_principal
        return residual_interest

    def mortgage_interest_paid(self, downpayment, mortgage_payment, mortgage_principal, mortgage_interest_rate, time):
        interest = self.mortgage_interest(downpayment, mortgage_payment, mortgage_principal, mortgage_interest_rate)
        interest_residual = self.mortgage_interest_residual(downpayment, mortgage_payment, mortgage_principal, mortgage_interest_rate, time)
        return interest - interest_residual 

    def mortgage_escrow_residual(self, downpayment, mortgage_payment, mortgage_principal, mortgage_interest_rate, time):
        duration = self.mortgage_duration(downpayment, mortgage_payment, mortgage_principal, mortgage_interest_rate)
        if time > duration:
            raise ValueError
        home_price = mortgage_principal / (1. - downpayment)
        escrow_expenses = self.escrow_rate * home_price if self.include_escrow_expenses else 0.
        return (duration - time) * escrow_expenses

    def mortgage_escrow_paid(self, downpayment, mortgage_payment, mortgage_principal, mortgage_interest_rate, time):
        duration = self.mortgage_duration(downpayment, mortgage_payment, mortgage_principal, mortgage_interest_rate)
        if time > duration:
            raise ValueError
        home_price = mortgage_principal / (1. - downpayment)
        escrow_expenses = self.escrow_rate * home_price if self.include_escrow_expenses else 0.
        return time * escrow_expenses

    def mortgage_residual(self, downpayment, mortgage_payment, mortgage_principal, mortgage_interest_rate, time):
        duration = self.mortgage_duration(downpayment, mortgage_payment, mortgage_principal, mortgage_interest_rate)
        if time > duration:
            raise ValueError
        return (duration - time) * mortgage_payment

    def mortgage_paid(self, downpayment, mortgage_payment, mortgage_principal, mortgage_interest_rate, time):
        duration = self.mortgage_duration(downpayment, mortgage_payment, mortgage_principal, mortgage_interest_rate)
        if time > duration:
            raise ValueError
        return time * mortgage_payment

    def total_cost_residual(self, downpayment, mortgage_payment, mortgage_principal, mortgage_interest_rate, time):
        duration = self.mortgage_duration(downpayment, mortgage_payment, mortgage_principal, mortgage_interest_rate)
        if time > duration:
            raise ValueError
        return self.total_cost(downpayment, mortgage_payment, mortgage_principal, mortgage_interest_rate) - \
               self.total_cost_paid(downpayment, mortgage_payment, mortgage_principal, mortgage_interest_rate, time)

    def total_cost_paid(self, downpayment, mortgage_payment, mortgage_principal, mortgage_interest_rate, time):
        duration = self.mortgage_duration(downpayment, mortgage_payment, mortgage_principal, mortgage_interest_rate)
        if time > duration:
            raise ValueError
        home_price = mortgage_principal / (1. - downpayment)
        return downpayment * home_price + self.mortgage_with_closing(downpayment, mortgage_payment, mortgage_principal, mortgage_interest_rate)

    def accrued_costs(self, downpayment, mortgage_payment, mortgage_principal, mortgage_interest_rate, time):
        home_price = mortgage_principal / (1. - downpayment)
        return downpayment * home_price + self.closing_costs * home_price + time * mortgage_payment

    def home_purchase_total_return(self, downpayment, mortgage_payment, mortgage_principal, mortgage_interest_rate, time):
        return self.property_value(downpayment, mortgage_principal, self.property_value_growth_rate, time) * (1. - self.closing_costs)

    def home_purchase_net_return(self, downpayment, mortgage_payment, mortgage_principal, mortgage_interest_rate, time):
        return self.home_purchase_total_return(downpayment, mortgage_payment, mortgage_principal, mortgage_interest_rate, time) - \
               self.mortgage_principal_residual(downpayment, mortgage_payment, mortgage_principal, mortgage_interest_rate, time)

    def no_home_purchase_total_return(self, downpayment, mortgage_payment, mortgage_principal, mortgage_interest_rate, time):
        home_price = mortgage_principal / (1. - downpayment)
        rent = self.property_value(0., home_price / self.price_to_rent_ratio, self.property_value_growth_rate, time)
        initial_capital = downpayment * home_price + self.closing_costs * home_price  # Downpayment + closing cost
        yearly_capital_to_invest = mortgage_payment - rent  # Cash available for investment after rent is paid
        base = 1. + self.market_rate_of_return
        base_n = pow(base, time)
        return_from_initial_capital = initial_capital * pow(base, time)
        return_from_yearly_investment = yearly_capital_to_invest * (base / self.market_rate_of_return) * (base_n - 1.)
        return return_from_initial_capital + return_from_yearly_investment 

calculator = MeCalculator(points=0.,
                          cost_per_point=0.01,
                          discount_per_point=0.025,
                          downpayment=0.2,
                          closing_costs=0.06,
                          mortgage_payment=76000,
                          mortgage_duration=30.,
                          mortgage_principal=1200000,
                          mortgage_interest_rate=0.03,
                          escrow_rate=0.02,
                          property_value_growth_rate=0.07,
                          pmi_insurance=0.000075,
                          price_to_rent_ratio=32,
                          market_rate_of_return=0.07)
#calculator.plot_1d("time", ["mortgage_principal_paid", "mortgage_interest_paid", "mortgage_escrow_paid", "mortgage_paid", "accrued_costs", "home_purchase_net_return", "no_home_purchase_total_return"])
#calculator.plot_1d("mortgage_duration", ["mortgage_payment"])
#calculator.plot_2d("mortgage_principal", "time", "mortgage_interest_paid")
