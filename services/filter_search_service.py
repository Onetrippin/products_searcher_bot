from data.user_queries import user_queries


def extract_selected_filters(chat_id: int) -> dict:
    filters = user_queries.get(chat_id).get('filters')
    selected_filters = {filter_: data.get('params') for filter_, data in filters.items() if data.get('any_selected')}
    only_selected_params = {filter_: [param for param, value in params.items() if value] for filter_, params in selected_filters.items()}
    only_selected_params.pop('Магазин', None)
    if only_selected_params.get('Оперативка'):
        for i, value in enumerate(only_selected_params['Оперативка']):
            only_selected_params['Оперативка'][i] = value[:-3]
    if only_selected_params.get('Память'):
        for i, value in enumerate(only_selected_params['Память']):
            if 'ТБ' in value:
                only_selected_params['Память'][i] = value[:-3] + '000'
                continue
            only_selected_params['Память'][i] = value[:-3]
    if only_selected_params.get('Аккумулятор'):
        params = only_selected_params.get('Аккумулятор')
        lower_limit = params[0].split('-')[0] if (params[0].split('-')[0]).isdigit() else '6000'
        upper_limit = params[-1].split()[-2].split('-')[1] if not (params[-1].split()[-2]).isdigit() else 'max'
        only_selected_params['Аккумулятор'] = [lower_limit,
                                               upper_limit]
    if only_selected_params.get('Камера'):
        for i, value in enumerate(only_selected_params['Камера']):
            only_selected_params['Камера'][i] = value[:-3]
    if only_selected_params.get('Объем SSD'):
        for i, value in enumerate(only_selected_params['Объем SSD']):
            if 'ТБ' in value:
                only_selected_params['Объем SSD'][i] = value[:-3] + '000'
                continue
            only_selected_params['Объем SSD'][i] = value[:-3]
    print(only_selected_params)
    return only_selected_params