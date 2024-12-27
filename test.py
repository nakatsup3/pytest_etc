# from math import pi, sin, cos, tan, log

# def calc_sin(theta):
#     rad = theta * pi / 180
#     return sin(rad)

# a = 2 ** 3
# print(a)

# def f2(x, a, b):
#     return a * x ** 3 + b

# import pyxel

# pyxel.init(128, 128, title='rand', display_scale=1)

# for _ in range(100):
#     print(pyxel.rndi(0, 4))

msg = 'ready?'

ary = []
for s in msg:
    ary.append(s)

print(ary)

while True:
    if 0 < len(ary):
        print(ary.pop(0))
    else:
        break