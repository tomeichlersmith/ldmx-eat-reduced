# Reduced LDMX EaT Analysis

Looking at 8GeV
- minimum size of Hcal
- removal of every-other layer of Ecal
- just use CERN 2022 Hcal prototype as Back Hcal, no Side Hcal

---

### Scaling
Single core, spa-cms016, "hot" disk since I was reading the initial file and did not clear the cache.

#### Enriched Nuclear 0
Looking at `enriched-nuclear-0` which did not do the trigger skimming pass so it is more pessimistic
of an estimate.

5000 files in this batch.

I believe the 10k -> 100k step is when I went from one file to two files, so I'm going to switch
to testing by the file.

N-Events | Real Time
---------|-----------
1        | 2.216s
10       | 2.199s
100      | 2.254s
1000     | 2.875s
10k      | 9.185s
100k     | 72.135s
1M       | 24m 21.645s

N Files | Real Time
--------|-----------
1       |    25.745s
2       |    36.741s
4       | 1m 31.784s
8       | 2m 20.695s
16      | 4m 41.803s
32      | 9m 24.830s

#### Enriched Nuclear 1
This is more representative of the other 9/10 batches of enriched nuclear events.

100 files per batch.

N Files | Real Time
--------|-----------
1       | 1m 58.635s
2       | 3m  1.355s
4       | 5m 52.699s
8       |
16      | 
32      | 

Ran `fire-parallel` over all 100 files on Enriched Nuclear 1 on my UMN workstation
with 8 cores and in groups of 4 files per job. Taking about 25min per job ended up
taking just under 90min in total (single-threaded would be ~150min).
On all 100 files of Enriched Nuclear 2 with 8 cores and not in groups, also took about 90min.

