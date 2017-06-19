``arsenic.actions``
###################

APIs to construct actions to be used in :py:meth:`arsenic.session.Session.perform_actions`.

.. py:module:: arsenic.actions

.. py:function:: chain(*ticks):

    Main API to construct actions for :py:meth:`arsenic.session.Session.perform_actions`.

    :param ticks: A sequence of actions to chain.
    :type ticks: :py:class:`Tick`
    :return: An object which can be passed to :py:meth:`arsenic.session.Session.perform_actions`.


.. py:class:: Button(Enum)

    .. py:attribute:: left
        Left mouse button.

    .. py:attribute:: middle
        Middle mouse button.

    .. py:attribute:: right
        Right mouse button.


.. py:class:: Tick

    Class holding an action tick, which can have multiple actions of different
    devices.

    You should not create instances of this class yourself, but rather use APIs
    on :py:class:`Device` subclasses to create them.

    :py:class:`Tick` can be used with the OR operator (``|``) to combine actions
    of multiple devices.


.. py:class:: Device

    Abstract base class for devices.

    .. py:method:: pause(duration):

        Pause this device (do nothing) for a duration in milliseconds.

        This is primarily used implicitly in action chains that have multiple
        devices but not all devices perform an action on each tick.

        :param int duration: Duration in milliseconds of the pause.
        :rtype: :py:class:`Tick`


.. py:class:: Pointer(Device)

    Base class for pointer devices.

    .. py:method:: move_to(element, duration=250) :

        Moves the pointer to an element.

        :param element: Element to move to.
        :type element: :py:class:`arsenic.session.Element`
        :param int duration: Duration in milliseconds of this action.
        :rtype: :py:class:`Tick`

    .. py:method:: move_by(x, y, duration=250):

        Move the pointer by a given number of pixels relative to the viewport.

        :param int x: Number of pixels to move in the x-axis.
        :param int x: Number of pixels to move in the y-axis.
        :param int duration: Duration in milliseconds for this action.
        :rtype: :py:class:`Tick`

    .. py:method:: down():

        Holds the pointer down.

        :rtype: :py:class:`Tick`

    .. py:method:: up():

        Lifts the pointer up.

        :rtype: :py:class:`Tick`


.. py:class:: Mouse(Pointer):

    Mouse device.

    .. py:method:: down(button=Button.left):

        Hold down a mouse button.

        :param button: Which button to hold down.
        :type button: :py:class:`Button`
        :rtype: :py:class:`Tick`

    .. py:method:: up(button=Button.right):

        Releases a mouse button.

        :param button: Which button to release.
        :type button: :py:class:`Button`
        :rtype: :py:class:`Tick`


.. py:class:: Pen(Pointer):

    A pen device.


.. py:class:: Touch(Pointer):

    A touch device.


.. py:class:: Keyboard(Device):

    A keyboard device.

    .. py:method:: down(key):

        Holds down a specific key.

        :param str key: Which key to hold down.
        :rtype: :py:class:`Tick`

    .. py:method:: up(key):

        Releases a specific key.

        :param str key: Which key to release.
        :rtype: :py:class:`Tick`

