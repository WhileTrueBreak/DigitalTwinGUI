from harvesters.core import Harvester
import numpy as np  # This is just for a demonstration.
h = Harvester()

h.update()
print(len(h.device_info_list))
