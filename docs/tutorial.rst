==========================
Tutorial: Creating an ePub
==========================

An ePub is really just a bunch of files compressed using zip. Unfortunately, the files are XML and XML is a bit ... particular. We have attempted to make the process as easy as possible.

Things you need to worry about
==============================

Much of the details of the ePub are handled for you, but not everything. Here are a few things to think about:

**Metadata.** There are three pieces of required metadata: title, language and a unique id. These pieces of metadata are set to reasonable defaults. Look at the section on :ref:`metadata` for more information.

**Templates.** The actual content of the ePub is in XHTML, formatted with CSS. Although you can override the templates for all the files that are used in the ePub, there are three you should be concerned about: ``article.html``, ``contents.html`` and ``title_page.html``. These templates are discussed in the :ref:`templates` section below.


Download ePub Generator
=======================

Get into a terminal or command line
git clone ...
download from github


Setting up the tutorial environment
===================================

We are going to start by setting up an isolated python environment. If you haven't installed ``virtualenv`` and ``virtualenvwrapper``, install them from the terminal prompt. ::

	easy_install virtualenv
	easy_install virtualenvwrapper

Add the following lines to your ~/.profile (or wherever it might go on windows)::

	export WORKON_HOME=\$HOME/.virtualenvs
	source /usr/local/bin/virtualenvwrapper_bashrc

Change into the epub project directory that you downloaded. ::

	cd epub

Now we are going to make the virtual environment::

	mkvirtualenv --no-site-packages epub

You now have created a new virtualenv that is isolated from your normal python installation. Your command prompt should have ``(epub)`` in front of it. That means you are using the isolated environment. Let's install Django to get things going::

	easy_install django

Change directories to the example project and create the database. Answer all the questions for creating the superuser::

	cd example
	python manage.py syncdb

Finally we'll load some sample data::

	python manage.py loaddata stories.json


Creating the ePub
=================

We'll do this from the python shell, although you could just as easily create a script for this. ::

	python manage.py shell

Start by importing a few models and modules. We'll use the ``os`` module and the Django ``settings`` module to create some paths. The ``EPub`` and ``Story`` models are for the actual creation of the ePub. ::

	import os
	from django.conf import settings
	from epub.models import EPub
	from simplestory.models import Story

Here are some paths we'll need later on. The ``img_path`` is the path for a Scalable Vector Graphic (SVG) logo that we'll embed. ``final_path`` is where the final ePub will be saved::

	img_path = os.path.abspath(os.path.join(settings.APP,'example','simplestory','fixtures','dailytimes.svg'))
	final_path = os.path.abspath(os.path.join(settings.APP,'example','testpub.epub'))

Create an empty :class:`EPub` object::

	e = EPub()

We'll set some of the metadata for this publication::

	e.metadata.title = "The Daily Times for Today"
	e.metadata.publisher = "Daily Times Publishing Inc"
	e.metadata.language = 'en-US'
	e.metadata.add_date('2009-07-05')
	e.metadata.add_date('2009-07-04', event="creation")
	e.metadata.modification_date = '2009-08-08'
	e.metadata.add_subject("Zombies")
	e.metadata.add_subject("Apocolypse")
	e.metadata.add_subject("Teen Angst")
	e.metadata.add_meta('price', 'USD 9.99')

The ePub format allows for the embedding of images. The image file is copied into the final document. Your XHTML documents can reference it using ``../images/filename.jpg``. The :meth:`EPub.add_image` method requires a path to the original file. It also allows a ``name`` parameter if you want to rename the file. The The :meth:`EPub.add_image` method tries to guess the MIME type of the file passed in, but you can override this by passing a ``mimetype`` parameter::

	e.add_image(img_path, name='logo.svg')

Adding the articles or chapters is very straightforward. The :meth:`EPub.add_article` method has two required parameters: ``title`` and ``content``, and two optional parameters: ``filename`` and ``author``. If the ``filename`` is left off, the ``title`` is modified to become the name of the file. If the ``author`` is included, the value is added as a ``contributor``. Here we get all the :class:`Story` objects, loop through them and add each to the publication::

	s = Story.objects.all()
	for item in s:
	    e.add_article(item.headline, item, item.slug+".html", item.byline)

At last we generate the actual ePub::

	e.generate_epub(final_path)
