import sys
import json
from functools import partial
from scipy.optimize import basinhopping


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


def add_nutrient_cost(nutrient_amounts, increase, percentage_tune):
    extra_cost = 0
    for nutrient, nutrient_amount in nutrient_amounts.values():
        add_to_cost = 0

        if nutrient_amount < nutrient.minimum:
            diff = nutrient.minimum - nutrient_amount
            percentage_diff = (diff / nutrient.minimum) * 100
            # add_to_cost += (diff / increase) ** 2
            add_to_cost += (diff / increase)
            add_to_cost += (percentage_diff / percentage_tune) ** 2

        elif nutrient_amount > nutrient.maximum:
            diff = nutrient_amount - nutrient.maximum
            percentage_diff = (diff / nutrient.maximum) * 100
            add_to_cost += (diff * increase) ** 2
            add_to_cost += (percentage_diff / percentage_tune) ** 2
        if add_to_cost:
            extra_cost += add_to_cost
    return extra_cost


def find_cost(ingredient_amounts, base_cost=False, increase=20, percentage_tune=6):
    nutrient_amounts, cost, total_amount = get_nutrient_amounts(ingredient_amounts)

    if not base_cost:
        cost += add_nutrient_cost(nutrient_amounts, increase, percentage_tune)
    return cost


def get_nutrient_amounts(ingredient_amounts):
    cost = 0
    nutrient_amounts = {}
    for name, nutrient in nutrients.items():
        nutrient_amounts[name] = [nutrient, 0]

    total_amount = sum(x for x in ingredient_amounts if x > 0)
    for x, ingredient in enumerate(ingredients):
        percent = 0
        if total_amount != 0:
            percent = max(ingredient_amounts[x] / total_amount, 0)

        cost += ingredient.price * percent
        for nutrient in ingredient.provides:
            nutrient_amounts[nutrient[0]][1] += nutrient[1] * percent

    return nutrient_amounts, cost, total_amount


# https://docs.scipy.org/doc/scipy-0.19.0/reference/generated/scipy.optimize.minimize.html
def basin_hopping(initial):
    # Use loose constraints to allow the algorithm to get close
    ret = basinhopping(partial(find_cost, increase=50, percentage_tune=8),
                       initial, niter=100, stepsize=1.5, interval=10)
    best_ration = ret.x
    nutrient_amounts, cost, total_amount = get_nutrient_amounts(best_ration)
    print_results(best_ration, nutrient_amounts, cost, total_amount)

    # Tighten up the constraints to get closer to the minimums
    ret = basinhopping(partial(find_cost, increase=10, percentage_tune=2.4),
                       best_ration, niter=50)
    best_ration = ret.x
    nutrient_amounts, cost, total_amount = get_nutrient_amounts(best_ration)
    print_results(best_ration, nutrient_amounts, cost, total_amount)
    result_amounts = ["{:4f}".format((max(x, 0) / total_amount) * 100) for x in best_ration]
    print(result_amounts)

    # J1
    # best_ration = [
    #     9.874915, 0.000000, 0.000000, 1.953607, 1.084227, 0.000000, 3.145987,
    #     18.141387, 0.000000, 65.274137, 0.000000, 0.383916, 0.141824, 0.000000, 0.000000
    # ]

    # ret2 = basinhopping(find_cost, best_ration, niter=100, stepsize=0.05,
    #                     interval=10, T=0.004, accept_test=accept_test)
    # best_ration = ret2.x
    # info = get_nutrient_amounts(best_ration)
    # print_results(best_ration, info)

    # result_amounts = ["{:4f}".format((max(x, 0) / info[2]) * 100) for x in best_ration]
    # print(result_amounts)

    if not send_to_ruby:
        print('------')
        print('------')
        print('------')


def print_results(best_ration, nutrient_amounts, cost, total_amount):
    dollar_cost = find_cost(best_ration, base_cost=True)
    if not send_to_ruby:
        print('Cost per KG ${:.2f}, at percent: {:.2f}'.format(dollar_cost, total_amount))

    for y, ingredient in enumerate(ingredients):
        if not send_to_ruby:
            print('{}: {:.5f}%'.format(ingredient, (max(best_ration[y], 0) / total_amount) * 100))

    for nut_name, values in nutrient_amounts.items():
        diff = round(values[0].minimum - values[1], 3)

        if diff > 0.001:
            if not send_to_ruby:
                print('{} was under the minimum by {:.3f}'.format(nut_name, diff))
        elif values[0].maximum < values[1]:
            if not send_to_ruby:
                print('{} over by {:.2f}'.format(nut_name, values[1] - values[0].maximum))

    if not send_to_ruby:
        print('------')


def find_rations():
    basin_hopping(initial)


initial = []
nutrients = {}
ingredients = []

send_to_ruby = False


def load_nutrients_and_ingredients(json):
    for i, nut_req in enumerate(json['ration_nutrient_requirements']):
        nutrients[nut_req['name']] = Nutrient(nut_req['name'], float(nut_req['min']),
                                              float(nut_req['max']))

    ing_nutrients = {}
    for i, row in enumerate(json['nutrient_chart']):

        if row['product_type_name'] not in ing_nutrients:
            ing_nutrients[row['product_type_name']] = []

        ing_nutrients[row['product_type_name']].append(
            (row['nutrient_type_name'], float(row['amount'])))

    for i, ing in enumerate(json['ration_products']):
        nuts = []
        if ing['name'] in ing_nutrients:
            nuts = ing_nutrients[ing['name']]
        ingredients.append(Ingredient(ing['name'], float(ing['ingredient_cost_per_kilo']),
                                      nuts, minimum=float(ing['min']), maximum=float(ing['max'])))
        initial.append(float(ing['min']))


if __name__ == '__main__':
    send_to_ruby = len(sys.argv) > 1

    if send_to_ruby:
        load_nutrients_and_ingredients(json.loads(sys.argv[1]))
    else:
        load_nutrients_and_ingredients(json.loads(open('recipes/B1.json').read()))
        # B1 ration: 23.73
        # B2: 22.18
        # B3: 23.15
        # J1 20.25

    find_rations()
