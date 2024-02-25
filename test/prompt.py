def multiplier(x):
    def inner_multiplier(y):
        return x * y
    return inner_multiplier
multiply_with_5 = multiplier(5)
result = multiply_with_5(2)
print(result)

