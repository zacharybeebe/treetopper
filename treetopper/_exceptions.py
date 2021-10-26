class TargetDensityError(Exception):
    def __init__(self, target_density, current_density, target_metric):
        p1 = f"""Target Density of {target_density} {target_metric} """
        p2 = f"""is greater than Stand Total of {round(current_density, 1)} {target_metric}. """
        p3 = f"""Please lower Target Density"""
        self.message = p1 + p2 + p3
        super(TargetDensityError, self).__init__(self.message)


class ImportSheetError(Exception):
    def __init__(self, filename, message_bucket):
        mesaages = '\n-'.join(message_bucket)
        self.message = f'\nFile: {filename}\n-{mesaages}'
        super(ImportSheetError, self).__init__(self.message)