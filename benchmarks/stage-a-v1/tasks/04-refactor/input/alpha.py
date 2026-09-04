def legacy_total(values):
    return sum(value for value in values if value >= 0)


def alpha_total(values):
    return legacy_total(values)
