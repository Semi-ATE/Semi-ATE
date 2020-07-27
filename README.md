# Semi-ATE
<ins>**Semi**</ins>conductor <ins>**A**</ins>utomated <ins>**T**</ins>est <ins>**E**</ins>quipment

`Semi-ATE` is a tester- and instrument **AGNOSTIC** framework for **<ins>Semi</ins>conductor <ins>ATE</ins> ASIC testing** projects.

This means that the system is **not** build around a specific instrument (let's consider an ATE tester for a moment as a super instrument😋), it rather focuses on
organizing semiconductor testing in such a way that **all** use- (and special) corner cases have their well known place. This enables the users (read: DE's, TCE's, TE's & PE's) to focus on the **REAL** work, being writing fast and stable tests. Organizing tests into test-programs and test-programs in to flows is handled by wizards, so the only code that needs writing is the actual test! (motto: [Code is our enemy](http://www.skrenta.com/2007/05/code_is_our_enemy.html))

The `Semi-ATE` package is writen purely in Python (noarch) and provides besides libraries also a plugin to the [Spyder](https://www.spyder-ide.org/) IDE.

Still interested? Visit the [wiki](https://github.com/ate-org/Semi-ATE/wiki). 
