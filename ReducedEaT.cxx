#include "Framework/EventProcessor.h"

#include "Hcal/Event/HcalHit.h"
#include "Ecal/Event/EcalHit.h"

#include <cmath>

int hcal_hit_cost(const ldmx::HcalHit& h) {
  return h.getLayer()*std::max(4, 2*static_cast<int>(std::floor(std::abs(h.getStrip() - 30.5))));
}

class ReducedEaT : public framework::Analyzer {
  int max_pe_threshold = 10;
  float rms_event_size_threshold = 20; // mm
  float reco_ecal_energy = 2760; // MeV
  float trig_ecal_energy = 3160; // MeV
 public:
  ReducedEaT(const std::string& name, framework::Process& p)
    : framework::Analyzer(name, p) {}
  ~ReducedEaT() override = default;
  void onProcessStart() override;
  void analyze(const framework::Event& event) override;
};

void ReducedEaT::onProcessStart() {
  getHistoDirectory();
  histograms_.create(
      "n_hcal_veto_hits",
      "N Hits above "+std::to_string(max_pe_threshold)+"PE",
      100,0,100
  );
}

void ReducedEaT::analyze(const framework::Event& event) {
  histograms_.setWeight(event.getEventWeight());

  const auto& hcal_hits{event.getCollection<ldmx::HcalHit>("HcalRecHits", "")};
  int n_hcal_veto_hits{0};
  for (const auto& hcal_hit: hcal_hits) {
    if (hcal_hit.getPE() < max_pe_threshold) {
      // this hit would not veto the event, skip it
      continue;
    }
    n_hcal_veto_hits++;
  }

  histograms_.fill("n_hcal_veto_hits", n_hcal_veto_hits);
}

DECLARE_ANALYZER(ReducedEaT);
