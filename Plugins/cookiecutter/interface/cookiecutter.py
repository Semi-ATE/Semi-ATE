# -*- coding: utf-8 -*-
"""
Created on Tue Jun  9 18:59:08 2020

@author: hoeren
"""

__version__ = "1.2.3"


cookeicutter = {
    'plugin' : {
        'full_name' : "Tom Hören",
        'email' : "tom.hoeren@micronas.com",
        'name' : "Micronas",
        'short_description' : "ATE.org plugin for Micronas",
        'version' : __version__,
        'license' : "closed source",
        'readme.md' : true,
        'tests' : (false, {}),
        'docs' : true,
        'translation' : true,
    },
    'github' : {
        'server' : "micronas.github.com",
        'user' : "hoeren",
        'password' : None,
        'keyring' : true,
        'organization' : "Micronas",
        'channel' : "TDK",
    },
    'implementation' : {
        "importers" : {
            "maskset" : ("external", "Micronas-internal", "TDK"),
            "package" : ("internal", "", ""),
        },
        "exporters" : {
            "ERP" : ("extrnal", "Micronas-internal", "TDK"),
        },
        "instruments" : {
            "Jonathan Bradford" : {
                "K2000" : (  # ---> TDKMicronas.Jonathan_Branford.K2000
                    "Tektronix",  # manufacturere
                    "Keithley 2000",  # display name
                ),
                "XYZ" : (
                    "Manufacturer",
                    "Instrument",
                ),
            },
            "Tom Hören" : {
                "K3458A" : (
                    "Keysight",
                    "3458A"
                ),
            },
        },
        "tester" : {},
        "equipment" : {
            "Georg Sammel" : {
                "ATS-710" : (
                    "inTEST",
                    "actuator",
                    "temperature",
                ),
            },
            "Tom Hören" : {
                "G2G" : (
                    "Geringer",
                    "in-line-handler",
                    {}
                ),
                "SO1000" : (
                    "Rasco",
                    "batch-handler",
                ),
            },
            "Oliver Kawaletz" : {
                "QCheck" : (
                    "Micronas",
                    "batch-handler",
                    {},
                ),
            },
        },
    },
}


if __name__ == '__main__':

    # Importers
    print("Importers")
    for importer in cookiecutter['implementation']['importers']:
        implementation, package, channel = cookiecutter['implementation']['importers'][importer]
        print(f"   {importer}: ('{implementation}', '{package}', '{channel}')")

    print("Exporters")
    for exporter in cookiecutter['exporters']:
        implementation, package, channel = cookiecutter['implementation']['exporters'][exporter]
        print(f"   {exporter}: ('{implementation}', '{package}', '{channel}')")

    print("Instruments")
    for implementer in cookiecutter['implementation']['instruments']:
        for library in cookiecutter['implementation']['instruments'][implementer]:
            manufacturer, instrument = cookiecutter['implementation']['instruments'][implementer][library]
            print(f"   {library}: ({implementer}, {instrument}, {manufacturer})")


