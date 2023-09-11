#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Aug  2 12:35:44 2023

@author: felipe.bortolletto

"""

from pathlib import Path
LOG_FILE = Path(__file__).parent / "log.txt"

class Log:
    def _log(self,msg):
        raise NotImplementedError(
            "Implemente o método log"
            )
        
    def log_error(self,msg):
        return self._log(f"Error: {msg}")
    
    def log_sucess(self,msg):
        return self._log(f"Sucesso: {msg}")
    

