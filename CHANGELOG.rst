Change Log
----------

..
   All enhancements and patches to appsembler_credentials_extensions will be documented
   in this file.  It adheres to the structure of http://keepachangelog.com/ ,
   but in reStructuredText instead of Markdown (for ease of incorporation into
   Sphinx documentation and the PyPI description).
   
   This project adheres to Semantic Versioning (http://semver.org/).

.. There should always be an "Unreleased" section for changes pending release.


[0.1.4] - 2019-07-12
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* flake8 tests, Hawthorn tests


[0.1.3] - 2019-05-27
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* Update author
* Never change `CertifiateGenerationCourseSetting` from enabled to disabled if the course is self-paced.

[0.1.2] - 2019-04-02
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* Add a --noinput option to create_course_certs management command.


[0.1.1] - 2019-02-09
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* Include missing course_published signal handler to enable/disable self-generated certificates
* Update README.rst - fix codecov, remove unused badges (pypi etc.)
* tox.ini comment unused Py ver., make coverage add codecov package, make test comment Hawthorn
* Fix a test in test_signals for course_certs_extensions
* Fix README code blocks
* Update README.rst


[0.1.0] - 2018-08-16
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Initial version ported from `appsembleredx <https://github.com/appsembler/appsembleredx/>`_.
Ready for inclusion in Ginkgo edx-platform.
 