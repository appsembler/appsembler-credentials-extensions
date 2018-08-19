|pypi-badge| |travis-badge| |codecov-badge| |doc-badge| |pyversions-badge|
|license-badge|

Common package with apps for extensions for Open edX course/program certificates, badges, and other credentials types TBD.
It is a successor package to the poorly named ``appsembleredx`` which handle the same functions but is deprecated for the Ginkgo Open edX release.

Overview
--------

This package contains apps and tools to change or add functionality to various types of credentials within the Open edX 
services.  It is designed to be installed in the virtual env for the core LMS and CMS (Studio) services.  

``appsembler_credentials_extensions`` is currently compatible with the Ginkgo release of Open edX.

Course certificates and possibly badges will eventually move to the `credentials` package, so this package may need to be reworked to run in that service, or in both services.  

This package contains two Django apps, ``badges_extensions`` and ``course_certs_extensions``, and a separate module ``course_extensions``.  The Django apps can be used singly or together.  The ``course_extensions`` module will always be installed but its functionality is gated by feature flags.


``badges_extensions`` app
~~~~~~~~~~~~~~~~~~~~~~~~~

Currently provides just one feature:  A signal handler to turn off ``issue_badges`` on a course if the feature switch is enabled.
At present, course completion badges don't work properly with the Badgr backend, so we use course group badging and have to turn off ``issue_badges`` on the course, which would otherwise create a (broken) course completion badge.


``course_certs_extensions`` app
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Provides improved behavior and usability around course certificates for some of our customers' common use cases:


* Most customers using course certificates want to use a certificate-earning course mode for all courses.
* Most of our customers' courses are open-ended courses (no end dates).  They need grade and certificate information to display on the dashboard and progress pages without needing to 'end' the course.
* Customers commonly use no signatories or the same signatories across all courses, or otherwise have no changes to make in Studio between course certificates. It makes more sense to automatically create a course certificate for each course if the feature is enabled overall.
* Customers may use certificates on some courses and not others. 
* Customers may need to set up course certificates on a large number of courses at once.
* Customers may need to enable certificates on some self-paced courses but not others.
* Customers may need to include data from course extension fields in the HTML certificate webview.


This app automates the setup to use HTML course certificates normally done manually via Django admin or Studio.  These are all enabled
via feature switches in ``*.env.json`` files.

* Django data migration (LMS) to change any ``audit`` mode ``CourseModes`` to the default configured in the env.
* Django data migration (LMS) to enable HTML certificates overall in the platform (creates enabled ``CertificateGenerationConfiguration``)
* Django data migration (LMS) to enable and configure a ``CertificateHTMLViewConfiguration`` object based on settings
* Signal handler on course pre-publish to create a ``CourseMode`` object in the default mode (usually 'honor' or other certificate-earning mode)
* Signal handler on course pre-publish to set certificate-related course settings to good defaults for open-ended (no end date) courses

 - enable HTML View certs
 - set cert display to show before end
 - include cert/grade info on dashboard

* Signal handler on course pre-publish to create and activate (or keep inactive, depending on settings) a default course certificate, including signatories and signature images defined in platform configuration.  Signature images should be added to a ``cms/static/images`` folder in your theme and collected to the CMS static files directory.
* Monkeypatch of lms.djangoapps.certificates.views.webview to include any additional fields added to ``CourseDescriptor`` via this package's ``course_extensions`` mixin classes.
* Management command (CMS) to create and activate (or keep inactive, depending on settings) a course certificate for one, several, or all courses.  Also supports replacing existing default certificates.

``course_extensions`` module
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This module provides some extension classes for ``CourseDescriptor`` to:

* provide a lightweight alternative to edX's Credits implementation (from the ``credentials`` service).  It adds fields to define for a course: 

 - number of credits
 - credit provider
 - credit unit 
 - text description of accreditation conferred  

* provide a lightweight set of metadata fields about the type of instruction provided by the course.  It adds fields to define for a course:

 - instructional method (e.g., mixed in-person/online; classroom)
 - instruction location (a physical location; e.g., a certain campus)
 - field of study

* extend the OLX export/import methods to include fields from arbitrary mixin classes such as the above.
* provides a field type which validates that field values are among the set of defined choices.

This module uses monkeypatching to extend the ``xmodule.course_module.CourseDescriptor`` class with one or more of the above types of mixins as enabled by feature flags.

How to Develop
--------------
Install this in a working Open edX instance/devstack:
 
``bash
$ cd /edx/app/edxapp
$ source edxapp_env
$ pip install -e git+https://github.com/appsembler/appsembler_credentials_extensions.git
``

then add to INSTALLED_APPS:

``python
[ 
"appsembler_credentials_extensions.apps.course_certs_extensions",
"appsembler_credentials_extensions.apps.badges_extensions",
]
``


Run the migrations:

``bash
$ cd /appsembler/app/edxapp
$ source edxapp_env
$ cd edx-platform
$ ./manage.py lms migrate appsembler_course_certs_extensions
``

then run the LMS or CMS service, like  ``$ ./manage.py lms runserver --settings=devstack_appsembler 8000``


Running tests
-------------
The following supports py.test/tox-driven automated testing. It will install the appropriate
release of edx-platform in a `virtualenv`.  Note that it doesn't currently run any 
assest compilation via paver, but just makes edx-platform modules available to the Python
shell that runs the tests. 

```bash
$ mkvirtualenv appsembler_credentials
$ workon appsembler_credentials
$ export EDX_PLATFORM_VERSION={one of Ginkgo|Hawthorn}
$ make upgrade
$ make requirements
$ make test
```

You can also just run tests for parts of the package, like:

* $ make test_course_certs
* $ make test_badges
* $ make test_course_extensions


Documentation
-------------

Additional usage documentation (currenty private) is at https://github.com/appsembler/openedx-docs/blob/master/openedx/certificates.md.
Note that at present this document needs updating for ``appsembler_credentials_extensions``.

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


Reporting Security Issues
-------------------------

Please do not report security issues in public. Please email technical@appsembler.com.



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
