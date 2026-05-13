module Etna.Gens.QuickCheck where

import qualified Test.QuickCheck as QC

import           Etna.Properties

------------------------------------------------------------------------------
-- gen_ord_psq_from_list_last_occurrence_wins
--
-- Generates a list of (key, prio, value) triples drawing from a small
-- key pool so that duplicate keys are common -- otherwise every random
-- list would be all-unique and the bug would never trigger.
------------------------------------------------------------------------------

gen_ord_psq_from_list_last_occurrence_wins :: QC.Gen FromListArgs
gen_ord_psq_from_list_last_occurrence_wins = do
  -- Mirrors upstream `arbitraryAction` shape: keys via default
  -- `arbitrary :: Gen Int` (unbounded, size-scaled), priorities in the
  -- tight `arbitraryPriority` range of (-10, 10) for collisions, values
  -- via default `arbitrary`.
  len <- QC.choose (0, 100)
  xs  <- QC.vectorOf len $ do
    k <- QC.arbitrary
    p <- QC.choose (-10, 10)
    v <- QC.arbitrary
    pure (k, p, v)
  pure (FromListArgs xs)

------------------------------------------------------------------------------
-- gen_hash_psq_insert_equal_priority_key_tie_break
--
-- Two distinct Int keys, a shared priority, and two value tags.
------------------------------------------------------------------------------

gen_hash_psq_insert_equal_priority_key_tie_break :: QC.Gen EqPriorityArgs
gen_hash_psq_insert_equal_priority_key_tie_break = do
  k1 <- QC.arbitrary
  k2 <- QC.arbitrary `QC.suchThat` (/= k1)
  p  <- QC.choose (-10, 10)
  v1 <- QC.arbitrary
  v2 <- QC.arbitrary
  pure (EqPriorityArgs k1 k2 p v1 v2)

------------------------------------------------------------------------------
-- gen_ord_psq_balance_after_operations
--
-- Sequence of insert/delete operations. Keys are drawn from a small
-- pool to keep deletes meaningful (a delete with a never-inserted key
-- is a no-op).
------------------------------------------------------------------------------

gen_ord_psq_balance_after_operations :: QC.Gen BalanceArgs
gen_ord_psq_balance_after_operations = do
  -- Mirror upstream `arbitraryPSQ`: 0..100 actions, frequency 10:2:2
  -- between Insert / Delete-by-key / DeleteMin. Upstream uses
  -- DeleteRandomMember (pick from existing keys) which we approximate
  -- with OpDelete on a small key pool — collisions with prior inserts
  -- give a similar effect.
  len <- QC.choose (0, 100)
  ops <- QC.vectorOf len genOp
  pure (BalanceArgs ops)

genOp :: QC.Gen BalanceOp
genOp = QC.frequency
  [ (10, OpInsert <$> QC.arbitrary
                  <*> QC.choose (-10, 10)
                  <*> QC.arbitrary)
  , (2,  OpDelete <$> QC.arbitrary)
  , (2,  pure OpDeleteMin)
  ]

------------------------------------------------------------------------------
-- Shrink functions. Used via @forAllShrink@ in the runner so that QC
-- can actually walk down to a smaller failing input — without these
-- the args types have no @Arbitrary@ instance and shrinking is a no-op.

shrinkTriple :: (Int, Int, Int) -> [(Int, Int, Int)]
shrinkTriple (k, p, v) =
  [(k', p, v) | k' <- QC.shrink k] ++
  [(k, p', v) | p' <- QC.shrink p] ++
  [(k, p, v') | v' <- QC.shrink v]

shrink_ord_psq_from_list_last_occurrence_wins :: FromListArgs -> [FromListArgs]
shrink_ord_psq_from_list_last_occurrence_wins (FromListArgs xs) =
  -- Property requires the list to have at least one duplicate key to
  -- exercise the last-occurrence semantics, but we leave that to the
  -- shrinker / property to short-circuit; just run a generic list shrink.
  FromListArgs <$> QC.shrinkList shrinkTriple xs

shrink_hash_psq_insert_equal_priority_key_tie_break :: EqPriorityArgs -> [EqPriorityArgs]
shrink_hash_psq_insert_equal_priority_key_tie_break args =
  -- Five fixed Int fields. Shrink each toward 0 independently. Skip
  -- shrinks that collapse k1 == k2 (the property discards on equal keys).
  [ args { epK1 = k1' } | k1' <- QC.shrink (epK1 args), k1' /= epK2 args ] ++
  [ args { epK2 = k2' } | k2' <- QC.shrink (epK2 args), k2' /= epK1 args ] ++
  [ args { epPrio = p' } | p' <- QC.shrink (epPrio args) ] ++
  [ args { epV1 = v' }   | v' <- QC.shrink (epV1 args) ] ++
  [ args { epV2 = v' }   | v' <- QC.shrink (epV2 args) ]

shrinkOp :: BalanceOp -> [BalanceOp]
shrinkOp (OpInsert k p v) =
  [OpInsert k' p v | k' <- QC.shrink k] ++
  [OpInsert k p' v | p' <- QC.shrink p] ++
  [OpInsert k p v' | v' <- QC.shrink v]
shrinkOp (OpDelete k) =
  [OpDelete k' | k' <- QC.shrink k]
shrinkOp OpDeleteMin = []  -- nullary, nothing to shrink

shrink_ord_psq_balance_after_operations :: BalanceArgs -> [BalanceArgs]
shrink_ord_psq_balance_after_operations (BalanceArgs ops) =
  BalanceArgs <$> QC.shrinkList shrinkOp ops
