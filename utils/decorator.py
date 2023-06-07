def with_advance_search(func):
    def wrapper(*args, **kwargs):
        result = args[0]
        params = args[1]
        filter_conditions = {}
        for param in params.get('query', []):
            if result.query_params.get(param, ''):
                filter_conditions[param] = result.query_params.get(param, '')

        return filter_conditions

    return wrapper
