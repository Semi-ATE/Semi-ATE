{%- set title = "Welcome to " + cookiecutter.project_name + "'s documentation!" -%}
{{ title }}
{{ "="*(title|length) }}

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   readme
   installation
   usage   
   contributing
   authors
   modules

Indices and tables
==================
* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
