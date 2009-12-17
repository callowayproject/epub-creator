from django import template
from django.template.loader import get_template

common_second_words = ('al', 'da', 'de', 'del', 'dela', 'della', 'di', 'du', 'el', 'la', 'le', 'mc', 'o\'', 'san', 'st', 'sta', 'van', 'vande', 'vanden', 'vander', 'von',)
common_third_words = ('van', 'de', )
common_suffixes = ("jr", "sr", "ii", "iii", "iv", "md", "phd")
def format_name(name):
    """
    Takes a name in the format ``first [middle/initial] last [suffix]`` and 
    returns it as ``last [suffix], first [middle/initial]``. Covers a wide variety
    of names, but not guaranteed to be perfect.
    
    The algorithm is:
    1. Normalize spacing and strip out periods and commas
    2. Split the name by spaces into a list
    2. If the last item is a suffix, merge it with the previous element
    3. Assume the last element is at least *part* of the last name: remove it from the list
    4. Assume the first element is at least *part* of the first name: remove it from the list
    5. If there are no more elements, return the lastname, firstname string
    6. If there are 2 or more elements left, and the second from the last item is in three-word-last-names: pop the last two elements off and add them to the last name
    7. If there is at least 1 element left, and the last item is in the two-word-last-names: pop the last element off and add it to the last name
    8. Anything left is assumed to be middle or compound first names, and added to the first name
    9. Return the last name, first name string
    """
    # strip out commas and periods
    new_name = name.replace(u',',u'').replace(u'.',u'').replace(u'  ', u' ')
    new_name.strip()
    # Split on spaces
    pieces = new_name.split()
    
    # Check for suffixes
    if pieces[-1].lower() in common_suffixes:
        suffix = pieces.pop(-1)
        pieces[-1] = " ".join([pieces[-1], suffix])
    
    # The last item is at least PART of the last name
    last_name = pieces.pop(-1)
    
    # The first item is at least PART of the first name
    first_name = pieces.pop(0)
    
    # Test for the easy 'firstname lastname' case
    length = len(pieces)
    if length == 0:
        return u'%s, %s' % (last_name, first_name)
    
    #check for 3-word last names, then 2-word last names
    if length >= 2 and pieces[-2].lower() in common_third_words:
        lname = [pieces.pop(-2), pieces.pop(-1), lastname]
        last_name = " ".join(lname)
    elif length >= 1 and pieces[-1].lower() in common_second_words:
        last_name = " ".join([pieces.pop(-1), last_name])
    
    # Anything else, put as middle name so add it to the first_name
    if len(pieces) > 0:
        first_name = " ".join([first_name,]+pieces)
    return u'%s, %s' % (last_name, first_name)


