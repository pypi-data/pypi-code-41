def exclude_page_type(queryset, page_models):
    qs = queryset.none()
    for model in page_models:
        qs |= queryset.not_type(model)
    return qs
