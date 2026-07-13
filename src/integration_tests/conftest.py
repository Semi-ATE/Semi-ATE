# -*- coding: utf-8 -*-
import sys
import asyncio
import pytest

if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    

def pytest_configure(config):
    config.addinivalue_line(
        "markers",
        "asyncio: mark test as asyncio"
    )

# Windows Event Loop Policy
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())    
