from decimal import Decimal, ROUND_HALF_UP
def amount(text):
 value=Decimal(text)
 if value<0:raise ValueError('negative wholesale charge')
 return int((value*100).quantize(Decimal('1'),rounding=ROUND_HALF_UP))
