import ulogger

from machine import RTC
#import ntptime

class Clock(ulogger.BaseClock):
    def __init__(self):
        self.rtc = RTC()
        
    def __call__(self) -> str:
        y,m,d,_,h,mi,s,_ = self.rtc.datetime ()
        return '%d-%d-%d %d:%d:%d' % (y,m,d,h,mi,s)
clock = Clock()
    
handlers = (
    ulogger.Handler(
        level=ulogger.INFO,
        colorful=True,
        fmt="&(time)% - &(level)% - &(name)% - &(fnname)% - &(msg)%",
        clock=clock,
        direction=ulogger.TO_TERM,
    ),
    ulogger.Handler(
        level=ulogger.WARN,
        fmt="&(time)% - &(level)% - &(name)% - &(fnname)% - &(msg)%",
        clock=clock,
        direction=ulogger.TO_FILE,
        file_name="logging.log",
        max_file_size=1024 # max for 1k
    )
)

def get_logger(name: str):
    return ulogger.Logger(name, handlers)
all = (get_logger)