import inspect

import dash


class PropertyClass:
    def __init__(self, name):
        self.id = name

    def __getattr__(self, name):
        attr = self.id + '.' + name
        return dash.ctx.inputs.get(
            attr,
            dash.ctx.inputs.get(attr.replace('_', '-')),
        ) or dash.ctx.states.get(attr, dash.ctx.states.get(attr.replace('_', '-')))


class DynamicStaticAttrMeta(type):
    def __getattr__(cls, name):
        setattr(cls, name, PropertyClass(name))
        return getattr(cls, name)


class CallbackManager(metaclass=DynamicStaticAttrMeta):
    pass


class DCWDash(dash.Dash):
    @staticmethod
    def callback(*args, **kwargs):
        def decorator(f):
            num_params = len(inspect.signature(f).parameters)

            def wrapper(*wrapper_args):
                if num_params == 0:
                    return f()
                else:
                    return f(*wrapper_args)

            return dash.callback(*args, **kwargs)(wrapper)

        return decorator


callback = DCWDash.callback
callback_manager = CallbackManager
