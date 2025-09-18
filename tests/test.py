import sys
import logging

level_map = {
    0: logging.WARNING,
    1: logging.INFO,
    2: logging.DEBUG
}

level = level_map.get(45, logging.WARNING)

print(level)