#!/bin/bash
cp $HOME/.local/share/ntracking_working_folder/local_machine/machine_resources.log $HOME/.local/share/ntracking_working_folder/Machine_S00.log
rsync -avz --update safe-s01:"/home/ubuntu/machine_resources.log" "/home/ubuntu/ntracking/Machine_S01.log"
rsync -avz --update safe-s02:"/home/ubuntu/machine_resources.log" "/home/ubuntu/ntracking/Machine_S02.log"
rsync -avz --update safe-s03:"/home/ubuntu/machine_resources.log" "/home/ubuntu/ntracking/Machine_S03.log"
rsync -avz --update safe-s04:"/home/ubuntu/machine_resources.log" "/home/ubuntu/ntracking/Machine_S04.log"
rsync -avz --update safe-s05:"/home/ubuntu/machine_resources.log" "/home/ubuntu/ntracking/Machine_S05.log"
rsync -avz --update safe-s06:"/home/ubuntu/machine_resources.log" "/home/ubuntu/ntracking/Machine_S06.log"
rsync -avz --update safe-s07:"/home/ubuntu/machine_resources.log" "/home/ubuntu/ntracking/Machine_S07.log"
rsync -avz --update safe-s08:"/home/ubuntu/machine_resources.log" "/home/ubuntu/ntracking/Machine_S08.log"
rsync -avz --update safe-s09:"/home/ubuntu/machine_resources.log" "/home/ubuntu/ntracking/Machine_S09.log"
rsync -avz --update safe-s10:"/home/ubuntu/machine_resources.log" "/home/ubuntu/ntracking/Machine_S10.log"
rsync -avz --update safe-s11:"/home/ubuntu/machine_resources.log" "/home/ubuntu/ntracking/Machine_S11.log"
rsync -avz --update safe-s12:"/home/ubuntu/machine_resources.log" "/home/ubuntu/ntracking/Machine_S12.log"
rsync -avz --update safe-s13:"/home/ubuntu/machine_resources.log" "/home/ubuntu/ntracking/Machine_S13.log"
rsync -avz --update safe-s14:"/home/ubuntu/machine_resources.log" "/home/ubuntu/ntracking/Machine_S14.log"
rsync -avz --update safe-s15:"/home/ubuntu/machine_resources.log" "/home/ubuntu/ntracking/Machine_S15.log"
rsync -avz --update safe-s16:"/home/ubuntu/machine_resources.log" "/home/ubuntu/ntracking/Machine_S16.log"
rsync -avz --update safe-s17:"/home/ubuntu/machine_resources.log" "/home/ubuntu/ntracking/Machine_S17.log"
rsync -avz --update safe-s18:"/home/ubuntu/machine_resources.log" "/home/ubuntu/ntracking/Machine_S18.log"
rsync -avz --update safe-s19:"/home/ubuntu/machine_resources.log" "/home/ubuntu/ntracking/Machine_S19.log"
rsync -avz --update safe-s20:"/home/ubuntu/machine_resources.log" "/home/ubuntu/ntracking/Machine_S20.log"
rsync -avz --update hamilton:"/home/ubuntu/machine_resources.log" "/home/ubuntu/ntracking/Machine_S21.log"
rsync -avz --update byres:"/home/ubuntu/machine_resources.log" "/home/ubuntu/ntracking/Machine_S22.log"
