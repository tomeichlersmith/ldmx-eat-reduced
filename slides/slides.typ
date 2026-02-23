#import "@local/umn-theme:0.0.0": *

#show: checklist

#show: umn-theme.with(
  config-info(
    title: [EaT for Reduced LDMX],
    subtitle: [Requirements for an "Early-Phase" Missing Energy Analysis],
    author: [Tom Eichlersmith],
    date: datetime.today(),
    institution: [he/him/his \ University of Minnesota],
  )
)

#title-slide()

= Background

== Background (aka Caveats)
=== Same background samples from EaT Paper
- 8GeV electron beam, $10^(13)$ EoT equivalent, v14 geometry
- 7GeV electron entering Ecal
- *Dimuon*: muon-conversion biased and filtered for
- *Enriched Nuclear*: eletron-nuclear and photon-nuclear biased and filtered for
- Ecal Missing Energy Trigger applied ($E_"L<20" < 3.16" GeV"$)
  - Uses both even and odd layers!

=== Attempt to Reduce
- Ignore hits in Side Hcal
  - _Material is still there_
- Ignore Odd-Layers of Ecal
  - _Material is still there_
  - Re-scale layer weights so energy estimate is still appropriate

== Vocabulary
- *Ecal Reco Energy* -- total energy in Ecal (calculated only with even layers)
- *Ecal RMS* -- transverse RMS of Ecal shower (calculated only with even layers)
- *Bar* -- single element of Hcal detector, used interchangeably with "strip"
- *Back Hcal Max PE* -- maximum PE deposited in a single bar in _entire_ Back Hcal
- *Quads* -- number of quads within a layer to get to strip $s$ symmetrically
$
  Q(s) = floor((|s - 19.5|)/2) + 1 
$
- *Layer #sym.star Quads* -- hit that minimizes "area" cost function $C(l="layer",s) = l times Q(s)$
- *Quads then Layer* -- hit that minimizes $Q(s)$ and then minimizes layer if more than one hit in that "most central" quad

= Plots

== Dimuon
#slide(composer: (auto, 1fr))[
  #image("../out/dimuon/trigger-hcal-area-strip-layer.svg")
][
  === Good News
  - The bars designed as the muon veto for mu2e still easily veto muons!
  - Only need one layer (12 bars) in the Back Hcal to veto all but 2 events from the dimuon sample

  #align(bottom)[
    Will need a larger Back Hcal for Enriched Nuclear...
  ]
]

== Enriched Nuclear: Area Cost
#slide(composer: (auto, 1fr))[
  #image("../out/enriched-nuclear/trigger-hcal-area-strip-layer.svg")
][
  - need to use Ecal to know how large the Back Hcal "needs" to be
]

#slide(composer: (auto, 1fr))[
  #image("../out/enriched-nuclear/ecalrms-hcal-area-strip-layer.svg")
][
  - require shower in Ecal to be "thin"
]

#slide(composer: (auto, 1fr))[
  #image("../out/enriched-nuclear/lowenergy-hcal-area-strip-layer.svg")
][
  - require shower in Ecal to be lower energy (below trigger threshold)
  
  #tblock(title: [Rough "Requirements"])[
    - 40 bars
    - \~70 layers
  ]
  (not really requirements, could reduce Back Hcal further and just allow more background into multi-bin analysis)
]

== Enriched Nuclear: Most Central
#slide(composer: (auto, 1fr))[
  #image("../out/enriched-nuclear/trigger-hcal-central-strip-layer.svg")
][
  - need to use Ecal to know how large the Back Hcal "needs" to be
]

#slide(composer: (auto, 1fr))[
  #image("../out/enriched-nuclear/ecalrms-hcal-central-strip-layer.svg")
][
  - require shower in Ecal to be "thin"
]

#slide(composer: (auto, 1fr))[
  #image("../out/enriched-nuclear/lowenergy-hcal-central-strip-layer.svg")
][
  - require shower in Ecal to be lower energy (below trigger threshold)
  
  #tblock(title: [Rough "Requirements"])[
    - 40 bars
    - \~70 layers
  ]
  (not really requirements, could reduce Back Hcal further and just allow more background into multi-bin analysis)
]

== Reduced Hcal Options
#slide(composer: (auto, 1fr))[
  #image("../out/enriched-nuclear/final-ecal-rec-energy.svg")
][
  #tblock(title: [Seems Feasible])[
    - same order-of-magnitude as 4~GeV distribution in paper
    - could do fit and multi-bin analysis
    - lowest-energy bin is still *empty* if broad modules are included
  ]

  - Module: 8 40-strip layers
  - Prototype: as configured at CERN
    - 9 8-strip layers then 10 12-strip layers

  === Further Questions

  - Trigger doing too much work?
    - requires new simulation
]

#show: appendix
= Questions
== Ecal RMS Distributions
#slide[
  #image("../out/enriched-nuclear/ecal-rms.svg")
][
  *Reminder*: using _entire_ Back Hcal
]

== Ecal Rec Energy
#slide[
  #image("../out/enriched-nuclear/ecal-rec-energy.svg")
][
  *Reminder*: using _entire_ Back Hcal
]

