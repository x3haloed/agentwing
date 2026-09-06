from decimal import Decimal
import money
def amount(text):
 if Decimal(text)<0:raise ValueError('negative wholesale charge')
 return money.to_cents(text)
