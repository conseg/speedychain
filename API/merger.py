import glob
import math
import pandas as pd
global received
i=0
list_gw =["allgwinallcontexts","halfgwineachcontext", "halfgwineachcontext_sendall"]
# list_gw = ["halfgwineachcontext_sendall"]
list_scenarios =["10gw_100dev_10s_pbft_poolsize1","10gw_100dev_10s_pbft_poolsize10","10gw_100dev_10s_pbft_poolsize100","10gw_100dev_10s_pbft_poolsize1000","10gw_100dev_10s_pbft_poolsize10000"]
# list_scenarios =["10gw_100dev_10s_pbft_poolsize1"]
metric="T22"
# metric="T20"
for gw in list_gw:
    for scenario in list_scenarios:
        merged = open(metric+"tput"+gw+scenario+'merged.csv', 'w')
        files = sorted(glob.glob("/home/roben/IEEEBLOCKCHAIN2020/"+gw+"/"+scenario+"/*"+metric+".csv"))
        merged.write("Round"+";"+"Mean"+";"+"Std Deviation"+";"+"ConfInt95+"+";"+"ConfInt95-"+  '\n')
        for f in files:
            received = pd.read_csv(f, header=None, sep=";", usecols=[9])
            mean= received.mean()
            std=received.std()
            count=received.count()
            ci95h=mean+ 1.96*std/math.sqrt(count)
            ci95l = mean - 1.96 * std / math.sqrt(count)
            print(str(f)+";"+str(mean)+";"+str(std)+";"+str(ci95h)+";"+str(ci95l))
            # list.append(str(f)+";"+str(a)+";"+str(b))
            merged.write(str(f)+";"+str(mean)+";"+str(std)+";"+str(ci95h)+";"+str(ci95l)+  '\n')