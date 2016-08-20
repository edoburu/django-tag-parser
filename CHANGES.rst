
Version 3.0 (git)
-----------------

* Support ``@register.tag`` directly on the class


Version 2.1 (2015-04-09)
------------------------

* Added Django 1.8 support


Version 2.0.1 (2015-01-26)
--------------------------

* Fix ``BaseAssignmentOrInclusionNode.get_context_data``.
* Fix passing ``template`` to ``BaseAssignmentOrInclusionNode.get_value(.. **tag_kwargs)`` when it's not in ``allowed_kwargs``.


Version 2.0 (2014-10-14)
------------------------

* Added Python 3 support.
* Added ``end_tag_name`` support.


Version 1.1 (2014-05-24)
------------------------

* Add ``BaseAssignmentOrOutputNode`` to support tags similar to ``{% trans .. as .. %}`` and ``{% url .. as .. %}``.
* **Backwards incompatible:**: The arguments of ``BaseAssignmentOrInclusionNode.get_value()`` also receive the ``context`` now.
  So ``get_value(self, *tag_args, **tag_kwargs)`` becomes: ``get_value(self, context, *tag_args, **tag_kwargs)``.
  If you use the positional arguments, update your method signature.


Version 1.0.3 (2013-10-08)
--------------------------

* Fix ``BaseAssignmentOrInclusionNode`` to support positional arguments


Version 1.0.2 (2013-09-25)
--------------------------

* Fix ``BaseAssignmentOrInclusionNode``, used self instead of cls


Version 1.0.1 (2013-08-14)
--------------------------

* Fixed reversed arguments in ``compile_args`` / ``compile_kwargs``
* Fix ``BaseAssignmentOrInclusionNode`` to pass the compile settings.


Version 1.0.0 (2013-02-16)
--------------------------

First PyPI release.
