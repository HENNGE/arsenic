Hello Arsenic
#############

This tutorial will show you how to install arsenic and write a simple script
that will use Firefox and Google Images to search for pictures of cats.

Prerequisites
*************

This tutorial assumes you already have `Python 3.6`_ and `Firefox`_ installed.

You will also need to install `geckodriver`_. Download the latest release for your
operating system from the `releases page`_. Extract the binary executable from
the archive and place it in the current directory. On OS X or Linux you might
need to mark it as an executable using ``chmod +x geckodriver`` in your terminal.

Creating a virtual env
**********************

We will create a virtual env to install arsenic::

    python3.6 -m venv env

Let's make sure that ``pip`` is up to date::

    env/bin/pip install --upgrade pip

Let's install arsenic::

    env/bin/pip install --pre arsenic


Writing the script
******************

In your favourite text editor, create a file named ``cats.py`` and insert the
following code:

.. literalinclude:: helloworld.py
    :emphasize-lines: 12-20


Save it and in the terminal, run ``python cats.py``. You should see an instance
of Firefox starting, navigating to ``https://images.google.com`` and entering
``Cats`` in the search box, then submitting the search. The browser will then
wait for 10 seconds for you to look at the cats before exiting.


.. _Python 3.6: https://www.python.org/downloads/release/python-361/
.. _Firefox: https://www.mozilla.org/en-US/firefox/new/?scene=2
.. _geckodriver: https://github.com/mozilla/geckodriver
.. _releases page: https://github.com/mozilla/geckodriver/releases
