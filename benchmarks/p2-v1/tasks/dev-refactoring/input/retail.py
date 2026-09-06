from decimal import Decimal, ROUND_HALF_UP
def amount(text):
 return int((Decimal(text)*100).quantize(Decimal('1'),rounding=ROUND_HALF_UP))
