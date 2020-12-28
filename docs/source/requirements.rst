System requirements
====================

.. contents:: Contents
   :local:
   :depth: 3

Base requirements
------------------

Before installing Pose-Trigger, make sure you have set up the following hardware:

1. **A linux computer** (we tested on `Ubuntu 18.04 LTS`_)
2. **a 16-bit monochrome video camera** from `ImagingSource`_ (e.g. refer to the :ref:`Reference setup`).

    .. note:: Other Video4Linux2-compliant cameras should also work with a few adjustments in the code, but will require some efforts.

3. For a faster working of DeepLabCut, **NVIDIA graphics board with a large amount of RAM** is required.

    .. note::

        For example, running DeepLabCut on ResNet-50 requires ~10.6 GB of RAM,
        so we use `GeForce RTX 2080 Ti`_ that has 11 GB on-board RAM (refer to the :ref:`Reference setup`).


Requirements for trigger-output generation
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

In addition to the pose-estimation feature, the trigger-output feature requires the followings:

1. The trigger-output server ("`FastEventServer`_").
2. An output board based on `Arduino`_ or its clone.

For Intel 64-bit CPUs, **Pose-Trigger comes with the working FastEventServer program**; you don't need to install it manually. For other architectures (e.g. AMD and ARM CPUs), refer to :doc:`Appendix: Compiling FastEventServer <fasteventserver>`.

Preparation of the Arduino-based output board may be non-trivial.
Please refer to :doc:`Appendix: Preparing an Output Board <outputboards>`.

.. _Reference setup:

Reference setup specifications
-------------------------------

We develop and test Pose-Trigger in the following environment:

Hardware
^^^^^^^^^

.. table:: Reference setup hardware specifications

    ============= ==============================================================
    Part name     Model type
    ============= ==============================================================
    CPU           3.7 GHz Core i7-9700K
    RAM           64 GB DDR4-3200
    GPU           NVIDIA GeForce RTX 2080 Ti (11 GB RAM)
    Camera        ImagingSource DMK 37BUX287
    Output board  Arduino UNO, rev. 2 (clone), with `arduino-fasteventtrigger`_
    ============= ==============================================================

Software
^^^^^^^^^

.. table:: Reference setup software environment

    ================== ====================================================
    Software           Specification
    ================== ====================================================
    Operating system   Ubuntu 18.04 LTS
    Python environment Anaconda3, Python 3.7.7
    CUDA Toolkit       version 10.1 (through `conda`)
    Tensorflow         version 1.13.1 (`tensorflow-gpu` package of `conda`)
    DeepLabCut         version 2.1.3
    NumPy              version 1.19.1 (through `conda`)
    ================== ====================================================

.. _Ubuntu 18.04 LTS: https://releases.ubuntu.com/18.04.5/
.. _ImagingSource: https://www.theimagingsource.com/
.. _GeForce RTX 2080 Ti: https://www.nvidia.com/en-eu/geforce/graphics-cards/rtx-2080-ti/
.. _FastEventServer: https://doi.org/10.5281/zenodo.3843623
.. _Arduino: https://store.arduino.cc/arduino-uno-rev3
.. _arduino-fasteventtrigger: https://doi.org/10.5281/zenodo.3515998
