FigRecipe API Reference
=======================

.. automodule:: figrecipe
   :members:
   :undoc-members:
   :show-inheritance:

Core Functions
--------------

.. autofunction:: figrecipe.subplots
.. autofunction:: figrecipe.save
.. autofunction:: figrecipe.reproduce
.. autofunction:: figrecipe.compose
.. autofunction:: figrecipe.validate
.. autofunction:: figrecipe.crop
.. autofunction:: figrecipe.info
.. autofunction:: figrecipe.extract_data

Recording Classes
-----------------

These classes are available via ``from figrecipe import utils`` or ``from figrecipe._wrappers import RecordingFigure, RecordingAxes``.

.. autoclass:: figrecipe._wrappers.RecordingFigure
   :members:
   :undoc-members:
   :show-inheritance:

.. autoclass:: figrecipe._wrappers.RecordingAxes
   :members:
   :undoc-members:
   :show-inheritance:

Style Management
----------------

.. autofunction:: figrecipe.load_style
.. autofunction:: figrecipe.unload_style
.. autofunction:: figrecipe.list_presets

Alignment Functions
-------------------

.. autofunction:: figrecipe.align_panels
.. autofunction:: figrecipe.align_smart
.. autofunction:: figrecipe.distribute_panels

GUI Editor
----------

.. autofunction:: figrecipe.gui

Diagram Class
-------------

.. autoclass:: figrecipe.Diagram
   :members:
   :undoc-members:
