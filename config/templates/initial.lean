inductive CacheState where
  | I
  | M
  deriving DecidableEq

open CacheState

def singleWriter (a b : CacheState) : Prop :=
  ¬ (a = M ∧ b = M)

theorem __THEOREM_NAME__ : singleWriter M I := by
  rfl
