Last change: |today|

.. _exampleproject:

Example Project 
===============

This document describes how to use semi-ate in developer mode to create and run testflows and various tests on your tester or test environment.
We start from a small example project with a test flow of two individual tests. 


Open Project
------------

Open an maxiconda terminal:

   >>> (maxiconda) PS:> cd ~/repos            // or to the directory where you save your github repositories 
   >>> (maxiconda) PS:> git clone https://github.com/Semi-ATE/tb_semi_ate_example.git
   >>> (maxiconda) PS:> conda activate Semi-ATE
   >>> (Semi-ATE) PS:> spyder


than open in spyder the Project:


.. image:: images/openproject.png
  :alt:   open project in spyder
  :align: center



now spyder should look something like this (click on the picture to get a bigger size)
   
.. image:: images/spyder.png
  :width: 600
  :class: hover150
  :alt:   picture from spyder
  :align: center


On the upper right corner select 1. *Lab Control*, then 2. check if Mosquito has connection, 3.enable *Start Auto* and *use breakpoints*, 4. select Flow Group-> *engineering*

.. image:: images/lab_control.png
  :width: 400
  :class: hover150
  :alt:   picture from lab control
  :align: right

.. hint::

  If you do not have a connection to your broker, check that your broker (e.g. Mosuitto) is correctly installed and running.


The toolbar should now look like this

.. image:: images/run_flow.png
  :alt:   toolbar
  :align: center


Now we can start the test flow. Click on Run Control. 
Spyder opens and runs through an automatically created python file that includes all tests selected in the test flow.
That we have selected *use breakpoints* in the lab control is first stopped at the default breakpoint.
Unfortunately this is still necessary because otherwise spyder does not take into account the normal breakpoints that you can set directly in the editor.

.. image:: images/stop_onbreakpoint.png
  :alt:   stop on breakpoint
  :align: center
  
  
.. hint::

  If you use breakpoints in a test, the test time for a flow is 20-30% slower. This is noticeable with long tests.    
 
 
click on the continue exectution button. 

.. image:: images/clickcontinue.png
  :alt:   click continue
  :align: center

The program is now executed until the end of the test flow. It then stops and waits for further input from you.
You can then use the control buttons to end the program completely (with the stop button) or run it again (continue Button).

.. image:: images/lab_control_next.png
  :alt:   toolbar
  :align: center


To set breakpoints or edit a test, go to the ATE tab on the left. Double-click to open the corresponding test.

.. image:: images/edittest.png
  :alt:   edit parameter
  :align: center
  
To change limits or parameter names, select the test, with the right mouse button you get a menu, click on edit and the test wizard opens.


