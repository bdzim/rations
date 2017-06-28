from scipy.optimize import minimize
import skopt


class Nutrient(object):
    def __init__(self, name, minimum, maximum):
        self.name = name
        self.minimum = minimum
        self.maximum = maximum

    def __str__(self):
        return self.name


class Ingredient(object):
    def __init__(self, name, price, provides, minimum=0, maximum=100):
        self.name = name
        self.price = price
        self.provides = provides
        self.minimum = minimum
        self.maximum = maximum

    def __str__(self):
        return self.name


# Nutrient names
calcium = 'Calcium'
crude_fiber = 'Crude Fiber'
crude_protein = 'Crude Protein'
dig_arganine = 'Dig. Arganine'
dig_isoleucine = 'Dig. Isoleucine'
dig_lysine = 'Dig. Lysine'
dig_meth_cyst = 'Dig. Meth. + Cyst'
dig_phosphorus_poultry = 'Dig. Phosphorus Poultry'
dig_threonine = 'Dig. Threonine'
dig_tryptophan = 'Dig. Tryptophan'
dig_valine = 'Dig. Valine'
energy_me_broiler = 'Energy ME Broiler'
fat = 'Fat'

ingredients = [
    Ingredient('Limestone', 2.6, [(calcium, 36)]),
    Ingredient('Wheat, 12.3% prot', 13.4, [
        (calcium, .04),
        (crude_fiber, 3),
        (crude_protein, 12.3),
        (dig_arganine, .497),
        (dig_isoleucine, .345),
        (dig_lysine, .258),
        (dig_meth_cyst, .384),
        (dig_phosphorus_poultry, .1),
        (dig_threonine, .25),
        (dig_tryptophan, .123),
        (dig_valine, .424),
        (energy_me_broiler, 3035),
        (fat, 1.5),
    ]),
    Ingredient('Corn', 15.523087683374898, [
        (calcium, .04),
        (crude_fiber, 2),
        (crude_protein, 7.8),
        (dig_arganine, .323),
        (dig_isoleucine, .223),
        (dig_lysine, .187),
        (dig_meth_cyst, .285),
        (dig_phosphorus_poultry, .08),
        (dig_threonine, .225),
        (dig_tryptophan, .047),
        (dig_valine, .3),
        (energy_me_broiler, 3310),
        (fat, 4),
    ]),
    Ingredient('Sunflower 34 Extracted', 20.2, [
        (calcium, .35),
        (crude_fiber, 23),
        (crude_protein, 31.7),
        (dig_arganine, 2.337),
        (dig_isoleucine, 1.144),
        (dig_lysine, .865),
        (dig_meth_cyst, 1.02),
        (dig_phosphorus_poultry, .25),
        (dig_threonine, .95),
        (dig_tryptophan, .304),
        (dig_valine, 1.336),
        (energy_me_broiler, 1203),
        (fat, 1.1),
    ]),
    Ingredient('SBM Expelled 43 / 4', 40.1, [
        (calcium, .27),
        (crude_fiber, 5.8),
        (crude_protein, 43.1),
        (dig_arganine, 2.808),
        (dig_isoleucine, 1.706),
        (dig_lysine, 2.262),
        (dig_meth_cyst, 1.018),
        (dig_phosphorus_poultry, .27),
        (dig_threonine, 1.396),
        (dig_tryptophan, .476),
        (dig_valine, 1.759),
        (energy_me_broiler, 2211),
        (fat, 6.2),
    ]),
    Ingredient('SBM full fat', 41.3, [
        (calcium, .22),
        (crude_fiber, 5.4),
        (crude_protein, 36),
        (dig_arganine, 2.344),
        (dig_isoleucine, 1.374),
        (dig_lysine, 1.779),
        (dig_meth_cyst, .792),
        (dig_phosphorus_poultry, .21),
        (dig_threonine, 1.053),
        (dig_tryptophan, .398),
        (dig_valine, 1.434),
        (energy_me_broiler, 2064),
        (fat, 19.5),
    ]),
    Ingredient(
        'Soya oil', 59,
        [
            (energy_me_broiler, 7500),
            (fat, 100),
        ],
        maximum=1,
    ),
    Ingredient('Mononcalcium Phosphate', 67, [
        (calcium, .18),
        (dig_phosphorus_poultry, 19.29),
    ]),
    Ingredient('Broiler Start 75831', 160, [
        (calcium, 12),
        (crude_fiber, .88),
        (crude_protein, 40.9),
        (dig_arganine, .81),
        (dig_isoleucine, .77),
        (dig_lysine, 19.5),
        (dig_meth_cyst, 17.5),
        (dig_phosphorus_poultry, 8.35),
        (dig_threonine, 7.5),
        (dig_valine, 4),
        (energy_me_broiler, 2468),
        (fat, .83),
    ]),
    Ingredient('Lysine', 200, [
        (crude_protein, 95.6),
        (dig_lysine, 79),
        (energy_me_broiler, 3500),
    ]),
    Ingredient('Threonine', 205, [
        (crude_protein, 60),
        (dig_threonine, 98),
        (energy_me_broiler, 3000),
    ]),
    Ingredient('Methionine', 405, [
        (calcium, 4),
        (crude_protein, 58.7),
        (dig_lysine, 3.5),
        (dig_meth_cyst, 99),
        (energy_me_broiler, 4700),
    ]),
]
nutrients = [
    Nutrient(calcium, .89, 100),
    Nutrient(crude_fiber, 0, 5.5),
    Nutrient(crude_protein, 19.8, 100),
    Nutrient(dig_arganine, 1.15, 100),
    Nutrient(dig_isoleucine, .71, 100),
    Nutrient(dig_lysine, 1.13, 100),
    Nutrient(dig_meth_cyst, .8, 100),
    Nutrient(dig_phosphorus_poultry, .4, 100),
    Nutrient(dig_threonine, .69, 100),
    Nutrient(dig_tryptophan, .18, 100),
    Nutrient(dig_valine, .85, 100),
    Nutrient(energy_me_broiler, 2750, 3000),
    Nutrient(fat, 0, 100),
]


