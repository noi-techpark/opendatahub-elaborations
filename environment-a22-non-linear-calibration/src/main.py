from dataprocessor.DataProcessor import Processor
import logging

f = Processor()
log = logging.getLogger()

def main():
    log.info('Elaboration start')
    f.calc_by_station();
    log.info('Elaboration end')

if __name__ == "__main__":
    main()
    