from _constants import (format_comma,
                        sort_grade,
                        LOG_LENGTHS,
                        ALL_SPECIES_NAMES,
                        SORTED_HEADS)

SPACE = 20


def print_species(species):
    heads = ['SPECIES'] + [head[1] for head in SORTED_HEADS]
    formatted_heads = ''.join([head + (' ' * (SPACE - len(head))) for head in heads])
    formatted_data = []
    for z, key in enumerate(species):
        if key == 'totals_all':
            show = 'TOTALS'
        else:
            show = key
        temp = [str(show)] + [format_comma(species[key][i[0]]) for i in SORTED_HEADS]
        formatted_data.append(''.join([t + (' ' * (SPACE - len(t))) for t in temp]))
        if z == len(species) - 1:
            formatted_data.append('-' * (SPACE * len(heads)))

    formatted_data.append(formatted_data.pop(0))

    print(formatted_heads)
    print('-' * SPACE * len(heads))
    for i in formatted_data:
        print(i)


def print_logs(logs):
    heads = ['LOG LENGTHS'] + [rng.upper() for rng in LOG_LENGTHS] + ['TOTALS']
    formatted_heads = ''.join([head + (' ' * (SPACE - len(head))) for head in heads])
    tables = [['bf_ac', 'BOARD FEET PER ACRE'], ['cf_ac', 'CUBIC FEET PER ACRE'], ['lpa', 'LOGS PER ACRE']]
    table_data = []

    for i in tables:
        temp = [[i[1]]]
        for species in logs:
            temp_temp = []
            ratio = 56
            if species == 'totals_all':
                label = 'TOTAL SPECIES'
            else:
                label = ALL_SPECIES_NAMES[species]
            first = '-' * (((SPACE * len(heads)) - len(label)) // 100 * ratio)
            second = '-' * ((len(heads) * SPACE) - (len(first) + len(label)))
            show = [first + label + second]

            temp_temp.append(''.join(show))
            temp_temp.append(formatted_heads)
            temp_temp.append('-' * (SPACE * len(heads)))
            grade_sort = []
            for grade in logs[species]:
                values = [logs[species][grade][rng][i[0]]['mean'] for rng in logs[species][grade]]
                if sum(values) > 0:
                    if grade == 'totals_by_length':
                        txt = 'TOTALS'
                    else:
                        txt = grade
                    show2 = [txt] + [format_comma(z) for z in values]
                    grade_sort.append(show2)
            grade_sort = sorted(grade_sort, key=sort_grade)
            for g in grade_sort:
                temp_temp.append(''.join([gs + (' ' * (SPACE - len(gs))) for gs in g]))
            temp.append(temp_temp)

        if len(logs) <= 2:
            temp.pop(1)
        else:
            temp.append(temp.pop(1))

        table_data.append(temp)

    for i in table_data:
        for z, j in enumerate(i):
            for k in j:
                print(k)
            if z > 0:
                if z == len(i) - 1:
                    print('-' * (SPACE * len(heads)))
                else:
                    print()
        print('\n\n')


def print_species_stats(species):
    print_data = []
    for spp in species:
        if spp == 'totals_all':
            show = 'TOTALS'
        else:
            show = ALL_SPECIES_NAMES[spp]
        temp = [show]
        heads = ['METRIC'] + [head.upper() for head in species[spp]['tpa'] if head != 'low_avg_high'] + ['LOW', 'AVERAGE', 'HIGH']
        formatted_heads = ''.join([head + (' ' * (SPACE - len(head))) for head in heads])
        temp.append(formatted_heads)
        temp.append('-' * (SPACE * len(heads)))

        for key in species[spp]:
            temp_temp = [key.upper() + (' ' * (SPACE - len(key)))]
            for sub in species[spp][key]:
                data = species[spp][key][sub]
                if data == 'Not enough data':
                    temp_temp.append(data)
                    for i in range(6):
                        temp_temp.append('-')
                    break
                else:
                    if sub != 'stderr_pct' and sub != 'low_avg_high':
                        temp_temp.append(format_comma(data))
                    elif sub == 'stderr_pct':
                        temp_temp.append(str(round(data, 1)) + ' %')
                    else:
                        for i in data:
                            temp_temp.append(format_comma(i))
            temp.append(''.join([dat + (' ' * (SPACE - len(dat))) for dat in temp_temp]))
        print_data.append(temp)

    if len(species) <= 2:
        print_data.pop(0)
    else:
        print_data.append(print_data.pop(0))

    for i in print_data:
        for j in i:
            print(j)
        print()


def print_thin_species(species):
    all_data = []
    for condition in species:
        formatted_data = [condition.replace('_', '').upper()]
        heads = ['SPECIES'] + [head[1] for head in SORTED_HEADS]
        formatted_heads = ''.join([head + (' ' * (SPACE - len(head))) for head in heads])
        formatted_data.append(formatted_heads)
        formatted_data.append('-' * (SPACE * len(heads)))
        for z, spp in enumerate(species[condition]):
            if spp == 'totals_all':
                show = 'TOTALS'
            else:
                show = spp
            temp = [str(show)] + [format_comma(species[condition][spp][i[0]]) for i in SORTED_HEADS]
            formatted_data.append(''.join([t + (' ' * (SPACE - len(t))) for t in temp]))
            if z == len(species[condition]) - 1:
                formatted_data.append('-' * (SPACE * len(heads)))

        formatted_data.append(formatted_data.pop(3))
        all_data.append(formatted_data)

    all_data.append(all_data.pop(1))

    for i in all_data:
        for j in i:
            print(j)
        print('\n')


def print_plot_logs(plot):
    logs = plot.logs
    heads = ['LOG LENGTHS'] + [rng.upper() for rng in LOG_LENGTHS] + ['TOTALS']
    formatted_heads = ''.join([head + (' ' * (SPACE - len(head))) for head in heads])
    tables = [['bf_ac', 'BOARD FEET PER ACRE']]#, ['cf_ac', 'CUBIC FEET PER ACRE'], ['lpa', 'LOGS PER ACRE']]
    table_data = []

    for i in tables:
        temp = [[i[1]]]
        for species in logs:
            temp_temp = []
            ratio = 56
            if species == 'totals_all':
                label = 'TOTAL SPECIES'
            else:
                label = ALL_SPECIES_NAMES[species]
            first = '-' * (((SPACE * len(heads)) - len(label)) // 100 * ratio)
            second = '-' * ((len(heads) * SPACE) - (len(first) + len(label)))
            show = [first + label + second]

            temp_temp.append(''.join(show))
            temp_temp.append(formatted_heads)
            temp_temp.append('-' * (SPACE * len(heads)))
            grade_sort = []
            for grade in logs[species]:
                if grade == 'totals_by_length':
                    txt = 'TOTALS'
                else:
                    txt = grade
                show2 = [txt] + [format_comma(logs[species][grade][rng][i[0]]) for rng in logs[species][grade] if rng != 'display']
                grade_sort.append(show2)
            grade_sort = sorted(grade_sort, key=sort_grade)
            for g in grade_sort:
                temp_temp.append(''.join([gs + (' ' * (SPACE - len(gs))) for gs in g]))
            temp.append(temp_temp)

        if len(logs) <= 2:
            temp.pop(1)
        else:
            temp.append(temp.pop(1))

        table_data.append(temp)

    for i in table_data:
        for z, j in enumerate(i):
            for k in j:
                print(k)
            if z > 2:
                print()
        print('\n')





if __name__ == '__main__':
    x = 10
    for i in range(15):
        print(format_comma(x + .1))
        x = x * 10

