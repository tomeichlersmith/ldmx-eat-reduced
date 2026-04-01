#include "Framework/EventProcessor.h"

#include "Ecal/Event/EcalHit.h"
#include "Recon/Event/TriggerResult.h"
#include "DetDescr/EcalID.h"

#include <cmath>

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
  histograms_.create("front_energy", "Energy in first 20 Layers [MeV]", 800,0,8000);
  histograms_.create("center_tower_front_energy", "Center Tower Energy in first 20 Layers [MeV]", 800,0,8000);
}

void CenterTowerTrigger::analyze(const framework::Event& event) {
  histograms_.setWeight(event.getEventWeight());

  const auto& all_ecal_hits{event.getCollection<ldmx::EcalHit>("EcalRecHits", "")};
  float total_energy{0},
        center_tower_energy{0},
        front_energy{0},
        center_tower_front_energy{0};
  for (const auto& hit: all_ecal_hits) {
    ldmx::EcalID id{static_cast<unsigned int>(hit.getID())};
    total_energy += hit.getEnergy();
    if (id.module() == 0) {
      center_tower_energy += hit.getEnergy();
    }
    if (id.layer() < 20) {
      front_energy += hit.getEnergy();
      if (id.module() == 0) {
        center_tower_front_energy += hit.getEnergy();
      }
    }
  }

  histograms_.fill("total_energy", total_energy);
  histograms_.fill("center_tower_energy", center_tower_energy);
  histograms_.fill("front_energy", front_energy);
  histograms_.fill("center_tower_front_energy", center_tower_front_energy);
}

DECLARE_ANALYZER(CenterTowerTrigger);
