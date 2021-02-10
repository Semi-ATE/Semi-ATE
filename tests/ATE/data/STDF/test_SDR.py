import os
import io
from tests.ATE.data.STDF.STDFRecordTest import STDFRecordTest
from ATE.data.STDF import SDR

#   Site Description Record
#   Function:
#   Contains the configuration information for one or more test sites,
#   connected to one testhead, that compose a site group.


def test_SDR():
    sdr("<")
    sdr(">")


def sdr(endian):

    #   ATDF page 31
    expected_atdf = "SDR:"
    #   record length in bytes
    rec_len = 0

    #   STDF page 35
    record = SDR(endian=endian)

    head_num = 1
    record.set_value("HEAD_NUM", head_num)
    rec_len += 1
    expected_atdf += str(head_num) + "|"

    site_grp = 1
    record.set_value("SITE_GRP", site_grp)
    rec_len += 1
    expected_atdf += str(site_grp) + "|"

    site_cnt = 3
    record.set_value("SITE_CNT", site_cnt)
    rec_len += 1
    #   There is no SITE_CNT field in the ATDF

    site_num = [0, 1, 2]
    record.set_value("SITE_NUM", site_num)
    rec_len += len(site_num) * 1
    for elem in site_num:
        expected_atdf += str(elem) + ","
    expected_atdf = expected_atdf[:-1] + "|"

    hand_typ = "HANDLER RASCO"
    record.set_value("HAND_TYP", hand_typ)
    rec_len += 1 + len(hand_typ)
    expected_atdf += hand_typ + "|"

    hand_id = "2234-21"
    record.set_value("HAND_ID", hand_id)
    rec_len += 1 + len(hand_id)
    expected_atdf += hand_id + "|"

    card_typ = "SMU TER"
    record.set_value("CARD_TYP", card_typ)
    rec_len += 1 + len(card_typ)
    expected_atdf += card_typ + "|"

    card_id = "SMU-3213"
    record.set_value("CARD_ID", card_id)
    rec_len += 1 + len(card_id)
    expected_atdf += card_id + "|"

    load_typ = "LOAD_HAL12345"
    record.set_value("LOAD_TYP", load_typ)
    rec_len += 1 + len(load_typ)
    expected_atdf += load_typ + "|"

    load_id = "LB-12345-A"
    record.set_value("LOAD_ID", load_id)
    rec_len += 1 + len(load_id)
    expected_atdf += load_id + "|"

    dib_typ = "DIB_HAL12345"
    record.set_value("DIB_TYP", dib_typ)
    rec_len += 1 + len(dib_typ)
    expected_atdf += dib_typ + "|"

    dib_id = "DIB-12345-D"
    record.set_value("DIB_ID", dib_id)
    rec_len += 1 + len(dib_id)
    expected_atdf += dib_id + "|"

    cabl_typ = "CABL_HAL12345"
    record.set_value("CABL_TYP", cabl_typ)
    rec_len += 1 + len(cabl_typ)
    expected_atdf += cabl_typ + "|"

    cabl_id = "CABL-12345-D"
    record.set_value("CABL_ID", cabl_id)
    rec_len += 1 + len(cabl_id)
    expected_atdf += cabl_id + "|"

    cont_typ = "CONT_HAL12345"
    record.set_value("CONT_TYP", cont_typ)
    rec_len += 1 + len(cont_typ)
    expected_atdf += cont_typ + "|"

    cont_id = "CONT-12345-D"
    record.set_value("CONT_ID", cont_id)
    rec_len += 1 + len(cont_id)
    expected_atdf += cont_id + "|"

    lasr_typ = "LASR_HAL12345"
    record.set_value("LASR_TYP", lasr_typ)
    rec_len += 1 + len(lasr_typ)
    expected_atdf += lasr_typ + "|"

    lasr_id = "LASR-12345-D"
    record.set_value("LASR_ID", lasr_id)
    rec_len += 1 + len(lasr_id)
    expected_atdf += lasr_id + "|"

    extr_typ = "EXTR_HAL12345"
    record.set_value("EXTR_TYP", extr_typ)
    rec_len += 1 + len(extr_typ)
    expected_atdf += extr_typ + "|"

    extr_id = "EXTR-12345-D"
    record.set_value("EXTR_ID", extr_id)
    rec_len += 1 + len(extr_id)
    expected_atdf += extr_id

    #    Test serialization
    #    1. Save SDR STDF record into a file
    #    2. Read byte by byte and compare with expected value

    w_data = record.__repr__()
    io_data = io.BytesIO(w_data)

    stdfRecTest = STDFRecordTest(io_data, endian)
    #   rec_len, rec_type, rec_sub
    stdfRecTest.assert_file_record_header(rec_len, 1, 80)
    #   Test HEAD_NUM, expected value num_bins
    stdfRecTest.assert_int(1, head_num)
    #   Test SITE_GRP, expected value head_num
    stdfRecTest.assert_int(1, site_grp)
    #   Test SITE_CNT, expected value site_cnt
    stdfRecTest.assert_int(1, site_cnt)
    #   Test SITE_NUM, expected value site_num
    stdfRecTest.assert_int_array(1, site_num)
    #   Test HAND_TYP, expected value hand_typ
    stdfRecTest.assert_ubyte(len(hand_typ))
    stdfRecTest.assert_char_array(len(hand_typ), hand_typ)
    #   Test HAND_ID, expected value hand_id
    stdfRecTest.assert_ubyte(len(hand_id))
    stdfRecTest.assert_char_array(len(hand_id), hand_id)
    #   Test CARD_TYP, expected value card_typ
    stdfRecTest.assert_ubyte(len(card_typ))
    stdfRecTest.assert_char_array(len(card_typ), card_typ)
    #   Test CARD_ID, expected value card_id
    stdfRecTest.assert_ubyte(len(card_id))
    stdfRecTest.assert_char_array(len(card_id), card_id)
    #   Test LOAD_TYP, expected value load_typ
    stdfRecTest.assert_ubyte(len(load_typ))
    stdfRecTest.assert_char_array(len(load_typ), load_typ)
    #   Test LOAD_ID, expected value load_id
    stdfRecTest.assert_ubyte(len(load_id))
    stdfRecTest.assert_char_array(len(load_id), load_id)
    #   Test DIB_TYP, expected value dib_typ
    stdfRecTest.assert_ubyte(len(dib_typ))
    stdfRecTest.assert_char_array(len(dib_typ), dib_typ)
    #   Test DIB_ID, expected value dib_id
    stdfRecTest.assert_ubyte(len(dib_id))
    stdfRecTest.assert_char_array(len(dib_id), dib_id)
    #   Test CABL_TYP, expected value cabl_typ
    stdfRecTest.assert_ubyte(len(cabl_typ))
    stdfRecTest.assert_char_array(len(cabl_typ), cabl_typ)
    #   Test CABL_ID, expected value cabl_id
    stdfRecTest.assert_ubyte(len(cabl_id))
    stdfRecTest.assert_char_array(len(cabl_id), cabl_id)
    #   Test CONT_TYP, expected value cont_typ
    stdfRecTest.assert_ubyte(len(cont_typ))
    stdfRecTest.assert_char_array(len(cont_typ), cont_typ)
    #   Test CONT_ID, expected value cont_id
    stdfRecTest.assert_ubyte(len(cont_id))
    stdfRecTest.assert_char_array(len(cont_id), cont_id)
    #   Test LASR_TYP, expected value lasr_typ
    stdfRecTest.assert_ubyte(len(lasr_typ))
    stdfRecTest.assert_char_array(len(lasr_typ), lasr_typ)
    #   Test LASR_ID, expected value lasr_id
    stdfRecTest.assert_ubyte(len(lasr_id))
    stdfRecTest.assert_char_array(len(lasr_id), lasr_id)
    #   Test EXTR_TYP, expected value extr_typ
    stdfRecTest.assert_ubyte(len(extr_typ))
    stdfRecTest.assert_char_array(len(extr_typ), extr_typ)
    #   Test EXTR_ID, expected value extr_id
    stdfRecTest.assert_ubyte(len(extr_id))
    stdfRecTest.assert_char_array(len(extr_id), extr_id)

    #    Test de-serialization
    #    1. Open STDF record from a file
    #    2. Read record fields and compare with the expected value

    inst = SDR("V4", endian, w_data)
    #   rec_len, rec_type, rec_sub
    stdfRecTest.assert_instance_record_header(inst, rec_len, 1, 80)
    #   Test HEAD_NUM, position 3, value of head_num variable
    stdfRecTest.assert_instance_field(inst, 3, head_num)
    #   Test SITE_GRP, position 4, value of site_grp variable
    stdfRecTest.assert_instance_field(inst, 4, site_grp)
    #   Test SITE_CNT, position 5, value of site_cnt variable
    stdfRecTest.assert_instance_field(inst, 5, site_cnt)
    #   Test SITE_NUM, position 6, value of site_num variable
    stdfRecTest.assert_instance_field(inst, 6, site_num)
    #   Test HAND_TYP, position 7, value of hand_typ variable
    stdfRecTest.assert_instance_field(inst, 7, hand_typ)
    #   Test HAND_ID, position 8, value of hand_id variable
    stdfRecTest.assert_instance_field(inst, 8, hand_id)
    #   Test CARD_TYP, position 9, value of card_typ variable
    stdfRecTest.assert_instance_field(inst, 9, card_typ)
    #   Test CARD_ID, position 10, value of card_id variable
    stdfRecTest.assert_instance_field(inst, 10, card_id)
    #   Test LOAD_TYP, position 11, value of load_typ variable
    stdfRecTest.assert_instance_field(inst, 11, load_typ)
    #   Test LOAD_ID, position 12, value of load_id variable
    stdfRecTest.assert_instance_field(inst, 12, load_id)
    #   Test DIB_TYP, position 13, value of dib_typ variable
    stdfRecTest.assert_instance_field(inst, 13, dib_typ)
    #   Test DIB_ID, position 14, value of dib_id variable
    stdfRecTest.assert_instance_field(inst, 14, dib_id)
    #   Test CABL_TYP, position 15, value of cabl_typ variable
    stdfRecTest.assert_instance_field(inst, 15, cabl_typ)
    #   Test CABL_ID, position 16, value of cabl_id variable
    stdfRecTest.assert_instance_field(inst, 16, cabl_id)
    #   Test CONT_TYP, position 17, value of cont_typ variable
    stdfRecTest.assert_instance_field(inst, 17, cont_typ)
    #   Test CABL_ID, position 18, value of cont_id variable
    stdfRecTest.assert_instance_field(inst, 18, cont_id)
    #   Test LASR_TYP, position 19, value of lasr_typ variable
    stdfRecTest.assert_instance_field(inst, 19, lasr_typ)
    #   Test LASR_ID, position 20, value of lasr_id variable
    stdfRecTest.assert_instance_field(inst, 20, lasr_id)

    #   Test ATDF output
    assert inst.to_atdf() == expected_atdf

    #   ToDo: Test JSON output
