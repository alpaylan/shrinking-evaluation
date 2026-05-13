module Etna.Gens.Hedgehog where

import qualified Hedgehog       as HH
import qualified Hedgehog.Gen   as Gen
import qualified Hedgehog.Range as Range

import           Etna.Properties

------------------------------------------------------------------------------
-- gen_ord_psq_from_list_last_occurrence_wins
------------------------------------------------------------------------------

gen_ord_psq_from_list_last_occurrence_wins :: HH.Gen FromListArgs
gen_ord_psq_from_list_last_occurrence_wins = do
  -- Match upstream's `arbitraryAction` shape: keys/values unbounded,
  -- priority tightly clustered for collisions.
  xs <- Gen.list (Range.linear 0 100) $ do
    k <- Gen.int (Range.linearFrom 0 (-200) 200)
    p <- Gen.int (Range.linearFrom 0 (-10) 10)
    v <- Gen.int (Range.linearFrom 0 (-200) 200)
    pure (k, p, v)
  pure (FromListArgs xs)

------------------------------------------------------------------------------
-- gen_hash_psq_insert_equal_priority_key_tie_break
------------------------------------------------------------------------------

gen_hash_psq_insert_equal_priority_key_tie_break :: HH.Gen EqPriorityArgs
gen_hash_psq_insert_equal_priority_key_tie_break = do
  k1 <- Gen.int (Range.linearFrom 0 (-200) 200)
  k2 <- Gen.filter (/= k1) (Gen.int (Range.linearFrom 0 (-200) 200))
  p  <- Gen.int (Range.linearFrom 0 (-10) 10)
  v1 <- Gen.int (Range.linearFrom 0 (-200) 200)
  v2 <- Gen.int (Range.linearFrom 0 (-200) 200)
  pure (EqPriorityArgs k1 k2 p v1 v2)

------------------------------------------------------------------------------
-- gen_ord_psq_balance_after_operations
------------------------------------------------------------------------------

gen_ord_psq_balance_after_operations :: HH.Gen BalanceArgs
gen_ord_psq_balance_after_operations = do
  -- Mirror upstream `arbitraryPSQ`: 0..100 actions, 10:2:2 frequency
  -- between Insert / Delete-by-key / DeleteMin.
  ops <- Gen.list (Range.linear 0 100) genOp
  pure (BalanceArgs ops)

genOp :: HH.Gen BalanceOp
genOp = Gen.frequency
  [ (10, OpInsert <$> Gen.int (Range.linearFrom 0 (-200) 200)
                  <*> Gen.int (Range.linearFrom 0 (-10) 10)
                  <*> Gen.int (Range.linearFrom 0 (-200) 200))
  , (2,  OpDelete <$> Gen.int (Range.linearFrom 0 (-200) 200))
  , (2,  pure OpDeleteMin)
  ]