class EPubMetadata(object):
    """
    Manages the metadata for an :class:`EPubMetadata` object. It has some methods
    to make things simpler and some basic error detecting.
    """
    # certain keys can have many items. They are stored as a list of items.
    _has_many = ("identifier", "creator", "contributor", "subject", "relation", "date", "type", "meta")
    
    # From http://www.idpf.org/2007/opf/OPF_2.0_final_spec.html#Section2.2.6
    valid_roles = (
        'adp','ann','arr','art','asn','aut','aqt','aft','aui','ant','bkp','clb',
        'cmm','dsr','edt','ill','lyr','mdc','mus','nrt','oth','pht','prt','red',
        'rev','spn','ths','trc','trl',
    )
    valid_date_events = ['creation', 'publication', 'modification']
    _unique_id = None
    
    _default_metadata = lambda x: dict(title='', language='en', identifier=[], creator={}, contributor={}, subject=[], relation=[], date=[], type=[])
    
    def __init__(self, *args, **kwargs):
        """
        When the object is instantiated, it sets up a dictionary to manage the
        various types of data. Some tags are one and only one, some zero ore
        more, some are must have at least one with this attribute, but other can
        be there too. It's a bit confusing.
        
        By default, the required attributes (title, language, a unique identifier)
        are set to ``''``, ``'en'`` and a uuid, respectively. All can be overridden
        at a later time. The idea was to make it as easy as possible to generate
        a valid ePub.
        """
        import uuid
        self._metadata = self._default_metadata()
        self.set_unique_id(id="BookId", scheme="uuid", value=str(uuid.uuid4()))
        self._metadata.update(kwargs)
    
    def __setattr__(self, name, value):
        if name in ['_metadata','_unique_id', 'unique_id', 'creation_date', 'modification_date', 'publication_date',]:
            object.__setattr__(self, name, value)
        elif name in self._has_many:
            raise AttributeError("Please set the %s attribute using the add_%s method." % (name, name))
        else:
            self._metadata[name] = value
    
    def __getattr__(self, name):
        if name == '_metadata':
            return None
        else:
            return self._metadata.get(name, '')
    
    def update(self, metadata):
        """
        Merge another EPubMetadata instance with this one, overriding this one's
        values where necessary, adding where it can.
        """
        if metadata._unique_id:
            self.set_unique_id(id=metadata._unique_id['id'], scheme=metadata._unique_id['scheme'], value=metadata._unique_id['value'])
        
        for key, val in self._metadata.items():
            if key in ['creator', 'identifier']:
                self._metadata[key].extend(val)
            elif key in ['contributor','subject','relation']:
                self._metadata[key].update(val)
            else:
                self._metadata[key] = val
    
    def add_date(self, value, event=None):
        """
        Adds a ``date`` metadata item. The ``event`` parameter is optional, but
        can only be certain values if set. Since there is only three valid events,
        they are accessible as properties.
        
        :param value: The date, formatted as ``YYYY``, ``YYYY-MM``, or ``YYYY-MM-DD``
        :type value: ``string``
        :param event: Optional. One of :ref:``EPubMetada.valid_date_events``
        :type event: ``string``
        """
        if event and event in self.valid_date_events:
            self._metadata['date'].append({'value':value, 'opf:event':event})
        elif event and event not in self.valid_date_events:
            raise AttributeError("A data event must be empty or one of %s." % str(self.valid_date_events))
        else:
            self._metadata['date'].append({'value':value})
    
    def get_event_date(self, event):
        """
        A getter for a date of a specific event. Used by the special date properties
        
        :param event: The event whose date you want
        :type event: ``string``
        :returns: The value of the date, or ``None`` if it doesn't exist
        :rtype: ``string`` or ``None``
        """
        for item in self._metadata['date']:
            if item.has_key('event') and item['event'] == event:
                return item['value']
        return None
    
    creation_date = property(lambda x: x.get_event_date('creation'), lambda x,y: x.add_date(y, 'creation'))
    modification_date = property(lambda x: x.get_event_date('modification'), lambda x,y: x.add_date(y, 'modification'))
    publication_date = property(lambda x: x.get_event_date('publication'), lambda x,y: x.add_date(y, 'publication'))
    
    def add_creator(self, value, file_as=None, role="aut"):
        """
        There can be zero or more creators for an ePub. The parameters are optional,
        but attempts are made to make good defaults.
        
        If ``file_as`` is left out, it will assume the ``value`` is in the ``"first_name last_name"``
        format and convert it to ``"lastname, first_name"``.
        
        If ``role`` is left out, it defaults to ``aut`` or *author*\ .
        :param value: The creator's name
        :type value: ``string``
        :param file_as: Optional. The normalized version of the creator's name. 
                        **Default:** convert to ``last, first``
        :type file_as: ``string``
        :param role: The role of this creator. Must be one of :ref:``EPubMetadata.valid_roles``
                     **Default:** ``aut`` for *author*
        :type role: ``string``
        """
        if not file_as:
            file_as = format_name(value)
        if role and role not in self.valid_roles:
            raise AttributeError("A creator role must be empty or one of %s." % str(self.valid_roles))
        
        self._metadata['creator'][value] = {'opf:file-as':file_as, 'opf:role':role}
    
    def add_meta(self, name, content):
        """
        Sets a generic ``<meta>`` tag. All keyword arguments will be used as 
        attributes for the ``<meta>`` tag, except ``value``. If ``value`` is 
        one of the keyword arguments, it's value will be put within the opening 
        and closing ``<meta>`` tags.
        """
        if not self._metadata.has_key('meta'):
            self._metadata['meta'] = {}
        self._metadata['meta']['name'] = content
    
    def get_unique_id(self):
        """
        A getter for the :ref:``EPubMetadata.unique_id`` property. The unique_id
        is just a special version of the ``identifier`` metadatum. It is stored
        separately for convenience.
        
        :returns: The unique id identifier
        :rtype: ``dict(id, opf:scheme, value)`` 
        """
        return self._unique_id
    
    def set_unique_id(self, value, id, scheme=None):
        """
        Sets the :ref:``EPubMetadata.unique_id`` property. The unique_id
        is just a special version of the ``identifier`` metadatum. It is stored
        separately for convenience, and replaces any current ``identifier`` with 
        that ``id``.
        
        :param value: However you want to identify this ePub, use it. A uuid is
                      used by default when the object is instantiated
        :type value: ``string``
        :param id:  The unique way to reference this identifier. It can be anything.
                    ``BookId`` is used bt default when the obect is instantiated.
        :type id: ``string``
        :param scheme: How was this identifier generated. ``uuid`` is used by default
        :type scheme: ``string``
        """
        self._unique_id = {'id':id, 'opf:scheme':scheme, 'value':value}
        for item in self._metadata['identifier']:
            if item['id'] == id:
                item['opf:scheme'] = scheme
                item['value'] = value
                return
        self.add_identifier(value, id, scheme)
    
    unique_id = property(get_unique_id)
    
    def add_identifier(self, value, id=None, scheme=None):
        self._metadata['identifier'].append({'id':id, 'opf:scheme':scheme, 'value':value})
    
    def add_contributor(self, value, file_as=None, role="aut"):
        if not file_as:
            file_as = format_name(value)
        self._metadata['contributor'][value] = {'opf:file-as':file_as, 'opf:role':role}
    
    def add_subject(self, value):
        self._metadata['subject'].append(value)
    
    def add_relation(self, value):
        self._metadata['relation'].append(value)
    
    def add_type(self, value):
        self._metadata['type'].append(value)
    
    def _format_dict(self, tag, my_dict):
        """
        makes all the keys in the dict attributes, except the key 'value'
        """
        attrs = my_dict.copy()
        try:
            value = attrs.get('value','')
            del attrs['value']
        except KeyError:
            value = ''
        attributes = []
        for key, val in attrs.items():
            if val:
                attributes.append(u'%s="%s"' % (key, val.encode('ascii','xmlcharrefreplace')))
        output = [u'<dc:%s %s>' % (tag, " ".join(attributes)),value.encode('ascii','xmlcharrefreplace'),'</dc:%s>' % tag]
        return "".join(output)
    
    def __eq__(self, other):
        # TODO: Implement __eq__
        return False
    
    def __str__(self):
        ret = self.__unicode__().encode('ascii', 'xmlcharrefreplace')
        return ret
    
    def __unicode__(self):
        md_list = []
        for key, val in self._metadata.items():
            if key == 'meta':
                # Need a slightly different format
                for meta in val.items():
                    md_list.append(u'<meta name="%s" content="%s" />' % meta)
            elif isinstance(val, (list, tuple)):
                for item in val:
                    if isinstance(item, dict):
                        md_list.append(self._format_dict(key, item))
                    else:
                        md_list.append(u'<dc:%s>%s</dc:%s>' % (key, item.encode('ascii', 'xmlcharrefreplace'), key))
            elif isinstance(val, (dict)):
                for item_key, item_val in val.items():
                    item_val['value']=item_key
                    md_list.append(self._format_dict(key, item_val))
            else:
                md_list.append(u'<dc:%s>%s</dc:%s>' % (key, val.encode('ascii', 'xmlcharrefreplace'), key))
        return u'\n'.join(md_list)

