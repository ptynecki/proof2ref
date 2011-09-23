proof2ref v0.2
==============

Automatically replaces theorems proofs in the *.miz files with available references.

How to use:
===========
For the single file (without *.miz extension):
<pre>python proof2ref.py -f text/filename</pre>

For the all files from text directory:
<pre>python proof2ref.py -d text</pre>

For the single file (without *.miz extension) with generated report (report.txt):
<pre>python proof2ref.py -f text/filename -r</pre>

For the all files from text directory with generated report (report.txt):
<pre>python proof2ref.py -d text -r</pre>

Remember to set up mizarPath inside of the script.

Requirments:
============
[Mizar 7.12+](http://mizar.org/), [Python 2.5+](http://python.org/), [lxml 2.3+](http://lxml.de/)

More info:
==========
Mizar: [mizar.org](http://mizar.org)
