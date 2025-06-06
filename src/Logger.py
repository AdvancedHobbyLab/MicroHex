import json
import time
import os

# Workaround for os.path not available in MicroPython
def path_exists(filename):
    try:
        os.stat(filename)
        return True
    except OSError:
        return False

class Logger:
    __log_file = ""
    __num_info = 0
    __num_warn = 0
    __num_err  = 0
    
    @classmethod
    def get_num_info(cls):
        return cls.__num_info
    
    @classmethod
    def get_num_warn(cls):
        return cls.__num_warn
    
    @classmethod
    def get_num_err(self):
        return self.__num_err
    
    @classmethod
    def setup_logger(cls, log_file, history=5):
        cls.__num_info = 0
        cls.__num_warn = 0
        cls.__num_err  = 0
        
        if history > 0:
            # Remove the oldest file
            filename = f"{log_file}.{history-1}.log"
            if path_exists(filename):
                os.remove(filename)
                
            # Shift files
            for i in reversed(range(1, history)):
                filename = f"{log_file}.{i-1}.log"
                filename2 = f"{log_file}.{i}.log"
                
                if path_exists(filename):
                    os.rename(filename, filename2)
        
        # Create the new file
        cls.__log_file  = f"{log_file}.0.log"
        with open(cls.__log_file, "w") as f:
            pass
        
    @classmethod
    def __log_msg(cls, level, msg):
        log = {"timestamp":time.time(), "level":level, "msg":msg}
        
        with open(cls.__log_file, "a+") as f:
            json.dump(log, f)
            f.write('\n')
    
    @classmethod
    def info(cls, msg):
        cls.__log_msg("INFO", msg)
        cls.__num_info += 1
        
    @classmethod
    def warn(cls, msg):
        cls.__log_msg("WARN", msg)
        cls.__num_warn += 1
        
    @classmethod
    def err(cls, msg):
        cls.__log_msg("ERROR", msg)
        cls.__num_err += 1
    