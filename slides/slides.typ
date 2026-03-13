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
- *Thin Module* -- 4 quad bars (36 strips) instead of 5 quad bars (40 strips) per layer

= Reducing Hcal

== Final Ecal Energy Distribution
#slide(composer: (auto, 1fr))[
  #image("../out/enriched-nuclear/final-ecal-rec-energy.svg")
][
  - entire back too expensive, prototype not enough
  - looks like need 2 modules
]

== Maximum Signal Yield Allowed
#slide(composer: (auto, 1fr))[
  #image("../out/enriched-nuclear/max-signal-allowed-all.pdf")
][
  - exponential fits to cumulative background
    - probably not the best shape
    - see appendix slides
  - use fit to predict background with uncertainy in three analysis bins
  - `combine` to set maximum signal yield
    - using signal efficiency from paper as conservative estimate
]

== Reach Estimate
#slide(composer: (auto, 1fr))[
  #image("../out/enriched-nuclear/8gev-reach-all.pdf")
][
  - using signal rates from paper
]

= Center Tower Trigger

== True Inclusive Sample
#slide[
  #image("../out/true-inclusive/trig-energy-comp.svg")
][
  - no filtering at sim or reco level
  - only $10^7$ events
  - $cal(O)(0.5 X_0)$ material upstream of ECal
  - number in parentheses in legend is event count below 3~GeV
  - $571/74 = #calc.round(571/74, digits: 2)$ ($785/268 = #calc.round(785/268, digits: 2)$) rate increase
    when only using center module for all (first 10) layers
  - $571/268 = #calc.round(571/268, digits: 2)$ rate increase using only the center module of all layers
    compared to all modules of the first 10 layers
]

== Unbiased Sample
#align(center)[
  histograms filling... ~1B events but includes simulation filter requiring electron to arrive at the ECal with $>7.5" GeV"$ energy
]

#show: appendix
= Questions

== Cumulative Background Comparison
#slide[
  #image("../out/enriched-nuclear/8gev-cumulative-bkgd-comp.pdf")
][
  #image("../out/enriched-nuclear/8gev-integrated-bkgd-fit-comp.pdf")
]

== Background Fits
#for key in ("prototype", "funnel1", "funnel2", "funnel3", "funnel4", "funnel5", "funnel6", "entireback") {
  slide[
    #image("../out/enriched-nuclear/8gev-"+key+"-cumulative-bkgd-fit.pdf")
  ][
    #image("../out/enriched-nuclear/8gev-"+key+"-integrated-bkgd-fit.pdf")
  ]
}

== Ecal RMS Distributions
#slide[
  #image("../out/enriched-nuclear/ecal-rms.svg")
][
  *Reminder*: using _entire_, full width Back Hcal
]

== Ecal Rec Energy
#slide[
  #image("../out/enriched-nuclear/ecal-rec-energy.svg")
][
  *Reminder*: using _entire_, full width Back Hcal
]

