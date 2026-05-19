{-# LANGUAGE FlexibleInstances #-}
{-# LANGUAGE TemplateHaskell #-}

-- BST CBC for Falsify using the actually-idiomatic recursive tree
-- pattern from Test.Falsify.Generator.bst — `firstThen id (const Leaf)`
-- at the *choice point* between Leaf and Branch.
--
-- Difference from FalsifyCBC and FalsifyCBC2:
--
--   * FalsifyCBC: `Gen.frequency [(1, pure E), (3, Branch...)]` at the
--     choice point. Frequency walks `perturb genIx gen`, so shrinking the
--     index re-shrinks everything inside.
--   * FalsifyCBC2: same `Gen.frequency` at choice point BUT wraps each
--     recursive subtree with `firstThen id (const E)`. The shrink-hint
--     only applies to subtrees, not to the top-of-recursion choice.
--   * FalsifyCBC3 (this module): replaces `Gen.frequency` entirely with
--     `firstThen id (const E) <*> branchGen`. The Leaf vs Branch decision
--     is one bit of shrink choice with no perturb.
--
-- Matches the structure of `Test.Falsify.Generator.bst` in the falsify
-- library itself.
module Strategy.FalsifyCBC3 where

import Etna.Lib
import Impl
import Spec
import qualified Test.Falsify.Generator as Gen
import Test.Falsify.Generator (Gen)
import qualified Test.Falsify.Range as Range

genBSTCBCF3 :: Int -> Int -> Int -> Gen BST
genBSTCBCF3 depth lo hi
  | depth <= 0 || lo + 1 >= hi = pure E
  | otherwise =
      Gen.firstThen id (const E) <*> branchGen
  where
    branchGen = do
      k     <- Gen.int (Range.between (lo + 1, hi - 1))
      v     <- Gen.int (Range.withOrigin (-1000, 1000) 0)
      left  <- genBSTCBCF3 (depth - 1) lo k
      right <- genBSTCBCF3 (depth - 1) k hi
      pure (T left (Key k) (Val v) right)

class FGen3 a where
  fgen3 :: Gen a

instance FGen3 BST where
  fgen3 = genBSTCBCF3 5 (-1000) 1000

instance FGen3 Key where
  fgen3 = Key <$> Gen.int (Range.withOrigin (-1000, 1000) 0)

instance FGen3 Val where
  fgen3 = Val <$> Gen.int (Range.withOrigin (-1000, 1000) 0)

instance (FGen3 a, FGen3 b) => FGen3 (a, b) where
  fgen3 = (,) <$> fgen3 <*> fgen3

instance (FGen3 a, FGen3 b, FGen3 c) => FGen3 (a, b, c) where
  fgen3 = (,,) <$> fgen3 <*> fgen3 <*> fgen3

instance (FGen3 a, FGen3 b, FGen3 c, FGen3 d) => FGen3 (a, b, c, d) where
  fgen3 = (,,,) <$> fgen3 <*> fgen3 <*> fgen3 <*> fgen3

instance (FGen3 a, FGen3 b, FGen3 c, FGen3 d, FGen3 e) => FGen3 (a, b, c, d, e) where
  fgen3 = (,,,,) <$> fgen3 <*> fgen3 <*> fgen3 <*> fgen3 <*> fgen3

$( mkStrategies
     [|fsRunGen fsDefaults Naive fgen3|]
     [ 'prop_InsertValid,
       'prop_DeleteValid,
       'prop_UnionValid,
       'prop_InsertPost,
       'prop_DeletePost,
       'prop_UnionPost,
       'prop_InsertModel,
       'prop_DeleteModel,
       'prop_UnionModel,
       'prop_InsertInsert,
       'prop_InsertDelete,
       'prop_InsertUnion,
       'prop_DeleteInsert,
       'prop_DeleteDelete,
       'prop_DeleteUnion,
       'prop_UnionDeleteInsert,
       'prop_UnionUnionAssoc
     ]
 )

test_UnionUnionIdem = fsRunGen fsDefaults Naive fgen3 prop_UnionUnionIdem
