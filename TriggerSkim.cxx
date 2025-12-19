#include "Framework/EventProcessor.h"

#include "Recon/Event/TriggerResult.h"

class TriggerSkim : public framework::Analyzer {
 public:
  TriggerSkim(const std::string& name, framework::Process& p)
    : framework::Analyzer(name, p) {}
  ~TriggerSkim() override = default;
  void analyze(const framework::Event& event) override;
};

void TriggerSkim::analyze(const framework::Event& event) {
  const auto& trig_desc{event.getObject<ldmx::TriggerResult>("Trigger", "")};
  if (trig_desc.passed()) {
    setStorageHint(framework::StorageControl::Hint::ShouldKeep);
  }
}

DECLARE_ANALYZER(TriggerSkim);
