=======
History
=======

1.0.0 (2022-06-05)
------------------

* Switch to Poetry package management.
* Add Python 3.10 and PyPy 3.6-3.9 testing.
* Migrate test infrastructure to Github Actions.

0.2.0 (2021-05-20)
------------------

* Improve encoding (~50%) and decoding (~25%) performance.
* Fix handling of combining characters that occur at the end of a file or before
  a control character. In those cases an implicit space (`U+0020`) is
  introduced.


0.1.1 (2018-12-31)
------------------

* Fix packaging error that prevented subpackage from being included in
  distribution.


0.1.0 (2018-12-30)
------------------

* First release on PyPI.
