# -*- coding: utf-8 -*-
"""
Test file for NeuroskyECG
"""

from .neurosky_ecg import NeuroskyECG

import sys





target_port = 'COM3'
#target_port = 'devA/tty.XXXXXXX'  #change this to work on OSX

try:
    nskECG = NeuroskyECG(target_port)
except serial.serialutil.SerialException:
    print("Could not open target serial port: %s" % target_port)
    sys.exit(1)

#optional call, default is already 1
nskECG.setHRVUpdate(1) #update hrv every 1 detected pulses

# start running the serial producer thread
nskECG.start()


# this loop is the consumer thread, and will pop 
# dict values (with 'timestamp', 'ecg_raw', and 'leadoff'
# from the internal buffer and run the analysis on the 
# data.

cur_hrv = None #whatever the current hrv value is
cur_hrv_t = None #timestamp with the current hrv

sample_count = 0 #keep track of numbers of samples we've processed
leadoff_count = 0 #counter for length of time been leadoff
while True:
	if not nskECG.isBufferEmpty():
		sample_count+=1
		D = nskECG.popBuffer() #get the oldest dict

		# if we are more than 2 seconds in and leadoff is still zero
		if D['leadoff']==0:
			leadoff_count+=1
			if leadoff_count> nskECG.Fs*2:
				if nskECG.getTotalNumRRI()!=0:
					#reset the library
					nskECG.ecgalgResetLib()
				nskECG.ecg_buffer.task_done() #let queue know that we're done
				continue
		else: # leadoff==200, or lead is on
			leadoff_count=0

		D = nskECG.ecgalgAnalyzeRaw(D)

		if 'hrv' in D:
			cur_hrv = D['hrv']
			cur_hrv_t = D['timestamp']

	# we keep looping until something tells us to stop
pass #