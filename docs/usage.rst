=====
Usage
=====

To use ANSEL Codecs in a project

.. code:: python

    import ansel

    ansel.register()

The :code:`register` function registers each of the encodings supported by
the ansel module. Once registered, they can be used with any of the functions
of the :py:mod:`codecs` module or other functions that rely on codecs, for
example:

.. code:: python

    with open(filename, "r", encodings="ansel") as fp:
        fp.read()

Will open the file :code:`filename` for read with the "ansel" encoding.

Encodings
---------
The following encodings are provided and registered with the :py:mod:`codecs`
module:

======  =======================================================================
Codec   Description
======  =======================================================================
ansel   American National Standard for Extended Latin Alphabet Coded Character
        Set for Bibliographic Use (ANSEL_).

gedcom  GEDCOM_ extensions to ANSEL.
======  =======================================================================

Limitations
-----------

Pythons :py:func:`open` uses the :py:class:`codecs.IncrementalEncoder`
interface, however it doesn't invoke
:py:func:`codecs.IncrementalEncoder.encode` with `final=True`. This prevents
the final character written from being emitted to the stream. For example:

.. code:: python

    parts = ["P", "a", "\u030A", "l"]
    with open("tmpfile", "w", encoding="ansel") as fp:
        for part in parts:
            fp.write(part)

will write the bytes:

.. csv-table::

    ``0x50`` P, ``0xEA`` ◌̊, ``0x61`` a 

Note that the last character, 'l', does not appear in the byte sequence.

Related functions like :py:func:`codecs.open` have similar issues. They don't
rely on the :py:func:`codecs.IncrementalEncoder`, and instead use the
:py:func:`codecs.encode` function. Since each write is considered atomic,
combining characters split across multiple write calls are not handled
correctly:

.. code:: python

    with codecs.open("tmpfile", "w", encoding="ansel") as fp:
        for part in parts:
            fp.write(part)

will write the bytes:

.. csv-table::

    ``0x50`` P, ``0x61`` a, ``0xEA`` ◌̊, ``0x6C`` l

Note that while all of the bytes were written, the combining character
follows the character it modifies. In ANSEL, the combining character should
be before the character it modifies.

To avoid these issues, manually encoding and writing the parts is
recommended. For example:

.. code:: python

    with codecs.open("tmpfile", "wb") as fp:
        for part in codecs.iterencode(parts, encoding="ansel"):
            fp.write(part)

will write the bytes:

.. csv-table::

    ``0x50`` P, ``0xEA`` ◌̊, ``0x61`` a, ``0x6C`` l

This version writes the correct byte sequence.


.. _ANSEL: https://en.wikipedia.org/wiki/ANSEL
.. _GEDCOM: https://en.wikipedia.org/wiki/ANSEL#GEDCOM