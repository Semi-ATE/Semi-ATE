import os
import xml.etree.ElementTree as tree


DEVICE_ID = 'SCT-82-1F'


def create_xml_file(file, new_file, device_id):
    if os.path.exists(new_file):
        os.remove(new_file)

    et = tree.parse(file)
    root = et.getroot()
    for cl in root.findall("CLUSTER"):
        item = cl.find("TESTER")
        if item is not None:
            item.text = device_id

    for st in root.findall("STATION"):
        item = st.find("STATION1")
        ts = item.find('TESTER1')
        ts.text = device_id

    et.write(new_file)
