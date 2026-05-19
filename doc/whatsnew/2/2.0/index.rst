What's new in Job Application Tracker 2.0.0?
--------------------------------------------
Release date: 2026-05-02


New Features
------------

- Official release of the multi-user version of the project. Everything now
  requires the use of a login, and job applications are stored on a per-user
  basis. Sub-features for the user include:

  - User registration, with email verification being required for account
    activation.
  - Password reset, via a link sent to the registered email address.
  - The ability to change your password, which is of course a requirement for
    any site like this. :smile:
  - Password complexity rules have been expanded.
  - The ability to change your email, again with verification to assure that the
    new email address was entered correctly.
  - Profile editing, where you can change/enter details about your name, and
    change your username.

- More consistency in page styling. For example, all pages dealing with the user
  login and profile now have a narrower body with a application header and a
  task header before the form.

- Improved About page.

- All actions surrounding job applications now enforces the login requirement,
  redirecting unauthenticated users to the login page, and preventing one user
  from accessing another user's data.

- The system layout now supports delivery of messages to the user, allowing the user to see things like success messages
  when changing passwords.

Internal Changes
----------------

- The project has transitioned from using Django's built-in authentication system, which was primarily used for
  administrator access to using `allauth <https://docs.allauth.org/en/latest/>`_, which provides much of the framework for
  authentication, registration and account management. Considerable work was done to customize the user experience,
  however, such as assuring that the account pages always render with the site layout.

- The project has transitioned from using a ``requirements.txt`` file to using the more modern `pyproject.toml
  <https://packaging.python.org/en/latest/guides/writing-pyproject-toml/>`_ file. This allows us to have both production
  and development dependencies, among other things.

- The project is now using `pylint <https://pylint.readthedocs.io>`_ to help assure code quality.

- The project is now under 100% test code coverage using the `unittest <https://docs.python.org/3/library/unittest>`_,
  again to help assure code quality.

- Added new user groups, which primarily right now control whether or not a user can change their password. The ``users``
  group, which allows changing of the password, is added automatically during registration.

What's new in Job Application Tracker 2.0.1?
--------------------------------------------
Release date: 2026-05-03

New Features
------------

- Added a new home page, with some of the latest news and instructions on use.

What's new in Job Application Tracker 2.0.2?
--------------------------------------------
Release date: 2026-05-03

New Features
------------

- Updated the permitted length of the field for job post URLs. The default of 200 characters for a URLField was just not
  cutting it, and I was having to save some of the URLs in the notes field instead. The field has been extended to 2048
  characters, so I can even store URLs for posts from sites like ZipRecruiter.
