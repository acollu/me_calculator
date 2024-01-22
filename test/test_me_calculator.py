import unittest

from me_calculator.me_calculator import MeCalculatorFunctions

class TestMeCalculatorFunctions(unittest.TestCase):
    def setUp(self):
        self.functions = MeCalculatorFunctions(cost_per_point=0.01,
                                               discount_per_point=0.0025,
                                               closing_costs=0.,
                                               escrow_rate=0.02,
                                               property_value_growth_rate=0.05,
                                               pmi_insurance=0.000075,
                                               price_to_rent_ratio=20.,
                                               market_rate_of_return=0.06)

    def test_mortgage_payment(self):
        downpayment = 0.1
        mortgage_principal = 900000.
        mortgage_duration = 30
        mortgage_interest_rate = 0.03
        expected_mortgage_payment = 0.
        payment_min = 0.
        payment_max = 100000.
        principal_paid = 0.
        home_price = mortgage_principal / (1. - downpayment)
        principal = mortgage_principal
        while abs(principal_paid - mortgage_principal) > 0.1: 
            if principal_paid < mortgage_principal:
                payment_min = expected_mortgage_payment 
            else: 
                payment_max = expected_mortgage_payment
            paid = 0.
            principal = mortgage_principal
            principal_paid = 0.
            expected_mortgage_payment = (payment_min + payment_max) / 2.
            for i in range(1, mortgage_duration + 1):
                paid = expected_mortgage_payment - principal * mortgage_interest_rate
                principal -= paid
                principal_paid += paid
        expected_mortgage_payment += self.functions.escrow_rate * home_price
        mortgage_payment = self.functions.mortgage_payment(downpayment, mortgage_duration, mortgage_principal, mortgage_interest_rate)
        self.assertAlmostEqual(mortgage_payment, expected_mortgage_payment, 0)

    def test_mortgage_principal(self):
        downpayment = 0.2
        mortgage_payment = 80000.
        mortgage_duration = 30
        mortgage_interest_rate = 0.03
        principal_min = 0.
        principal_max = 3000000.
        expected_principal = 0.
        principal_residual = -1.
        while abs(principal_residual) > 0.1: 
            if principal_residual < 0.:
                principal_min = expected_principal 
            else:
                principal_max = expected_principal 
            expected_principal = (principal_min + principal_max) / 2.
            home_price = expected_principal / (1. - downpayment)
            principal_residual = expected_principal
            for i in range(1, mortgage_duration + 1):
                paid = mortgage_payment - principal_residual * mortgage_interest_rate - home_price * self.functions.escrow_rate
                principal_residual -= paid
                if principal_residual < 0. and i < mortgage_duration:
                    principal_residual = -1. 
                    break
        mortgage_principal = self.functions.mortgage_principal(downpayment, mortgage_payment, mortgage_duration, mortgage_interest_rate)
        self.assertAlmostEqual(mortgage_principal, expected_principal, 0)

    def test_mortgage_interest_rate(self):
        downpayment = 0.2
        mortgage_payment = 80000.
        mortgage_duration = 26.5
        mortgage_principal = 1000000.
        mortgage_interest_rate = self.functions.mortgage_interest_rate(downpayment, mortgage_payment, mortgage_duration, mortgage_principal) 
        interest_rate = 0.03
        self.assertAlmostEqual(mortgage_interest_rate, interest_rate, 5)

    def test_mortgage_duration(self):
        downpayment = 0.2
        mortgage_payment = 80000.
        mortgage_interest_rate = 0.03
        mortgage_principal = 1000000.
        residual = mortgage_principal
        home_price = mortgage_principal / (1. - downpayment)
        duration = 0
        while residual > 0:
            residual -= mortgage_payment - residual * mortgage_interest_rate - self.functions.escrow_rate * home_price
            duration += 1
        mortgage_duration = self.functions.mortgage_duration(downpayment, mortgage_payment, mortgage_principal, mortgage_interest_rate) 
        self.assertAlmostEqual(mortgage_duration, duration, 0)

    def test_mortgage_interest(self):
        downpayment = 0.2
        mortgage_payment = 80000.
        mortgage_principal = 1106157.
        mortgage_interest_rate = 0.03
        home_price = mortgage_principal / (1. - downpayment)
        corrected_mortgage_payment = mortgage_payment - self.functions.escrow_rate * home_price 
        interest = 0.
        residual = mortgage_principal
        while residual > 0.:
            interest += residual * mortgage_interest_rate
            residual -= corrected_mortgage_payment - residual * mortgage_interest_rate
        mortgage_interest = self.functions.mortgage_interest(downpayment, mortgage_payment, mortgage_principal, mortgage_interest_rate) 
        self.assertAlmostEqual(mortgage_interest, interest, 0)

    def test_property_value(self):
        downpayment = 0.1
        mortgage_principal = 900000.
        property_value_growth_rate = 0.1
        time = 10.
        property_value = self.functions.property_value(downpayment, mortgage_principal, property_value_growth_rate, time)
        self.assertAlmostEqual(property_value, 2593742.46, 2)

if __name__ == '__main__':
    unittest.main()
