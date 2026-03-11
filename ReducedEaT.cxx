#include "Framework/EventProcessor.h"

#include "Hcal/Event/HcalHit.h"
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

/// count number of quad-bars are needed to reach out to the input
/// strip assuming we start filling from the center (strip 20)
int hcal_hit_n_required_quads(int strip) {
  return std::floor(std::abs(strip - 19.5)/2)+1;
}

int hcal_hit_cost(const ldmx::HcalHit& h) {
  return h.getLayer()*hcal_hit_n_required_quads(h.getStrip());
}

using HcalHitFilter = bool (*)(const ldmx::HcalHit& hit);

/**
 * Hcal "prototype" from CERN 2022 testbeam is
 * - 9 layers each with 2 quads and 10 layers each with 3 quad bars
 *
 * One Hcal "module" is 8 layers with 5 quad bars (40 strips)
 */
bool is_in_back_hcal(const ldmx::HcalHit& hit) {
  return (hit.getSection() == 0);
}

bool is_in_thin_back(const ldmx::HcalHit& hit) {
  if (not is_in_back_hcal(hit)) return false;
  return hcal_hit_n_required_quads(hit.getStrip()) < 5;
}

bool is_in_first_six_modules(const ldmx::HcalHit& hit) {
  if (not is_in_back_hcal(hit)) return false;
  return (hit.getLayer() < 6*8 + 1);
}

bool is_in_prototype(const ldmx::HcalHit& hit) {
  if (not is_in_back_hcal(hit)) return false;
  if (hit.getLayer() < 9 + 1) {
    // first 9 layers have 2 quads
    return hcal_hit_n_required_quads(hit.getStrip()) < 3;
  } else if (hit.getLayer() < 19 + 1) {
    // 10-19 have 3 quads
    return hcal_hit_n_required_quads(hit.getStrip()) < 4;
  }
  return false;
}

bool is_in_prototype_then_six_modules(const ldmx::HcalHit& hit) {
  if (not is_in_back_hcal(hit)) return false;
  if (hit.getLayer() < 9 + 1) {
    // first 9 layers have 2 quads
    return hcal_hit_n_required_quads(hit.getStrip()) < 3;
  } else if (hit.getLayer() < 19 + 1) {
    // 10-19 have 3 quads
    return hcal_hit_n_required_quads(hit.getStrip()) < 4;
  } else {
    // next 6 modules (8 layers each) have all 5 quads
    return hit.getLayer() < (19 + 6*8 + 1);
  }
}

template<int N>
bool is_in_N_modules_then_reverse_prototype(const ldmx::HcalHit& hit) {
  if (not is_in_back_hcal(hit)) return false;
  if (hit.getLayer() < N*8+1) {
    // first 6 modules (8 layers each) have all 4 quads
    return hcal_hit_n_required_quads(hit.getStrip()) < 5;
  } else if (hit.getLayer() < (N*8 + 10 + 1)) {
    // next 10 layers have 3 quads
    return hcal_hit_n_required_quads(hit.getStrip()) < 4;
  } else if (hit.getLayer() < (N*8 + 10 + 9 + 1)) {
    // next 9 layers have 2 quads
    return hcal_hit_n_required_quads(hit.getStrip()) < 3;
  } else {
    return false;
  }
}

static const std::map<std::string, HcalHitFilter> REDUCED_HCAL_OPTIONS = {
  {"entireback", is_in_back_hcal},
  {"thinback", is_in_thin_back},
  {"sixonly", is_in_first_six_modules},
  {"funnel6", is_in_N_modules_then_reverse_prototype<6>},
  {"funnel5", is_in_N_modules_then_reverse_prototype<5>},
  {"funnel4", is_in_N_modules_then_reverse_prototype<4>},
  {"funnel3", is_in_N_modules_then_reverse_prototype<3>},
  {"funnel2", is_in_N_modules_then_reverse_prototype<2>},
  {"funnel1", is_in_N_modules_then_reverse_prototype<1>},
  {"megaphone", is_in_prototype_then_six_modules},
  {"prototype", is_in_prototype}
};

class ReducedEaT : public framework::Analyzer {
  int max_pe_threshold = 10;
  float rms_event_size_threshold = 20; // mm
  float low_energy_threshold = 3160; // MeV
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
  for (const std::string& selection : {"trigger", "ecalrms", "lowenergy"}) {
    histograms_.create(
        selection+"_hcal_min_cost_strip_layer",
        "Strip", 40, -0.5, 39.5,
        "Layer", 100, 0.5, 100.5
    );
    histograms_.create(
        selection+"_hcal_central_strip_layer",
        "Strip", 40, -0.5, 39.5,
        "Layer", 100, 0.5, 100.5
    );
  }

