import spidev
import time
spi = spidev.SpiDev()
# create spi object
spi.open(0,1)
spi.close()

