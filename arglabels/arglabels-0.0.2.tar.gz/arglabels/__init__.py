name = "arglabels"


def create_decorator(**label_map):

    def decorator(original_function):

        def relabeled_function(*args, **kwargs):
            new_kwargs = {}
            for param_name, arg_label in label_map.items():
                new_kwargs[param_name] = kwargs[arg_label]

            return original_function(*args, **new_kwargs)

        return relabeled_function

    return decorator


arglabels = create_decorator
