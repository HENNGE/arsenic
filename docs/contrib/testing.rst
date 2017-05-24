Testing
#######

Using circleci-local
********************

The easiest way to run the tests is using `circleci local`_. If you have it
installed, simply run ``circleci build`` in the root directory.

Manual
******

1. Install the test dependencies in ``tests/requirements.txt`` and ``tests/app/requirements.txt``.
2. Run the app in ``tests/app/app.py``.
3. Run ``WEB_APP_BASE_URL=http://localhost:5000 pytest`` in the root directory.


.. _circleci local: https://circleci.com/docs/2.0/local-jobs/
