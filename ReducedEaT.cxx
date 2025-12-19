#include "Framework/EventProcessor.h"

#include "Hcal/Event/HcalHit.h"
#include "Ecal/Event/EcalHit.h"
#include "Recon/Event/TriggerResult.h"
#include "DetDescr/EcalID.h"

#include <cmath>

int hcal_hit_cost(const ldmx::HcalHit& h) {
  return h.getLayer()*std::max(4, 2*static_cast<int>(std::floor(std::abs(h.getStrip() - 19.5))));
}

class ReducedEaT : public framework::Analyzer {
  int max_pe_threshold = 10;
  float rms_event_size_threshold = 20; // mm
  float reco_ecal_energy = 2760; // MeV
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
  histograms_.create(
      "trigger_total_ecal_rec_energy",
      "Ecal Reco Energy [MeV]",
      400,0,4000);
  histograms_.create(
      "hcalmaxpe_total_ecal_rec_energy",
      "Ecal Reco Energy [MeV]",
      400,0,4000);
  histograms_.create(
      "ecalrms_total_ecal_rec_energy",
      "Ecal Reco Energy [MeV]",
      400,0,4000);
}

static const std::vector<float> even_only_layer_weights = {
  2.329,
  4.339, 4.339+6.495,
  7.490, 7.490+8.595,
  10.253, 10.253+10.915,
  10.915, 10.915+10.915,
  10.915, 10.915+10.915,
  10.915, 10.915+10.915,
  10.915, 10.915+10.915,
  10.915, 10.915+10.915,
  10.915, 10.915+10.915,
  10.915, 10.915+10.915,
  10.915, 10.915+10.915,
  14.783, 14.783+18.539,
  18.539, 18.539+18.539, 
  18.539, 18.539+18.539,
  18.539, 18.539+18.539,
  18.539, 18.539+18.539,
  9.938
};
static const float mip_si_energy = 0.130; // MeV

bool include_ecal_hit(const ldmx::EcalHit& hit) {
  ldmx::EcalID id(static_cast<unsigned int>(hit.getID()));
  if (id.layer() >= 32) return false;
  return (id.layer() % 2 == 0);
}

bool include_hcal_hit(const ldmx::HcalHit& hit) {
  return (hit.getSection() == 0);
}

void ReducedEaT::analyze(const framework::Event& event) {
  histograms_.setWeight(event.getEventWeight());

  const auto& trig_desc{event.getObject<ldmx::TriggerResult>("Trigger", "")};
  if (not trig_desc.passed()) {
    return;
  }

  const auto& all_ecal_hits{event.getCollection<ldmx::EcalHit>("EcalRecHits", "")};
  std::vector<const ldmx::EcalHit*> ecal_hits;
  for (const auto& ecal_hit: all_ecal_hits) {
    if (include_ecal_hit(ecal_hit)) {
      ecal_hits.push_back(&ecal_hit);
    }
  }

  const auto& all_hcal_hits{event.getCollection<ldmx::HcalHit>("HcalRecHits", "")};
  std::vector<const ldmx::HcalHit*> hcal_hits;
  for (const auto& hcal_hit: all_hcal_hits) {
    if (include_hcal_hit(hcal_hit)) {
      hcal_hits.push_back(&hcal_hit);
    }
  }

  float total_energy{0},
        center_x{0},
        center_y{0},
        shower_rms{0};
  for (const auto* ecal_hit: ecal_hits) {
    ldmx::EcalID id{static_cast<unsigned int>(ecal_hit->getID())};
    float hit_energy = (1 + even_only_layer_weights.at(id.layer())/mip_si_energy)*ecal_hit->getAmplitude();
    total_energy += hit_energy;
    center_x += hit_energy*ecal_hit->getXPos();
    center_y += hit_energy*ecal_hit->getYPos();
  }
  if (total_energy > 0) {
    center_x /= total_energy;
    center_y /= total_energy;
    for (const auto* ecal_hit: ecal_hits) {
      ldmx::EcalID id{static_cast<unsigned int>(ecal_hit->getID())};
      float hit_energy = (1 + even_only_layer_weights.at(id.layer())/mip_si_energy)*ecal_hit->getAmplitude();
      shower_rms += hit_energy*std::sqrt(
          (ecal_hit->getXPos() - center_x)*(ecal_hit->getXPos() - center_x)
          + (ecal_hit->getYPos() - center_y)*(ecal_hit->getYPos() - center_y)
          );
    }
    shower_rms /= total_energy;
  }

  int n_hcal_veto_hits{0};
  float hcal_max_pe{0};
  for (const auto* hcal_hit: hcal_hits) {
    if (hcal_hit->getPE() > hcal_max_pe) {
      hcal_max_pe = hcal_hit->getPE();
    }
    if (hcal_hit->getPE() < max_pe_threshold) {
      // this hit would not veto the event, skip it
      continue;
    }
    n_hcal_veto_hits++;
  }

  histograms_.fill("n_hcal_veto_hits", n_hcal_veto_hits);
  histograms_.fill("trigger_total_ecal_rec_energy", total_energy);
  if (hcal_max_pe < max_pe_threshold) {
    histograms_.fill("hcalmaxpe_total_ecal_rec_energy", total_energy);
    if (shower_rms < rms_event_size_threshold) {
      histograms_.fill("ecalrms_total_ecal_rec_energy", total_energy);
    }
  }
}

DECLARE_ANALYZER(ReducedEaT);