def add_nutrient_cost_flat(nutrient_amounts, debug):
    extra_cost = 0
    for nutrient, nutrient_amount in nutrient_amounts.values():
        add_to_cost = 0
        increase = 8
        if nutrient_amount < nutrient.minimum:
            diff = nutrient.minimum - nutrient_amount
            add_to_cost = (diff * increase) ** 2
        elif nutrient_amount > nutrient.maximum:
            diff = nutrient_amount - nutrient.maximum
            add_to_cost = (diff * increase) ** 2
        if add_to_cost:
            extra_cost += add_to_cost
            if debug:
                print('{}: {} < {:.5f} < {}: diff: {:.3f}'.format(
                    nutrient, nutrient.minimum, nutrient_amount, nutrient.maximum, diff))
    return extra_cost


def add_nutrient_cost_percentage(nutrient_amounts, debug):
    extra_cost = 0
    for nutrient, nutrient_amount in nutrient_amounts.values():
        add_to_cost = 0
        increase = 1
        if nutrient_amount < nutrient.minimum:
            diff = nutrient.minimum - nutrient_amount
            percentage_diff = (diff / nutrient.minimum) * 100
            add_to_cost = (percentage_diff / increase) ** 2
        elif nutrient_amount > nutrient.maximum:
            diff = nutrient_amount - nutrient.maximum
            percentage_diff = (diff / nutrient.maximum) * 100
            add_to_cost = (percentage_diff / increase) ** 2
        if add_to_cost:
            extra_cost += add_to_cost
            if debug:
                print('{}: {} < {:.5f} < {}: diff: {:.3f} {:.2f}%'.format(
                    nutrient, nutrient.minimum, nutrient_amount, nutrient.maximum, diff,
                    percentage_diff
                ))
    return extra_cost


def add_nutrient_cost_both(nutrient_amounts, debug):
    extra_cost = 0
    for nutrient, nutrient_amount in nutrient_amounts.values():
        add_to_cost = 0
        increase = 5
        percentage_tune = 4
        if nutrient_amount < nutrient.minimum:
            diff = nutrient.minimum - nutrient_amount
            percentage_diff = (diff / nutrient.minimum) * 100
            add_to_cost += (diff / increase) ** 2
            add_to_cost += (percentage_diff / percentage_tune) ** 2
        elif nutrient_amount > nutrient.maximum:
            diff = nutrient_amount - nutrient.maximum
            percentage_diff = (diff / nutrient.maximum) * 100
            add_to_cost += (diff * increase) ** 2
            add_to_cost += (percentage_diff / percentage_tune) ** 2
        if add_to_cost:
            extra_cost += add_to_cost
            if debug:
                print('{}: {} < {:.5f} < {}: diff: {:.3f} {:.2f}%'.format(
                    nutrient, nutrient.minimum, nutrient_amount, nutrient.maximum, diff,
                    percentage_diff
                ))
    return extra_cost


def find_cost(ingredient_amounts, base_cost=False, debug=False):
    cost = 0
    nutrient_amounts = {}
    for nutrient in nutrients:
        nutrient_amounts[nutrient.name] = [nutrient, 0]

    total_amount = sum(x for x in ingredient_amounts if x > 0)
    for x, ingredient in enumerate(ingredients):
        percent = max(ingredient_amounts[x] / total_amount, 0)
        cost += ingredient.price * percent
        for nutrient in ingredient.provides:
            nutrient_amounts[nutrient[0]][1] += nutrient[1] * percent

    if not base_cost:
        cost += add_nutrient_cost_both(nutrient_amounts, debug)

    return cost


def accept_test(**kwargs):
    x_new = kwargs.pop('x_new')
    print('{}: {}'.format(x_new, all(x >= 0 for x in x_new)))
    return all(x >= 0 for x in x_new)


def print_fun(x, f, accepted):
    print("at minima %.4f accepted %d" % (f, int(accepted)))


def bfgs():
    initial = [2.81, 4.45, 52.5, 0, 27.66, 6.875, 0, 3.5, 2.1149, .0084, .07, .0046]
    dollar_cost = find_cost(initial, base_cost=True)
    print('Initial cost per KG ${:.2f}'.format(dollar_cost))
    lowest_cost = 100
    best_ration = initial
    for x in range(5):
        ret = minimize(
            find_cost, best_ration, method='BFGS',
            options=dict(disp=False),
        )
        cost = find_cost(ret.x)
        print('Cost:', cost)
        if cost < lowest_cost:
            best_ration = ret.x

    print(find_cost(best_ration, debug=True), '\n')
    dollar_cost = find_cost(ret.x, base_cost=True)
    print('Cost per KG ${:.2f}'.format(dollar_cost))
    total_amount = sum(x for x in best_ration if x > 0)
    for y, ingredient in enumerate(ingredients):
        print('{}: {:.5f}%'.format(ingredient, (max(best_ration[y], 0) / total_amount) * 100))


def forest():
    res = skopt.forest_minimize(find_cost, )


def find_rations():
    bfgs()
    # forest()


if __name__ == '__main__':
    find_rations()
