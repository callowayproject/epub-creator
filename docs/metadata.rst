.. _metadata:

========
Metadata
========

Metadata for a publication is handled by the :class:`EPubMetadata` class. When you instantiate an :class:`EPub` object, an empty :class:`EPubMetadata` object is created with default values for the required elements: ``title``, ``indicator``, ``language``.

There are several standard metadata tags:

* `title <http://www.idpf.org/2007/opf/OPF_2.0_final_spec.html#Section2.2.1>`_
  *Required.* The title of the publication. Although the specification allows
  for more than one ``title`` element, we only allow one. ::
  
  	epub = EPub()
  	epub.metadata.title = 'My Cool Publication'

* `creator <http://www.idpf.org/2007/opf/OPF_2.0_final_spec.html#Section2.2.2>`_
  *Optional.* A primary creator or author of this publication, with each
  person in their own element. For publications with multiple articles, the
  authors should be listed as ``contributor`` elements (in fact :class:`EPub`
  will do it for you when you add an article). 
  
  There are two *optional* attributes: ``file_as`` and ``role``. The 
  ``file-as`` attribute is to specify a normalized form of the contents,
  suitable for machine processing. ``EPubMetadata`` attempts to convert the
  value to a ``lastname, firstname`` format if the attribute is not specified.
  
  The ``role`` attribute must be one of those listed `in the specification <http://www.idpf.org/2007/opf/OPF_2.0_final_spec.html#Section2.2.6>`_. It defaults to ``aut``. ::
  
  	epub = EPub()
  	epub.metadata.add_creator('Rev. Dr. Martin Luther King Jr.')
  	# The resulting element would look like:
  	# <dc:creator opf:file-as="King Jr, Rev Dr Martin Luther" opf:role="aut">
  	#    Rev. Dr. Martin Luther King Jr.
  	# </dc:creator>
  	epub.metadata.add_creator('Jean Claude Van Damme', file_as='Van Damme, J C', role='edt')
  	# The resulting element would look like:
  	# <dc:creator opf:file-as="Van Damme, J C" opf:role="edt">
  	#    Jean Claude Van Damme
  	# </dc:creator>

* `subject <http://www.idpf.org/2007/opf/OPF_2.0_final_spec.html#Section2.2.3>`_
  *Optional.* Arbitrary keywords or phrases describing what the publication is
  about. ::
  
  	epub = EPub()
  	epub.metadata.add_subject('Entertainment')
  	epub.metadata.add_subject('Mary Poppins')

* `description <http://www.idpf.org/2007/opf/OPF_2.0_final_spec.html#Section2.2.4>`_
  *Optional.* The description of the publication's content. ::
  
  	epub = EPub()
  	epub.metadata.description = "An exposé of the immoral events leading to the tragic death of Mary Poppins."

* `publisher <http://www.idpf.org/2007/opf/OPF_2.0_final_spec.html#Section2.2.5>`_
  *Optional.* An entity responsible for making the resource available. 
  Examples of ``publisher`` include a person, organization, or service. ::
  
  	epub = EPub()
  	epub.publisher = "The Daily Times, LLC"

* `contributor <http://www.idpf.org/2007/opf/OPF_2.0_final_spec.html#Section2.2.6>`_
  *Optional.* Contributors are identical to creators, only implying less 
  significance in contribution to the whole work. There can be more than one, 
  and they have ``file_as`` and ``role`` attributes, which have the same 
  defaults as the ``creator`` element.
  
  When you add an article with :meth:`EPub.add_article()` and specify an 
  ``author``, a ``contributor`` element is added automatically. ::
  
  	epub = EPub()
  	epub.add_article(title='Awesome Article', content=my_content_var, author='Johnny Appleseed')
  	# A contributor element is added for Johnny Appleseed with a role of 'aut'
  	
  	epub.metadata.add_contributor('P T Barnum', role='ill')
  	# Adds an illustrator contributor of Barnum, P T

* `date <http://www.idpf.org/2007/opf/OPF_2.0_final_spec.html#Section2.2.7>`_
  *Optional.* The date of publication, in the form ``YYYY`` or ``YYYY-MM`` or
  ``YYYY-MM-DD``. The optional ``event`` attribute can specify: ``creation``,
  ``publication``, or ``modification``. The :class:`EPubMetadata` has three
  attributes that serve as shortcuts to setting and getting specific events:
  ``EPubMetadata.creation_date``, ``EPubMetadata.modification_date``, and 
  ``EPubMetadata.publication_date``. ::
  
  	epub = EPub()
  	epub.metadata.add_date('2009-01-01')
  	# Sets a generic publication date
  	epub.metadata.add_date('2008-05', event='creation')
  	# Sets a creation date
  	epub.metadata.creation_date
  	# returns '2008-05'
  	epub.metadata.modification_date = '2010'
  	# Same as: epub.metadata.add_date('2010', event='modification')

