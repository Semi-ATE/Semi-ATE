# -*- coding: utf-8 -*-
"""
Created on Wed Oct 28 10:04:51 2026

@author: jung
"""

import socket
import time

def find_broker(host, port):
    for i in range(3):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(0.5)
        try:
            if s.connect_ex((host, port)) == 0:
                print("Mosquitto is ready")
                return True
        finally:
            s.close()
    
        print(f"Waiting for Mosquitto... ({i+1}/3)")
        time.sleep(0.5)
    return False
