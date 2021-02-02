from ATE.data.STDF import STDR
        

def test_STDR():
    
    stdr = STDR()

#   test unsined byte value    
    ubyte_field = 5
    set_ubyte = 5;
    stdr.set_value(ubyte_field, set_ubyte)
    get_ubyte = stdr.get_value(5)
    assert set_ubyte == get_ubyte

    try:
        stdr.set_value(ubyte_field, -5)
        print("Negative test for unsigned byte : FAIL")
        assert False
    except:
        print("Negative test for unsigned byte : PASS")
        assert True

    try:
        stdr.set_value(ubyte_field, 500)
        print("Over-range test exception : FAIL")
        assert False
    except:
        print("Over-range test exception : PASS")
        assert True
