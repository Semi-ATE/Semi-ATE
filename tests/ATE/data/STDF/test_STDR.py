from ATE.data.STDF import STDR
        

def test_STDR():
    
    stdr = STDR()

#   test unsigned byte value    
    ubyte_field = 5
    set_ubyte = 5;
    stdr.set_value(ubyte_field, set_ubyte)
    get_ubyte = stdr.get_value(5)
    assert set_ubyte == get_ubyte

    try:
        stdr.set_value(ubyte_field, -5)
        assert False
    except:
        assert True

    try:
        stdr.set_value(ubyte_field, 500)
        assert False
    except:
        assert True
