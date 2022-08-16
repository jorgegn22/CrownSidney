import datetime
from datetime import datetime, timedelta
a = 1
b= 1.0
c= 'test'
d= datetime.strptime('2022-05-16', '%Y-%m-%d')
e = datetime.strptime('2022-05-18', '%Y-%m-%d')
if type(d) == int:
    print(f'Entero: {d}')
elif type(d) == float:
    print(f'Float: {d}')
elif type(d) == str:
    print(f'String: {d}')
elif type(d) == datetime:
    print(f'Datetime: {d}')
else:
    print(type(d))
    
print(type((e-d).days))