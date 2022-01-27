import volume
import os
import logging

logging.basicConfig()

if os.fork() == 0:
    volume.client.run('VolRemote')

os.wait()

