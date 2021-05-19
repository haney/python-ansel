=======
History
=======

0.2.0 (TBD)
-----------

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
