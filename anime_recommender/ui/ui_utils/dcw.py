"""Dash callback wrapper.

Enables property-chained referencing style for callback parameters and parameter-free callback definition for callbacks
with parameters.
"""

import inspect

from dash import Dash
from dash import callback as dash_callback
from dash import ctx


class PropertyClass(object):
    """Dash callback parameter wrapper. Stores reference to component property."""

    def __init__(self, name):
        """Initialize PropertyClass instance.

        Parameters
        ----------
        name : str
            Dash component id.
        """
        self.id = name

    def __getattr__(self, name):
        """Get component property.

        Parameters
        ----------
        name : str
            Dash component property name.

        Returns
        -------
        Any
            Dash component property.
        """
        attr = '{id}.{name}'.format(id=self.id, name=name)
        attr_hyphen = attr.replace('_', '-')
        input_var = ctx.inputs.get(attr, ctx.inputs.get(attr_hyphen))
        state_var = ctx.states.get(attr, ctx.states.get(attr_hyphen))
        return input_var or state_var


class DynamicStaticAttrMeta(type):
    """Metaclass for CallbackManager."""

    def __getattr__(cls, name):
        """Create a new attribute based on Dash component id.

        Parameters
        ----------
        name : str
            Dash component id.

        Returns
        -------
        PropertyClass
            Dash callback parameter wrapper.
        """
        if name not in cls.__dict__:
            setattr(cls, name, PropertyClass(name))
        return getattr(cls, name)


class CallbackManager(metaclass=DynamicStaticAttrMeta):  # noqa: WPS306
    """Dash callback manager. Enables property-chained referencing style for callback parameters."""

    pass  # noqa: WPS604, WPS420


class DCWDash(Dash):
    """Dash subclass.

    Allows defining callbacks in both styles: @callback and @app.callback.
    """

    @staticmethod
    def callback(*args, **kwargs):  # noqa: WPS602
        """Dash callback wrapper. Enables parameter-free callback definition for callbacks with parameters.

        Parameters
        ----------
        args : Any
            Dash callback args.

        kwargs : Any
            Dash callback kwargs.

        Returns
        -------
        Callable
            Dash callback.
        """

        def decorator(func):
            num_params = len(inspect.signature(func).parameters)

            def wrapper(*wrapper_args):
                if num_params:
                    return func(*wrapper_args)
                return func()

            return dash_callback(*args, **kwargs)(wrapper)

        return decorator


callback = DCWDash.callback
callback_manager = CallbackManager
