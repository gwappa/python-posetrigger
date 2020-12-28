Appendix: Compiling FastEventServer
====================================

.. contents:: Contents
   :local:
   :depth: 3

Pose-Trigger makes use of the `FastEventServer <https://doi.org/10.5281/zenodo.3843623>`_ project to perform low-latency, high-throughput trigger-output generation.

If you use the 64-bit Intel CPU, you probably don't have to compile FastEventServer yourself because Pose-Trigger comes with a working program.
In case you use AMD, ARM etc, however, you have to have your own FastEventServer binary.

.. note::

	In case you compile the program for any additional architecture, we appreciate it very much if you could **file a Pull Request** to the Pose-Trigger repository (or send the binary file to us)!

Cloning the repository
-----------------------

It contains the submodule called ``libks``, so you have to populate this directory using ``git submodule update``:

.. code-block:: Bash

    $ git clone https://github.com/gwappa/FastEventServer.git
    $ cd FastEventServer
    $ git submodule update

Compiling the program
----------------------

Running ``make`` in the repository root should compile and update the program ``FastEventServer_linux_<bitwidth>``.

Installing the program to Pose-Trigger
---------------------------------------

Pose-Trigger has its own ``bin`` directory inside, and looks up the appropriate program file using the ``lscpu`` command. **Be sure to rename your FastEventServer program accordingly!**

Finding the architecture of your computer
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Running the ``lscpu`` command on your Linux computer will generate the information about the CPU:

.. code-block:: Bash

    $ lscpu # below is the output of this command
    Architecture:        x86_64 # in case of Intel 64-bit CPU
    ...

Please note the output on the "Architecture" field, and **rename your FastEventServer program** to ``FastEventServer_linux_<Architecture>`` (e.g. ``FastEventServer_linux_x86_64`` in the above case).

Finding where to install
^^^^^^^^^^^^^^^^^^^^^^^^^

As mentioned above, Pose-Trigger looks for its own ``bin`` directory, i.e. ``<path/to/python/posetrigger>/bin``.

You can check out the exact value of ``<path/to/python/posetrigger>`` by running:

.. code-block:: Bash

    $ python -c "import posetrigger; print(posetrigger.__file__)"
    /home/mouse/anaconda3/envs/posetrigger/lib/python3.7/site-packages/posetrigger/__init__.py

Installation example
^^^^^^^^^^^^^^^^^^^^^

Together, you can install the FastEventServer binary e.g. by running:

.. code-block:: Bash

    $ make # compile
    $ CPUARCH=`lscpu | grep Arch | sed -e 's/Architecture: \+/g'` # detect architecture
    $ ROOTDIR=`python -c "import posetrigger; print(posetrigger.__file__)" | xargs dirname`
    $ BINDIR="$ROOTDIR/bin" # identify the directory to install
    $ cp FastEventServer_linux_64bit "$BINDIR/FastEventServer_linux_$CPUARCH" # copy the file
