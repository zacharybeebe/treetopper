from random import choice, randrange
from time import perf_counter
from _constants import (ALL_SPECIES_NAMES,
                        OFFICIAL_GRADES)


SPECIES_RANGE = 3

def timer(func):
    def wrapper(*args, **kwargs):
        now = perf_counter()
        x = func(*args, **kwargs)
        after = perf_counter()
        time_took = round(after-now, 5)
        print(f'{func.__name__} took {time_took} seconds\n')
        return x, time_took
    return wrapper


def calc_log_grade(species, dib, length, next_=False):
    for i, specs in enumerate(OFFICIAL_GRADES[species]):
        if dib >= specs[0] and length >= specs[1]:
            if i != len(OFFICIAL_GRADES[species]) - 1:
                if next_:
                    return OFFICIAL_GRADES[species][i+1][2]
                else:
                    return specs[2]
            else:
                return specs[2]


def generate_random_trees_quick(number_of_trees: int):
    from timber import TimberQuick

    tree_list = []
    for i in range(number_of_trees):
        hdr = randrange(540, 899) / 10
        species = choice([key for key in ALL_SPECIES_NAMES][:SPECIES_RANGE])
        dbh = randrange(69, 455) / 10
        height = int((dbh / 12) * hdr)
        plot_factor = 33.3

        tree_list.append(TimberQuick(*[species, dbh, height, plot_factor]))
    return tree_list, len(tree_list)


def generate_random_trees_full(number_of_trees: int):
    from timber import TimberFull

    tree_list = []
    for i in range(number_of_trees):
        hdr = randrange(540, 899) / 10
        species = choice([key for key in ALL_SPECIES_NAMES][:SPECIES_RANGE])

        dbh = randrange(69, 455) / 10
        height = int((dbh / 12) * hdr)
        plot_factor = 33.3

        tree = TimberFull(*[species, dbh, height, plot_factor])

        x = 1
        max_ = int(height * 0.8)
        defects = [0, 0, 0, 0, 0, 0, 0, 0, 0, 5, 5, 5, 5, 5, 10, 10, 10, 15]
        for i in range(10):
            if x + 41 > max_:
                length = int(((max_ - x - 2) // 2) * 2)
                if length < 2:
                    break
                else:
                    stem_height = max_
                    dib = tree.get_any_dib(stem_height)
                    defect = choice(defects)
                    if defect > 5:
                        grade = calc_log_grade(species, dib, length, next_=True)
                    else:
                        grade = calc_log_grade(species, dib, length)
                    tree.add_log(stem_height, length, grade, defect)
                    break
            else:
                length = 40
                stem_height = x + length + 1
                dib = tree.get_any_dib(stem_height)
                defect = choice(defects)
                if defect > 5:
                    grade = calc_log_grade(species, dib, length, next_=True)
                else:
                    grade = calc_log_grade(species, dib, length)
                tree.add_log(stem_height, length, grade, defect)
                if x + length + 1 < max_:
                    x += length + 1
        tree.calc_volume_and_logs()
        tree_list.append(tree)
    return tree_list, len(tree_list)


def generate_random_plots(number_of_plots: int, full: bool = False):
    from plot import Plot

    tree_count = 0
    plot_list = []

    for i in range(number_of_plots):
        num_trees = randrange(3, 12)
        plot = Plot()
        if full:
            trees, count = generate_random_trees_full(num_trees)
        else:
            trees, count = generate_random_trees_quick(num_trees)

        for j in trees:
            plot.add_tree(j)
        plot_list.append(plot)
        tree_count += count

    return plot_list, tree_count

