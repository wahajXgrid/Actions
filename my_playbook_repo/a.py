import bitmath as bit
print(bit.GiB(4).to_MiB())

print(bit.parse_string("2KiB"))
print(type(bit.parse_string_unsafe("2KiB")))


# import bitmath
# a_gig = bitmath.parse_string_unsafe("1gb")
# print (type(a_gig))

