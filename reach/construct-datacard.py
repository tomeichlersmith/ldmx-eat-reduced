from harvester.datacard import DataCard
import json
import os
    

with open('bkgd-prediction.json','r') as f:
    bkgd_yield = json.load(f)

with open('sig-eff.json','r') as f:
    sig_eff = json.load(f)


with open('jm-requests/jobs.list','w') as jobs:
    for beam in [4, 8]:
        by = bkgd_yield[beam]
        for proc, se in seg_eff[beam].items():
            datacard_path = str(output / f'{proc}.txt')
            (
                DataCard(3)
                .sig(*se.value)
                .bkg(*by.value)
                .bkg_stat(*((by.up - by.lo)/2/by.value))
                .bkg_syst(0.05)
                .bkg_syst(0.0, 0.6, 0.7)
                .write(datacard_path)
            )
            for q in [0.025, 0.16, 0.5, 0.84, 0.975]:
                jobs.write(' '.join([
                    datacard_path,
                    f'--keyword-value option={name}',
                    f'--mass {proc[2:]}',
                    f'--expectedFromGrid={q}'
                ])