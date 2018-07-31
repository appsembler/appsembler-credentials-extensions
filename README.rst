appsembler-credentials-extensions
=============================

|pypi-badge| |travis-badge| |codecov-badge| |doc-badge| |pyversions-badge|
|license-badge|

The ``README.rst`` file should start with a brief description of the repository,
which sets it in the context of other repositories under the ``appsembler``
organization. It should make clear where this fits in to the overall edX
codebase.

Common package with apps for extensions for Open edX course/program certificates, badges, and other credentials types TBD.

Overview (please modify)
------------------------

The ``README.rst`` file should then provide an overview of the code in this
repository, including the main components and useful entry points for starting
to understand the code in more detail.

How to Develop
--------------
Install this in a working Open edX instance/devstack:

``` 
$ cd /edx/app/edxapp
$ source edxapp_env
$ pip install -e git+https://github.com/appsembler/appsembler_credentials_extensions.git
```

then add to INSTALLED_APPS:

```
[ 
"appsembler_credentials_extensions.apps.course_certs_extensions",
"appsembler_credentials_extensions.apps.badges_extensions",
]
```

Run the migrations:

```
$ cd /appsembler/app/edxapp
$ source edxapp_env
$ cd edx-platform
$ ./manage.py lms migrate appsembler_course_certs_extensions
```

then run the LMS or CMS service, like  `$ ./manage.py lms runserver --settings=devstack_appsembler`


Running tests
-------------
The following supports py.test/tox-driven automated testing. It will install the appropriate
release of edx-platform in a `virtualenv`.  Note that it doesn't currently run any 
assest compilation via paver, but just makes edx-platform modules available to the Python
shell that runs the tests. 

```
$ mkvirtualenv appsembler_credentials
$ workon appsembler_credentials
$ export EDX_PLATFORM_VERSION={one of Ficus|Ginkgo|Hawthorne}
$ make upgrade
$ make requirements
$ make test
```

Documentation
-------------

The full documentation is at https://appsembler-credentials-extensions.readthedocs.org.

License
-------

The code in this repository is licensed under the Apache Software License 2.0 unless
otherwise noted.

Please see ``LICENSE.txt`` for details.

How To Contribute
-----------------

Contributions are very welcome.

Please read `How To Contribute <https://github.com/appsembler/appsembler_credentials_extensions/blob/master/CONTRIBUTING.rst>`_ for details.

Even though they were written with ``edx-platform`` in mind, the guidelines
should be followed for Open edX code in general.

PR description template should be automatically applied if you are sending PR from github interface; otherwise you
can find it it at `PULL_REQUEST_TEMPLATE.md <https://github.com/appsembler/appsembler-credentials-extensions/blob/master/.github/PULL_REQUEST_TEMPLATE.md>`_

Issue report template should be automatically applied if you are sending it from github UI as well; otherwise you
can find it at `ISSUE_TEMPLATE.md <https://github.com/appsembler/appsembler-credentials-extensions/blob/master/.github/ISSUE_TEMPLATE.md>`_

Reporting Security Issues
-------------------------

Please do not report security issues in public. Please email technical@appsembler.com.

Getting Help
------------

Have a question about this repository, or about Open edX in general?  Please
refer to this `list of resources`_ if you need any assistance.

.. _list of resources: https://open.edx.org/getting-help


.. |pypi-badge| image:: https://img.shields.io/pypi/v/appsembler-credentials-extensions.svg
    :target: https://pypi.python.org/pypi/appsembler-credentials-extensions/
    :alt: PyPI

.. |travis-badge| image:: https://travis-ci.org/appsembler/appsembler-credentials-extensions.svg?branch=master
    :target: https://travis-ci.org/appsembler/appsembler-credentials-extensions
    :alt: Travis

.. |codecov-badge| image:: http://codecov.io/github/appsembler/appsembler-credentials-extensions/coverage.svg?branch=master
    :target: http://codecov.io/github/appsembler/appsembler-credentials-extensions?branch=master
    :alt: Codecov

.. |doc-badge| image:: https://readthedocs.org/projects/appsembler-credentials-extensions/badge/?version=latest
    :target: http://appsembler-credentials-extensions.readthedocs.io/en/latest/
    :alt: Documentation

.. |pyversions-badge| image:: https://img.shields.io/pypi/pyversions/appsembler-credentials-extensions.svg
    :target: https://pypi.python.org/pypi/appsembler-credentials-extensions/
    :alt: Supported Python versions

.. |license-badge| image:: https://img.shields.io/github/license/appsembler/appsembler-credentials-extensions.svg
    :target: https://github.com/appsembler/appsembler-credentials-extensions/blob/master/LICENSE.txt
    :alt: License
