MRP Areas
~~~~~~~~~

* Go to *Manufacturing > Configuration > MRP Areas* and define or edit
  any existing area. You can specify the working hours for every area.


You can check or uncheck the priorize_safety_stock flag on an area. When you do
this, you get one additional parameter:

* Safety stock lead date

The idea is that your area may be under tension at a given moment (maybe
some workers are off, maybe there is high demand from customers) and you
can barely keep up with the demand. In this case, you can set
Safety stock rebuild lead date to a date in the future at
which you anticipate that the situation will have been fixed. 
Until that date, the MRP Multi Level planner
will consume the safety stock without attempting to rebuild it, and only
resupply if the forecasted stock goes below zero.


Product MRP Area Parameters
~~~~~~~~~~~~~~~~~~~~~~~~~~~

* Go to *Manufacturing > Master Data > Product MRP Area Parameters* and set
  the MRP parameters for a given product and area.
