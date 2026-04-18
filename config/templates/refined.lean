inductive CacheState where
  | I
  | M
  deriving DecidableEq

open CacheState

def singleWriter (a b : CacheState) : Prop :=
  ¬ (a = M ∧ b = M)

theorem singleWriter_demo : singleWriter M I := by
  intro h
  cases h with
  | intro h1 h2 =>
      cases h2
