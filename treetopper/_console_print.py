from treetopper._constants import (format_comma,
                                   sort_grade,
                                   LOG_LENGTHS,
                                   ALL_SPECIES_NAMES,
                                   SORTED_HEADS)

SPACE = 20


def print_species(summary_stand):
    formatted = ['STAND METRICS']
    for i, row in enumerate(summary_stand):
        formatted.append(''.join([j + (' ' * (SPACE - len(j))) for j in row]))
        if i == 0 or i == len(summary_stand) - 2:
            formatted.append('-' * (SPACE * len(row)))
    return '\n'.join(formatted)


def print_logs(summary_logs):
    formatted = ['LOG METRICS']
    for metric in summary_logs:
        formatted.append(metric)
        for species in summary_logs[metric]:
            table_len = SPACE * len(summary_logs[metric][species][0])
            first = '-' * SPACE * 3
            spp_len = len(species)
            formatted.append(first + species + ('-' * (table_len - len(first) - spp_len)))
            for i, row in enumerate(summary_logs[metric][species]):
                formatted.append(''.join([j + (' ' * (SPACE - len(j))) for j in row]))
                if i == 0:
                    formatted.append('-' * (SPACE * len(row)))
            formatted.append('')
        formatted.append('')
    return '\n'.join(formatted)


def print_species_stats(summary_stats):
    formatted = ['STAND STATISTICS']
    for species in summary_stats:
        table_len = SPACE * len(summary_stats[species][0])
        first = '-' * SPACE * 4
        spp_len = len(species)
        formatted.append(first + species + ('-' * (table_len - len(first) - spp_len)))
        for i, row in enumerate(summary_stats[species]):
            formatted.append(''.join([j + (' ' * (SPACE - len(j))) for j in row]))
            if i == 0:
                formatted.append('-' * (SPACE * len(row)))
        formatted.append('')
    formatted.append('')
    return '\n'.join(formatted)


def print_test(summary_stats):
    formatted = ['STAND STATISTICS']
    for species in summary_stats:
        table_len = SPACE * len(summary_stats[species][0])
        first = '-' * SPACE * 4
        spp_len = len(species)
        formatted.append(first + species + ('-' * (table_len - len(first) - spp_len)))
        for i, row in enumerate(summary_stats[species]):
            formatted.append(''.join([j + (' ' * (SPACE - len(j))) for j in row]))
            if i == 0:
                formatted.append('-' * (SPACE * len(row)))
        formatted.append('')
    formatted.append('')

    return '\n'.join(formatted)





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

    text = ''

    for i in all_data:
        for j in i:
            #print(j)
            text += f'\n{j}'
        text += '\n\n'
        #print('\n')
    return text


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

