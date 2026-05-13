{-# LANGUAGE FlexibleInstances #-}
{-# LANGUAGE TemplateHaskell #-}

-- BST CBC for Falsify with the canonical subtree-promotion shrinking
-- pattern from Test.Falsify.Generator.bst (`firstThen id (const Leaf)`).
-- Same generation distribution as FalsifyCBC; differs only in shrink
-- exposure: every recursive subtree wraps with `firstThen id (const E)`,
-- so the shrinker has explicit subtree-collapse candidates at each level.
module Strategy.FalsifyCBC2 where

import Etna.Lib
import Impl
import Spec
import qualified Test.Falsify.Generator as Gen
import Test.Falsify.Generator (Gen)
import qualified Test.Falsify.Range as Range

collapseSubtree :: Gen BST -> Gen BST
collapseSubtree g = Gen.firstThen id (const E) <*> g

genBSTCBCF2 :: Int -> Int -> Int -> Gen BST
genBSTCBCF2 depth lo hi
  | depth <= 0 || lo + 1 >= hi = pure E
  | otherwise =
      Gen.frequency
        [ (1, pure E)
        , ( 3
          , do
              k <- Gen.int (Range.between (lo + 1, hi - 1))
              v <- Gen.int (Range.withOrigin (-1000, 1000) 0)
              left  <- collapseSubtree (genBSTCBCF2 (depth - 1) lo k)
              right <- collapseSubtree (genBSTCBCF2 (depth - 1) k hi)
              pure (T left (Key k) (Val v) right)
          )
        ]

class FGen2 a where
  fgen2 :: Gen a

instance FGen2 BST where
  fgen2 = genBSTCBCF2 5 (-1000) 1000

instance FGen2 Key where
  fgen2 = Key <$> Gen.int (Range.withOrigin (-1000, 1000) 0)

instance FGen2 Val where
  fgen2 = Val <$> Gen.int (Range.withOrigin (-1000, 1000) 0)

instance (FGen2 a, FGen2 b) => FGen2 (a, b) where
  fgen2 = (,) <$> fgen2 <*> fgen2

instance (FGen2 a, FGen2 b, FGen2 c) => FGen2 (a, b, c) where
  fgen2 = (,,) <$> fgen2 <*> fgen2 <*> fgen2

instance (FGen2 a, FGen2 b, FGen2 c, FGen2 d) => FGen2 (a, b, c, d) where
  fgen2 = (,,,) <$> fgen2 <*> fgen2 <*> fgen2 <*> fgen2

instance (FGen2 a, FGen2 b, FGen2 c, FGen2 d, FGen2 e) => FGen2 (a, b, c, d, e) where
  fgen2 = (,,,,) <$> fgen2 <*> fgen2 <*> fgen2 <*> fgen2 <*> fgen2

$( mkStrategies
     [|fsRunGen fsDefaults Correct fgen2|]
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

test_UnionUnionIdem = fsRunGen fsDefaults Correct fgen2 prop_UnionUnionIdem