class EPub(object):
    """
    An epub class
    """
    _metadata = None
    
    def __init__(self):
        self.articles = []
        self.images = []
        self.files = []
        self._metadata = EPubMetadata()
    
    def get_metadata(self):
        return self._metadata
    
    def set_metadata(self, value):
        if self._metadata:
            self._metadata.update(value)
        else:
            self._metadata = value
    metadata = property(get_metadata, set_metadata)
    
    # content
    def add_article(self, title, content, filename=None, author=None):
        if not filename:
            filename = "%s.html" % slugify(title)
        self.articles.append({'title': title, 'content':content, 'filename':filename})
        if author:
            self.metadata.add_contributor(author, role="aut")
    
    def add_image(self, filepath, name=None, mime_type=None):
        if not name:
            name = os.path.basename(filepath)
        if not mime_type:
            from mimetypes import guess_type
            mime_type = guess_type(filepath)[0]
        self.images.append({'orig':filepath, 'dest':'OEBPS/images/%s' % name, 'filename': name, 'mimetype':mime_type})
    
    def add_file(self, filepath, name=None, mime_type=None):
        if not name:
            name = os.path.basename(filepath)
        if not mime_type:
            from mimetypes import guess_type
            mime_type = guess_type(filepath)[0]
        self.files.append({'orig':filepath, 'dest':"OEBPS/%s" % name, 'filename': name, 'mimetype':mime_type})
    
    # Generation stuff
    def generate_opf(self):
        context = template.Context({
            'metadata': self.metadata, 
            'articles': self.articles,
            'images': self.images,
            'files': self.files,
        })
        tpl = get_template('epub/content.opf')
        return tpl.render(context=context)
    
    def generate_toc(self):
        tmpl = get_template('epub/toc.ncx')
        context = template.Context(dict(
            pub_id=self.metadata.unique_id['value'],
            title=self.metadata.title,
            articles=self.articles
        ))
        return tmpl.render(context)
    
    def generate_contents(self):
        tmpl = get_template('epub/contents.html')
        context = template.Context(dict(
            articles=self.articles
        ))
        return tmpl.render(context)
    
    def generate_titlepage(self):
        tmpl = get_template('epub/title_page.html')
        context = template.Context(dict(
            title=self.metadata.title,
            description=self.metadata.description,
            publisher=self.metadata.publisher,
            metadata=self.metadata
        ))
        return tmpl.render(context)
    
    def generate_article(self, article):
        tmpl = get_template('epub/article.html')
        context = template.Context(dict(
            article=article
        ))
        tmplstr = tmpl.render(context)
        return tmplstr.encode('ascii', 'xmlcharrefreplace')
    
    def generate_epub(self, filepath):
        import zipfile, os
        try:
            epub = zipfile.ZipFile(filepath, 'w', zipfile.ZIP_DEFLATED)
            tmpl_dir = os.path.join(os.path.dirname(__file__),'templates','epub')
            # Write the mimetype,without compression
            mtypepath = os.path.abspath(os.path.join(tmpl_dir,'mimetype'))
            epub.write(mtypepath,'mimetype', zipfile.ZIP_STORED)
            
            # Write META-INF/container.xml
            contpath = os.path.abspath(os.path.join(tmpl_dir, 'container.xml'))
            epub.write(contpath, 'META-INF/container.xml')
            
            # Write content.opf
            epub.writestr('OEBPS/content.opf', self.generate_opf())
            
            # Write toc.ncx
            epub.writestr('OEBPS/toc.ncx', self.generate_toc())
            
            # Write stylesheet
            stylepath = os.path.abspath(os.path.join(tmpl_dir,'stylesheet.css'))
            epub.write(stylepath, 'OEBPS/stylesheet.css')
            
            # write pagetemplate
            pagetmplpath = os.path.abspath(os.path.join(tmpl_dir,'pagetemplate.xpgt'))
            epub.write(pagetmplpath, 'OEBPS/pagetemplate.xpgt')
            
            # Write title page
            epub.writestr('OEBPS/text/title_page.html', self.generate_titlepage())
            
            # Write contents
            epub.writestr('OEBPS/text/contents.html', self.generate_contents())
            
            # Write images
            for img in self.images:
                epub.write(img['orig'], img['dest'])
            
            # Write articles
            for article in self.articles:
                epub.writestr('OEBPS/text/%s' % article['filename'], self.generate_article(article['content']))
        except Exception, e:
            print e
        
        if epub:
            epub.close()