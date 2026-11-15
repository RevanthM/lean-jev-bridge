import Std

namespace Bridge

/- The reviewed facts and policy are application inputs, not neural outputs.
   Their semantic correctness is an explicit trust boundary. -/
structure Policy where
  id : String
  sourceId : String
  sourceLine : String
  factId : String
  reviewedFact : Bool
  validFrom : Nat
  validThrough : Nat
  day : Nat
  minChoiceBps : Nat := 9800
  minNoulBps : Nat := 9800
  maxRiskNumerator : Nat := 500
  deriving Repr, BEq

structure Packet where
  model : String
  policyId : String
  sourceId : String
  quote : String
  factId : String
  choice : String
  refundBps : Nat
  reviewBps : Nat
  noneBps : Nat
  supportNoulBps : Nat
  risk0Bps : Nat
  risk1Bps : Nat
  risk2Bps : Nat
  deriving Repr, BEq

def packetValid (x : Packet) : Prop :=
  x.model = "jev-1.14.0" ∧
  (x.choice = "refund" ∨ x.choice = "review" ∨ x.choice = "none") ∧
  x.refundBps + x.reviewBps + x.noneBps = 10000 ∧
  x.supportNoulBps ≤ 10000 ∧
  x.risk0Bps + x.risk1Bps + x.risk2Bps = 10000

instance (x : Packet) : Decidable (packetValid x) := inferInstanceAs (Decidable (_ ∧ _ ∧ _ ∧ _ ∧ _))

def certificateValid (p : Policy) (x : Packet) : Prop :=
  x.policyId = p.id ∧ x.sourceId = p.sourceId ∧
  x.quote = p.sourceLine ∧ p.sourceLine ≠ "" ∧ x.factId = p.factId

instance (p : Policy) (x : Packet) : Decidable (certificateValid p x) :=
  inferInstanceAs (Decidable (_ ∧ _ ∧ _ ∧ _ ∧ _))

def acceptable (p : Policy) (x : Packet) : Prop :=
  packetValid x ∧ certificateValid p x ∧ p.reviewedFact = true ∧
  p.validFrom ≤ p.day ∧ p.day ≤ p.validThrough ∧
  x.choice = "refund" ∧ p.minChoiceBps ≤ x.refundBps ∧
  p.minNoulBps ≤ x.supportNoulBps ∧
  x.risk1Bps + 2 * x.risk2Bps ≤ p.maxRiskNumerator

instance (p : Policy) (x : Packet) : Decidable (acceptable p x) :=
  inferInstanceAs (Decidable (_ ∧ _ ∧ _ ∧ _ ∧ _ ∧ _ ∧ _ ∧ _ ∧ _))

inductive Decision where
  | accepted
  | review
  | invalid
  deriving Repr, BEq, DecidableEq

def evaluate (p : Policy) (x : Packet) : Decision :=
  if ¬ packetValid x then .invalid
  else if acceptable p x then .accepted else .review

theorem accepted_iff (p : Policy) (x : Packet) :
    evaluate p x = .accepted ↔ acceptable p x := by
  unfold evaluate
  by_cases hv : packetValid x
  · simp [hv]
  · have hn : ¬ acceptable p x := fun h => hv h.1
    simp [hv, hn]

theorem accepted_requires_reviewed_fact (p : Policy) (x : Packet)
    (h : evaluate p x = .accepted) : p.reviewedFact = true :=
  ((accepted_iff p x).mp h).2.2.1

theorem accepted_requires_certificate (p : Policy) (x : Packet)
    (h : evaluate p x = .accepted) : certificateValid p x :=
  ((accepted_iff p x).mp h).2.1

theorem accepted_requires_pinned_model (p : Policy) (x : Packet)
    (h : evaluate p x = .accepted) : x.model = "jev-1.14.0" :=
  ((accepted_iff p x).mp h).1.1

theorem accepted_requires_current_policy (p : Policy) (x : Packet)
    (h : evaluate p x = .accepted) : p.validFrom ≤ p.day ∧ p.day ≤ p.validThrough := by
  have ha := (accepted_iff p x).mp h
  exact ⟨ha.2.2.2.1, ha.2.2.2.2.1⟩

theorem accepted_requires_choice_threshold (p : Policy) (x : Packet)
    (h : evaluate p x = .accepted) : p.minChoiceBps ≤ x.refundBps :=
  ((accepted_iff p x).mp h).2.2.2.2.2.2.1

theorem accepted_requires_noul_threshold (p : Policy) (x : Packet)
    (h : evaluate p x = .accepted) : p.minNoulBps ≤ x.supportNoulBps :=
  ((accepted_iff p x).mp h).2.2.2.2.2.2.2.1

theorem accepted_requires_risk_bound (p : Policy) (x : Packet)
    (h : evaluate p x = .accepted) :
    x.risk1Bps + 2 * x.risk2Bps ≤ p.maxRiskNumerator :=
  ((accepted_iff p x).mp h).2.2.2.2.2.2.2.2

theorem no_probability_can_bypass_false_fact (p : Policy) (x : Packet)
    (h : p.reviewedFact = false) : evaluate p x ≠ .accepted := by
  intro ha
  have ht := accepted_requires_reviewed_fact p x ha
  simp [h] at ht

theorem no_probability_can_bypass_bad_certificate (p : Policy) (x : Packet)
    (h : ¬ certificateValid p x) : evaluate p x ≠ .accepted := by
  intro ha
  exact h (accepted_requires_certificate p x ha)

theorem unrecognized_model_is_invalid (p : Policy) (x : Packet)
    (h : x.model ≠ "jev-1.14.0") : evaluate p x = .invalid := by
  have hn : ¬ packetValid x := fun hv => h hv.1
  simp [evaluate, hn]

theorem replay_is_deterministic (p₁ p₂ : Policy) (x₁ x₂ : Packet)
    (hp : p₁ = p₂) (hx : x₁ = x₂) : evaluate p₁ x₁ = evaluate p₂ x₂ := by
  cases hp
  cases hx
  rfl

/- A complete, synthetic, reviewed policy bundle. The semantics of this sentence
   were reviewed by the application author; Lean checks equality and gates. -/
def demoPolicy : Policy := {
  id := "synthetic-refund-v1"
  sourceId := "synthetic-ledger-TX42-v1"
  sourceLine := "TX42 was charged twice; the duplicate amount is USD 25.00."
  factId := "duplicate-charge-25-reviewed"
  reviewedFact := true
  validFrom := 20261101
  validThrough := 20261130
  day := 20261115
}

def demoPacket : Packet := {
  model := "jev-1.14.0"
  policyId := demoPolicy.id
  sourceId := demoPolicy.sourceId
  quote := demoPolicy.sourceLine
  factId := demoPolicy.factId
  choice := "refund"
  refundBps := 9900
  reviewBps := 90
  noneBps := 10
  supportNoulBps := 9950
  risk0Bps := 9900
  risk1Bps := 90
  risk2Bps := 10
}

end Bridge
