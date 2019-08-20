import subprocess
import time
print('Running ethtool command')
subprocess.call(['sudo', 'ethtool', '-s','enp1s0', 'wol','g' ])
time.sleep(10)
subprocess.call(['sudo', 'ethtool', '-s','enp1s0', 'wol','g' ])
