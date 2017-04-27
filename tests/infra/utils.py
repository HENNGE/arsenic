def ids_from_params(params):
    for ec, sc in params:
        yield f'{ec.name}-{sc.name}'
