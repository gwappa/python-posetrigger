Installation
=============

Software installation
----------------------

We recommend installing everything through `Anaconda3`_. Make sure your PC satisfies the :doc:`System requirements <requirements>`.

Find the environment file ``posetrigger.yaml`` from the repository, and run the following command in the terminal:

   .. code-block:: Bash

       $ conda env create -f posetrigger.yaml; conda activate posetrigger

You can change the name of the environment by giving the alternative as ``conda env create -n <name> -f posetrigger.yaml``.

.. note::

    Please be noted that Python version must be equal or above 3.7.
    Otherwise, some functionality won't work properly.
    

Hardware installation
----------------------

In addition, to make use of the trigger-output feature, you need to :doc:`prepare an output board <outputboards>`.

.. _Anaconda3: https://www.anaconda.com/
