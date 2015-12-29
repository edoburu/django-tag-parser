
Version 2.2 (git)
-----------------

* Support ``@register.tag`` directly on the class

Version 2.1
-----------

* Added Django 1.8 support

Version 2.0.1
-------------

* Fix ``BaseAssignmentOrInclusionNode.get_context_data``.
* Fix passing ``template`` to ``BaseAssignmentOrInclusionNode.get_value(.. **tag_kwargs)`` when it's not in ``allowed_kwargs``.

Version 2.0
-----------

* Added Python 3 support.
* Added ``end_tag_name`` support.

Version 1.1
-----------

* Add ``BaseAssignmentOrOutputNode`` to support tags similar to ``{% trans .. as .. %}`` and ``{% url .. as .. %}``.
* **Backwards incompatible:**: The arguments of ``BaseAssignmentOrInclusionNode.get_value()`` also receive the ``context`` now.
  So ``get_value(self, *tag_args, **tag_kwargs)`` becomes: ``get_value(self, context, *tag_args, **tag_kwargs)``.
  If you use the positional arguments, update your method signature.

Version 1.0.3
-------------

* Fix ``BaseAssignmentOrInclusionNode`` to support positional arguments


Version 1.0.2
-------------

* Fix ``BaseAssignmentOrInclusionNode``, used self instead of cls


Version 1.0.1
-------------

* Fixed reversed arguments in ``compile_args`` / ``compile_kwargs``
* Fix ``BaseAssignmentOrInclusionNode`` to pass the compile settings.


Version 1.0.0
-------------

First PyPI release.
