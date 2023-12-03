import logging

logging.basicConfig(
    format='%(asctime)s %(levelname)-8s [%(filename)s:%(lineno)d %(message)s',
    datefmt='[%d.%m.%Y-%H:%M%S]',
    filename='logfile.log',
    filemode='w',
    encoding='utf-8',
    level=logging.INFO
)