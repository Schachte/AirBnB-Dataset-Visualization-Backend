from distutils.core import setup

VERSION = '0.2'

setup(name='eventful',
      version=VERSION,
      author="Edward O'Connor",
      author_email='ted@eventful.com',
      url='http://api.eventful.com/libs/python/',
      download_url='http://api.eventful.com/libs/python/dist/eventful-%s.tar.gz' % VERSION,
      description='A client for the Eventful API.',
      license='MIT',
      long_description="""
A client for Eventful's API (http://api.eventful.com/).

Uses httplib2 and simplejson.
      """,
      py_modules=['eventful'],
      classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Software Development :: Libraries'
        ])
