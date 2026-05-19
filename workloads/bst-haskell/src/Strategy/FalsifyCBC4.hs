{-# LANGUAGE FlexibleInstances #-}
{-# LANGUAGE TemplateHaskell #-}

-- BST CBC for Falsify mirroring Test.Falsify.Generator.bst exactly:
--   * key at each split is the midpoint of the inclusive interval
--     (deterministic, not random)
--   * Leaf-vs-Branch choice at every level is `firstThen id (const Leaf)`
--   * recursion bound by interval exhaustion, not a depth counter
--
-- Only randomness in the *structure* is the cascade of firstThen bits.
-- Values are sampled per-node.
--
-- Compared to FalsifyCBC3:
--   * CBC3 used random keys; this uses fixed midpoint
--   * CBC3 capped at depth=5; this recurses until the interval is empty
--     (~log2(range) levels — log2(2000) ≈ 11)
module Strategy.FalsifyCBC4 where

import Etna.Lib
import Impl
import Spec
import qualified Test.Falsify.Generator as Gen
import Test.Falsify.Generator (Gen)
import qualified Test.Falsify.Range as Range

-- Generate a BST for the inclusive interval (lo, hi). Stops when the
-- interval contains no integers. Each split's key is the deterministic
-- midpoint; left/right subtrees are wrapped with `firstThen id (const E)`
-- so the shrinker has a single-bit "collapse subtree" hint at every level.
genBSTCBCF4 :: Int -> Int -> Gen BST
genBSTCBCF4 lo hi
  | lo > hi   = pure E
  | otherwise = Gen.firstThen id (const E) <*> branchGen
  where
    mid       = lo + (hi - lo) `div` 2
    branchGen = do
      v     <- Gen.int (Range.withOrigin (-1000, 1000) 0)
      left  <- genBSTCBCF4 lo (mid - 1)
      right <- genBSTCBCF4 (mid + 1) hi
      pure (T left (Key mid) (Val v) right)

class FGen4 a where
  fgen4 :: Gen a

instance FGen4 BST where
  fgen4 = genBSTCBCF4 (-1000) 1000

instance FGen4 Key where
  fgen4 = Key <$> Gen.int (Range.withOrigin (-1000, 1000) 0)

instance FGen4 Val where
  fgen4 = Val <$> Gen.int (Range.withOrigin (-1000, 1000) 0)

instance (FGen4 a, FGen4 b) => FGen4 (a, b) where
  fgen4 = (,) <$> fgen4 <*> fgen4

instance (FGen4 a, FGen4 b, FGen4 c) => FGen4 (a, b, c) where
  fgen4 = (,,) <$> fgen4 <*> fgen4 <*> fgen4

instance (FGen4 a, FGen4 b, FGen4 c, FGen4 d) => FGen4 (a, b, c, d) where
  fgen4 = (,,,) <$> fgen4 <*> fgen4 <*> fgen4 <*> fgen4

instance (FGen4 a, FGen4 b, FGen4 c, FGen4 d, FGen4 e) => FGen4 (a, b, c, d, e) where
  fgen4 = (,,,,) <$> fgen4 <*> fgen4 <*> fgen4 <*> fgen4 <*> fgen4

$( mkStrategies
     [|fsRunGen fsDefaults Naive fgen4|]
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

test_UnionUnionIdem = fsRunGen fsDefaults Naive fgen4 prop_UnionUnionIdem
