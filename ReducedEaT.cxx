#include "Framework/EventProcessor.h"

#include "Hcal/Event/HcalHit.h"
#include "Ecal/Event/EcalHit.h"
#include "Recon/Event/TriggerResult.h"
#include "DetDescr/EcalID.h"

#include <cmath>

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

bool is_in_narrow_back(const ldmx::HcalHit& hit) {
  if (not is_in_back_hcal(hit)) return false;
  return hcal_hit_n_required_quads(hit.getStrip()) < 9;
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
bool is_in_N_narrow_modules_then_reverse_prototype(const ldmx::HcalHit& hit) {
  if (not is_in_back_hcal(hit)) return false;
  if (hit.getLayer() < N*8+1) {
    // first 6 modules (8 layers each) have 8 quads
    return hcal_hit_n_required_quads(hit.getStrip()) < 9;
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

template<int N>
bool is_in_N_modules_then_reverse_prototype(const ldmx::HcalHit& hit) {
  if (not is_in_back_hcal(hit)) return false;
  if (hit.getLayer() < N*8+1) {
    // first N modules (8 layers each) have all 10 quads
    return true;
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

template<int N>
bool is_in_N_modules_then_reverse_prototype_or_6_side(const ldmx::HcalHit& hit) {
  if (not is_in_back_hcal(hit)) {
    // check if hit is in first 6 layers of side hcal
    return hit.getLayer() < 6+1;
  }
  return is_in_N_modules_then_reverse_prototype<N>(hit);
}

template<int N>
bool is_in_N_narrow_modules_then_reverse_prototype_or_6_side(const ldmx::HcalHit& hit) {
  if (not is_in_back_hcal(hit)) {
    // check if hit is in first 6 layers of side hcal
    return hit.getLayer() < 6+1;
  }
  return is_in_N_narrow_modules_then_reverse_prototype<N>(hit);
}

static const std::map<std::string, HcalHitFilter> REDUCED_HCAL_OPTIONS = {
  {"entireback", is_in_back_hcal},
  {"narrowback", is_in_narrow_back},
  {"sixonly", is_in_first_six_modules},
  {"funnel6", is_in_N_modules_then_reverse_prototype<6>},
  {"funnel5", is_in_N_modules_then_reverse_prototype<5>},
  {"funnel4", is_in_N_modules_then_reverse_prototype<4>},
  {"funnel3", is_in_N_modules_then_reverse_prototype<3>},
  {"funnel2", is_in_N_modules_then_reverse_prototype<2>},
  {"funnel1", is_in_N_modules_then_reverse_prototype<1>},
  {"funnel6_withside6", is_in_N_modules_then_reverse_prototype_or_6_side<6>},
  {"funnel5_withside6", is_in_N_modules_then_reverse_prototype_or_6_side<5>},
  {"funnel4_withside6", is_in_N_modules_then_reverse_prototype_or_6_side<4>},
  {"funnel3_withside6", is_in_N_modules_then_reverse_prototype_or_6_side<3>},
  {"funnel2_withside6", is_in_N_modules_then_reverse_prototype_or_6_side<2>},
  {"funnel1_withside6", is_in_N_modules_then_reverse_prototype_or_6_side<1>},
  {"narrowfunnel6", is_in_N_narrow_modules_then_reverse_prototype<6>},
  {"narrowfunnel5", is_in_N_narrow_modules_then_reverse_prototype<5>},
  {"narrowfunnel4", is_in_N_narrow_modules_then_reverse_prototype<4>},
  {"narrowfunnel3", is_in_N_narrow_modules_then_reverse_prototype<3>},
  {"narrowfunnel2", is_in_N_narrow_modules_then_reverse_prototype<2>},
  {"narrowfunnel1", is_in_N_narrow_modules_then_reverse_prototype<1>},
  {"narrowfunnel6_withside6", is_in_N_narrow_modules_then_reverse_prototype_or_6_side<6>},
  {"narrowfunnel5_withside6", is_in_N_narrow_modules_then_reverse_prototype_or_6_side<5>},
  {"narrowfunnel4_withside6", is_in_N_narrow_modules_then_reverse_prototype_or_6_side<4>},
  {"narrowfunnel3_withside6", is_in_N_narrow_modules_then_reverse_prototype_or_6_side<3>},
  {"narrowfunnel2_withside6", is_in_N_narrow_modules_then_reverse_prototype_or_6_side<2>},
  {"narrowfunnel1_withside6", is_in_N_narrow_modules_then_reverse_prototype_or_6_side<1>},
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
  float total_energy{0},
        center_x{0},
        center_y{0},
        shower_rms{0};
  for (const auto& hit: all_ecal_hits) {
    total_energy += hit.getEnergy();
    center_x += hit.getEnergy()*hit.getXPos();
    center_y += hit.getEnergy()*hit.getYPos();
  }
  if (total_energy > 0) {
    center_x /= total_energy;
    center_y /= total_energy;
    for (const auto& hit: all_ecal_hits) {
      shower_rms += hit.getEnergy()*std::sqrt(
          (hit.getXPos() - center_x)*(hit.getXPos() - center_x)
          + (hit.getYPos() - center_y)*(hit.getYPos() - center_y)
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
