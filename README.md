pyconair
========

Currently a working prototype.

Python API for communication via [ConAir](http://simple-solutions.de/shop/product_info.php?products_id=87)
433MHz - Ethernet Gateway or compatible devices.

The current prototypical state allows to send Intertechno commands to the radio controlled plugs.

Fixme
-----

Protocol layers are not correct.
While the details are part of the wire protocol the actual values must be derivied from the Higher levels.
Either by ratios, frequencies, timings or similar since the speed
