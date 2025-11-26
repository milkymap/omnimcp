import logging 

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(filename)s - %(lineno)03d - %(levelname)s - %(message)s'
)

logging.getLogger('http').setLevel(logging.WARNING)
logger = logging.getLogger(name='omnimcp')


