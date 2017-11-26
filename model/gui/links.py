"""
View model for parsed link
classes:
    ParsedLink - named tuple representing parsed link    
"""

from collections import namedtuple

ParsedLink = namedtuple(
    "ParsedLink",
    "status url login campaign group ad comment"
)
