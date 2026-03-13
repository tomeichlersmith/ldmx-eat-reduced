#include "Framework/EventProcessor.h"

#include "Ecal/Event/EcalHit.h"
#include "Recon/Event/TriggerResult.h"
#include "DetDescr/EcalID.h"

#include <cmath>

/// updated layer weights for v14 that adds the pre-ceeding
/// odd-layer weight to the even layer weight
static const std::vector<float> even_only_layer_weights = {
  2.329,
  -1, 4.339+6.495,
  -1, 7.490+8.595,
  -1, 10.253+10.915,
  -1, 10.915+10.915,
  -1, 10.915+10.915,
  -1, 10.915+10.915,
  -1, 10.915+10.915,
  -1, 10.915+10.915,
  -1, 10.915+10.915,
  -1, 10.915+10.915,
  -1, 10.915+10.915,
  -1, 14.783+18.539,
  -1, 18.539+18.539, 
  -1, 18.539+18.539,
  -1, 18.539+18.539,
  -1, 18.539+18.539,
  -1
};
/// for re-reconstructing energy of an ecal hit
static const float mip_si_energy = 0.130; // MeV

/// function to check if a ecal hit should be included
/// only even layers from the first 32 layers
bool include_ecal_hit(const ldmx::EcalHit& hit) {
  ldmx::EcalID id(static_cast<unsigned int>(hit.getID()));
  if (id.layer() >= 32) return false;
  return (id.layer() % 2 == 0);
}

class CenterTowerTrigger : public framework::Analyzer {
 public:
  CenterTowerTrigger(const std::string& name, framework::Process& p)
    : framework::Analyzer(name, p) {}
  ~CenterTowerTrigger() override = default;
  void onProcessStart() override;
  void analyze(const framework::Event& event) override;
};

void CenterTowerTrigger::onProcessStart() {
  getHistoDirectory();
  histograms_.create("total_energy", "Ecal Reco Energy [MeV]", 800,0,8000);
  histograms_.create("center_tower_energy", "Center Tower Energy [MeV]", 800,0,8000);
  histograms_.create("front_energy", "Energy in first 10 Layers [MeV]", 800,0,8000);
  histograms_.create("center_tower_front_energy", "Center Tower Energy in first 10 Layers [MeV]", 800,0,8000);
}

void CenterTowerTrigger::analyze(const framework::Event& event) {
  histograms_.setWeight(event.getEventWeight());

  const auto& all_ecal_hits{event.getCollection<ldmx::EcalHit>("EcalRecHits", "")};
  std::vector<const ldmx::EcalHit*> ecal_hits;
  for (const auto& ecal_hit: all_ecal_hits) {
    if (include_ecal_hit(ecal_hit)) {
      ecal_hits.push_back(&ecal_hit);
    }
  }
  float total_energy{0},
        center_tower_energy{0},
        front_energy{0},
        center_tower_front_energy{0};
  for (const auto* ecal_hit: ecal_hits) {
    ldmx::EcalID id{static_cast<unsigned int>(ecal_hit->getID())};
    float hit_energy = (1 + even_only_layer_weights.at(id.layer())/mip_si_energy)*ecal_hit->getAmplitude();
    total_energy += hit_energy;
    if (id.module() == 0) {
      center_tower_energy += hit_energy;
    }
    if (id.layer() < 20) {
      front_energy += hit_energy;
      if (id.module() == 0) {
        center_tower_front_energy += hit_energy;
      }
    }
  }

  histograms_.fill("total_energy", total_energy);
  histograms_.fill("center_tower_energy", center_tower_energy);
  histograms_.fill("front_energy", front_energy);
  histograms_.fill("center_tower_front_energy", center_tower_front_energy);
}

DECLARE_ANALYZER(CenterTowerTrigger);
