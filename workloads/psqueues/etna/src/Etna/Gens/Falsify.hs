module Etna.Gens.Falsify where

import qualified Test.Falsify.Generator as F
import qualified Test.Falsify.Range     as FR

import           Etna.Properties

------------------------------------------------------------------------------
-- gen_ord_psq_from_list_last_occurrence_wins
------------------------------------------------------------------------------

gen_ord_psq_from_list_last_occurrence_wins :: F.Gen FromListArgs
gen_ord_psq_from_list_last_occurrence_wins = do
  -- Match upstream's `arbitraryAction`: keys/values unbounded
  -- (Falsify needs a finite range so we use minBound..maxBound),
  -- priority tightly clustered for collisions.
  n  <- F.integral (FR.between (0, 100))
  xs <- mapM (const tripleGen) [1 .. (n :: Int)]
  pure (FromListArgs xs)
  where
    tripleGen = do
      k <- F.integral (FR.withOrigin (-200, 200) 0)
      p <- F.integral (FR.withOrigin (-10, 10) 0)
      v <- F.integral (FR.withOrigin (-200, 200) 0)
      pure (k, p, v)

------------------------------------------------------------------------------
-- gen_hash_psq_insert_equal_priority_key_tie_break
------------------------------------------------------------------------------

gen_hash_psq_insert_equal_priority_key_tie_break :: F.Gen EqPriorityArgs
gen_hash_psq_insert_equal_priority_key_tie_break = do
  k1 <- F.integral (FR.withOrigin (-200, 200) 0)
  k2 <- F.integral (FR.withOrigin (-200, 200) 0)
  p  <- F.integral (FR.withOrigin (-10, 10) 0)
  v1 <- F.integral (FR.withOrigin (-200, 200) 0)
  v2 <- F.integral (FR.withOrigin (-200, 200) 0)
  -- Property discards when k1 == k2; bump one to avoid wasting cycles.
  let k2' = if k2 == k1 then k1 + 1 else k2
  pure (EqPriorityArgs k1 k2' p v1 v2)

------------------------------------------------------------------------------
-- gen_ord_psq_balance_after_operations
------------------------------------------------------------------------------

gen_ord_psq_balance_after_operations :: F.Gen BalanceArgs
gen_ord_psq_balance_after_operations = do
  -- Match upstream `arbitraryPSQ`: 0..100 ops, 10:2:2 frequency
  -- between Insert / Delete-by-key / DeleteMin.
  n   <- F.integral (FR.between (0, 100))
  ops <- mapM (const opGen) [1 .. (n :: Int)]
  pure (BalanceArgs ops)
  where
    opGen :: F.Gen BalanceOp
    opGen = do
      tag <- F.integral (FR.between (0, 13 :: Int))
      if tag <= 1
        then pure OpDeleteMin
        else if tag <= 3
          then OpDelete <$> F.integral (FR.withOrigin (-200, 200) 0)
          else OpInsert <$> F.integral (FR.withOrigin (-200, 200) 0)
                        <*> F.integral (FR.withOrigin (-10, 10) 0)
                        <*> F.integral (FR.withOrigin (-200, 200) 0)
