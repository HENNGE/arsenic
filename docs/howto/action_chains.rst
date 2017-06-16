Action Chains
#############

Arsenic supports action chains that allow you to define a sequence of mouse and/or
keyboard actions to perform in sequence (and in parallel).

.. note::

    Action chains are only supported by a few browsers so far. For other browsers,
    arsenic will attempt to emulate them using older APIs, however it can only
    emulate a single mouse input.

Drag and drop
*************

Drag and drop functionality can be implemented using :py:class:`arsenic.actions.Mouse`
together with :py:func:`arsenic.actions.chain` and :py:meth:`arsenic.session.Session.preform_actions`.

Here is an example helper function which moves the mouse to an element and drags
it by a specified amount of pixels:

.. literalinclude:: action_chains.py
    :lines: 1-13

