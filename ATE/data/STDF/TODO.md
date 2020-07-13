# library
- [ ] split records.py in individual modules (same name as the records)
- [ ] surrond self.fields with `# fmt: off` and `# fmt: on` (prepare for black)
- [ ] add a check for python <= 3.7
- [ ] move support functions to __init__.py
- [ ] records.py should be empty now, so delete it
- [ ] create a list of all used types (combinations), and remove anything else from STDR (cfr also tests)
- [ ] remove all V3 records.
- [ ] find the memory extension spec on internet and add it to the docs (we lost it along the road)
- [ ] implement __repr__ and __str__ correctly (__str__ for print, and __repr__ for packing)
- [ ] move `self.info` to docstring of the class
- [ ] implement 'FPE' for all applicable records (cfr PTR) 
- [ ] re-enable the DT !!!
- [ ] re-enable the magic numbers !!!

# tests
- [ ] STDF needs heavy testing, at least 3 tests (smaller than min, bigger than max, nominal) per type.
- [ ] all non-STDR records need just ONE test (see that the __repr__ equals the record supplied upon instantiation.
- [ ] test that the 3 supported zippings work 