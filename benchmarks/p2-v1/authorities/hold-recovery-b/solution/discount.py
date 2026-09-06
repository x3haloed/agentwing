def apply(cents,percent):
 if type(cents) is not int or type(percent) is not int or cents<0 or not 0<=percent<=100:raise ValueError('invalid')
 return (cents*(100-percent)+50)//100