* `type <http://www.idpf.org/2007/opf/OPF_2.0_final_spec.html#Section2.2.8>`_
  *Optional.* The nature or genre of the content of the resource. Type 
  includes terms describing general categories, functions, genres, or 
  aggregation levels for content. Wikipedia has a list of
  `literary genres <http://en.wikipedia.org/wiki/Literary_genre>`_. To 
  describe the physical or digital manifestation of the resource, use the
  ``format`` element. ::
  
  	epub = EPub()
  	epub.metadata.add_type('Fiction')
  	epub.metadata.add_type('Comedy')
  	epub.metadata.add_type('Romance')
  
* `format <http://www.idpf.org/2007/opf/OPF_2.0_final_spec.html#Section2.2.9>`_
  *Optional.* The specifications say "The media type or dimensions of
  the resource. and suggest using MIME types. It doesn't make any sense 
  to me. I'd recommend not using this. ::
  
  	epub = EPub()
  	epub.metadata.format = 'US Letter'

* `identifier <http://www.idpf.org/2007/opf/OPF_2.0_final_spec.html#Section2.2.10>`_
  *Required.* A string or number used to uniquely identify the resource. One 
  set up for you at the creation of the :class:`EPub` object. You can override
  this with :meth:`EPub.metadata.set_unique_id`. The unique id requires one
  attribute, ``id``, which is unique across all publication ``identifier``
  elements, and optionally a ``scheme`` attribute to identify the system or
  authority that assigned or created the value of the identifier (ISBN, uuid, 
  URL, etc.)
  
  You can add additional ``identifier`` elements with or without the ``id``
  and ``scheme`` attributes. ::
  
  	epub = EPub()
  	epub.metadata.unique_id
  	# returns the automatically generated id as a dictionary.
  	epub.metadata.set_unique_id('1-60239-243-9', id='BookId', scheme='ISBN')
  	epub.metadata.add_identifier('978-1-60239-243-9', scheme='ISBN-13')

* `source <http://www.idpf.org/2007/opf/OPF_2.0_final_spec.html#Section2.2.11>`_
  *Optional.* If this publication was derived from a prior resource, indicate
  from which resource it was derived using a formal identification system. ::
  
  	epub = EPub()
  	epub.metadata.source = 'http://www.example.com/booknotes/'

* `language <http://www.idpf.org/2007/opf/OPF_2.0_final_spec.html#Section2.2.12>`_
  *Required.* By default it is set to ``en``. You can change it to any two- or
  three-letter value in `ISO 639.2 <http://www.loc.gov/standards/iso639-2/langhome.html>`_ and you can add a two-
  letter `country abbrviation <http://www.iso.org/iso/country_codes/iso_3166_code_lists/english_country_names_and_code_elements.htm>`_ to specify a country-specific dialect such as ``en-US`` or ``en-GB``. ::
  
  	epub = EPub()
  	epub.metadata.language = 'fr-CA'

* `relation <http://www.idpf.org/2007/opf/OPF_2.0_final_spec.html#Section2.2.13>`_
  *Optional.* An identifier of an auxiliary resource and its relationship to
  the publication. There can be more than one ``relation`` element. ::
  
  	epub = EPub()
  	epub.metadata.add_relation('http://www.example.com/errata.html')
  	epub.metadata.add_relation('ISBN:1-60239-243-9')

* `coverage <http://www.idpf.org/2007/opf/OPF_2.0_final_spec.html#Section2.2.14>`_
  *Optional.* Typically, coverage will include spatial location (a place name
  or geographic coordinates), temporal period (a period label, date, or date
  range) or jurisdiction (such as a named administrative entity). Recommended
  best practice is to select a value from a controlled vocabulary (for
  example, the `Thesaurus of Geographic Names <http://www.getty.edu/research/tools/vocabulary/tgn/index.html>`_) and to use, where
  appropriate, named places or time periods in preference to numeric
  identifiers such as sets of coordinates or date ranges. ::
  
  	epub = EPub()
  	epub.metadata.coverage = 'Italy, 1440-1560'

* `rights <http://www.idpf.org/2007/opf/OPF_2.0_final_spec.html#Section2.2.15>`_
  *Optional.* A statement about rights held in and over the publication.
  Rights information often encompasses Intellectual Property Rights (IPR), 
  Copyright, and various Property Rights. ::
  
  	epub = EPub()
  	epub.metadata.rights = 'Copyright © 2009 by Digital Times, LLC. All rights reserved.'


* `meta <http://www.idpf.org/2007/opf/OPF_2.0_final_spec.html#Section2.2>`_
  *Optional.* This is the catch-all metadata tag. Anything not specified 
  above, can be specified here, as long as it applies to the whole
  publication.
  
  When adding the meta information, you must specify the name of the metadata
  and the content of the metadata ::
  
  	epub = EPub()
  	epub.metadata.add_meta(name="price", currency="USD", value="9.99")
  	# The tag generated is: <meta name="price" content="USD 9.99" />

