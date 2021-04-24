Pipelines module
================

The pipelines module contains the definitions of our scoring pipelines. The risk scoring pipelines are implemented using the `imbalanced-learn <https://imbalanced-learn.org/stable/user_guide.html>`_ 
Pipeline allowing for defining sequences of **resampling, preprocessing and modeling steps as one estimators**. See scikit-learn 
`Pipelines and composite estimators <https://scikit-learn.org/stable/modules/compose.html#pipeline>`_  for more information.


.. literalinclude:: ../../../../pyro_risks/models/pipelines.py
  :language: PYTHON