  for (const auto& [hcal_name, _filter]: REDUCED_HCAL_OPTIONS) {
    for (const std::string& selection : {"trigger", "ecalrms", "lowenergy"}) {
      histograms_.create(
          hcal_name+"_"+selection+"_hcalmaxpe",
          "PE", 50, 0, 50
      );
    }

    for (const std::string& selection : {"trigger", "hcalmaxpe"}) {
      histograms_.create(
          hcal_name+"_"+selection+"_ecalrms",
          "Ecal RMS [mm]", 50, 0, 50);
    }
  
    for (const std::string& selection: {"trigger", "hcalmaxpe", "ecalrms", "final"}) {
      histograms_.create(
          hcal_name+"_"+selection+"_total_ecal_rec_energy",
          "Ecal Reco Energy [MeV]",
          400,0,4000);
    }
  }
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

  const auto& all_hcal_hits{event.getCollection<ldmx::HcalHit>("HcalRecHits", "")};

  /****************************************************************************
   * Use Entire Back Hcal to find "Best" hit that vetos event
   ***************************************************************************/
  int n_hcal_veto_hits{0};
  float hcal_max_pe{0};
  int hcal_hit_veto_cost{20*200};
  std::pair<int,int> min_quad_bar{40,100};
  const ldmx::HcalHit* min_cost_veto{nullptr}, *central_veto{nullptr};
  for (const auto& hcal_hit: all_hcal_hits) {
    if (not is_in_back_hcal(hcal_hit)) {
      continue;
    }
    if (hcal_hit.getPE() > hcal_max_pe) {
      hcal_max_pe = hcal_hit.getPE();
    }
    if (hcal_hit.getPE() < max_pe_threshold) {
      // this hit would not veto the event, skip it
      continue;
    }
    n_hcal_veto_hits++;
    int cost{hcal_hit_cost(hcal_hit)};
    if (cost < hcal_hit_veto_cost) {
      hcal_hit_veto_cost = cost;
      min_cost_veto = &hcal_hit;
    }
    int n_req_quads{hcal_hit_n_required_quads(hcal_hit.getStrip())};
    if (n_req_quads < min_quad_bar.first or
        (n_req_quads == min_quad_bar.first and hcal_hit.getLayer() < min_quad_bar.second)) {
      min_quad_bar = {n_req_quads, hcal_hit.getLayer()};
      central_veto = &hcal_hit;
    }
  }

  histograms_.fill("n_hcal_veto_hits", n_hcal_veto_hits);
  histograms_.fill("trigger_hcal_min_cost_strip_layer",
      min_cost_veto ? min_cost_veto->getStrip() : -1,
      min_cost_veto ? min_cost_veto->getLayer() : -1);
  histograms_.fill("trigger_hcal_central_strip_layer",
      central_veto ? central_veto->getStrip() : -1,
      central_veto ? central_veto->getLayer() : -1);
  if (shower_rms < rms_event_size_threshold) {
    histograms_.fill("ecalrms_hcal_min_cost_strip_layer",
        min_cost_veto ? min_cost_veto->getStrip() : -1,
        min_cost_veto ? min_cost_veto->getLayer() : -1);
    histograms_.fill("ecalrms_hcal_central_strip_layer",
        central_veto ? central_veto->getStrip() : -1,
        central_veto ? central_veto->getLayer() : -1);
    if (total_energy < low_energy_threshold) {
      histograms_.fill("lowenergy_hcal_min_cost_strip_layer",
        min_cost_veto ? min_cost_veto->getStrip() : -1,
        min_cost_veto ? min_cost_veto->getLayer() : -1);
      histograms_.fill("lowenergy_hcal_central_strip_layer",
        central_veto ? central_veto->getStrip() : -1,
        central_veto ? central_veto->getLayer() : -1);
    }
  }

  /****************************************************************************
   * do event selection for a few different options of a reduced Hcal
   ***************************************************************************/
  for (const auto& [hcal_name, should_keep] : REDUCED_HCAL_OPTIONS) {
    float hcal_max_pe{0};
    for (const auto& hcal_hit : all_hcal_hits) {
      if (not should_keep(hcal_hit)) {
        continue;
      }
      if (hcal_hit.getPE() > hcal_max_pe) {
        hcal_max_pe = hcal_hit.getPE();
      }
    }

    histograms_.fill(hcal_name+"_trigger_total_ecal_rec_energy", total_energy);
    histograms_.fill(hcal_name+"_trigger_ecalrms", shower_rms);
    histograms_.fill(hcal_name+"_trigger_hcalmaxpe", hcal_max_pe);
    if (hcal_max_pe < max_pe_threshold) {
      histograms_.fill(hcal_name+"_hcalmaxpe_total_ecal_rec_energy", total_energy);
      histograms_.fill(hcal_name+"_hcalmaxpe_ecalrms", shower_rms);
      if (shower_rms < rms_event_size_threshold) {
        histograms_.fill(hcal_name+"_final_total_ecal_rec_energy", total_energy);
      }
    }
  
    if (shower_rms < rms_event_size_threshold) {
      histograms_.fill(hcal_name+"_ecalrms_total_ecal_rec_energy", total_energy);
      histograms_.fill(hcal_name+"_ecalrms_hcalmaxpe", hcal_max_pe);
      if (total_energy < low_energy_threshold) {
        histograms_.fill(hcal_name+"_lowenergy_hcalmaxpe", hcal_max_pe);
      }
    }
  }
}

DECLARE_ANALYZER(ReducedEaT);
