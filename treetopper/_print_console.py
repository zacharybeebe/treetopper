SPACE = 20


def print_stand_species(summary_stand):
    formatted = ['STAND METRICS']
    for i, row in enumerate(summary_stand):
        formatted.append(''.join([j + (' ' * (SPACE - len(j))) for j in row]))
        if i == 0 or i == len(summary_stand) - 2:
            formatted.append('-' * (SPACE * len(row)))
    return '\n'.join(formatted)


def print_stand_logs(summary_logs):
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


def print_stand_stats(summary_stats):
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


def print_thin(summary_thin):
    formatted = []
    for condition in summary_thin:
        formatted.append(condition)
        for i, row in enumerate(summary_thin[condition]):
            if i == len(summary_thin[condition]) - 1:
                formatted.append('-' * SPACE * len(row))
            formatted.append(''.join([j + (' ' * (SPACE - len(j))) for j in row]))
            if i == 0:
                formatted.append('-' * SPACE * len(row))
        formatted += '\n'
    return '\n'.join(formatted)


