import bitmath
a = bitmath.parse_string('10Gib')
b = bitmath.parse_string('912Mib')
print(a+b)
print(type(a+b))
print(int(a+b))
b > a
a > b