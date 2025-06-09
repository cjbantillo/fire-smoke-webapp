"""
Fire Detection System
A real-time fire-smoke-detection

Original Author: Sayed Gamal (sayyedgamall@gmail.com)
Remade by: Christian James Bantillo (bantillocj1@gmail.com)
Project: Finals Project for Graphics in Visual Computing CSC 126
"""

__version__ = '2.0.0'
__author__ = 'Sayed Gamal (Original), Christian James Bantillo (Remake)'
__email__ = 'sayyedgamall@gmail.com, bantillocj1@gmail.com'
__original_author__ = 'Sayed Gamal'
__remake_author__ = 'Christian James Bantillo'
__course__ = 'Graphics in Visual Computing CSC 126'
__project_type__ = 'Finals Project'

from .config import Config, setup_logging
from .fire_detector import Detector

__all__ = [
    'Config',
    'setup_logging',
    'Detector',
]
