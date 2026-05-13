{-# LANGUAGE DeriveGeneric #-}
{-# LANGUAGE FlexibleInstances #-}
{-# LANGUAGE StandaloneDeriving #-}
{-# LANGUAGE TemplateHaskell #-}

module Strategy.QuickCBC where

import Etna.Lib
import GHC.Generics (Generic)
import Impl
import Spec
import Test.QuickCheck hiding (Result)

deriving instance Generic BST

-- Correct-by-construction BST generator: every generated tree satisfies
-- the BST invariant by construction. Each node picks a key strictly
-- between the inherited (lo, hi) bounds, then recurses with the bounds
-- tightened on each side. Because the precondition is guaranteed, this
-- module wires the strategies with `Correct` (no precondition filter).
genBSTCBC :: Int -> Int -> Int -> Gen BST
genBSTCBC depth lo hi
  | depth <= 0 || lo + 1 >= hi = pure E
  | otherwise =
      frequency
        [ (1, pure E)
        , ( 3
          , do
              k <- chooseInt (lo + 1, hi - 1)
              v <- chooseInt (-1000, 1000)
              left <- genBSTCBC (depth - 1) lo k
              right <- genBSTCBC (depth - 1) k hi
              pure (T left (Key k) (Val v) right)
          )
        ]

instance Arbitrary BST where
  arbitrary = genBSTCBC 5 (-1000) 1000
  -- Structural shrinks may produce trees that violate the BST invariant.
  -- That's fine: we wire with `Naive` below so the property's
  -- precondition (`isBST t`) discards invalid candidates, letting QC
  -- continue exploring smaller-but-valid shrinks.
  shrink = genericShrink

instance Arbitrary Key where
  arbitrary = Key <$> chooseInt (-1000, 1000)
  shrink (Key n) = Key <$> shrink n

instance Arbitrary Val where
  arbitrary = Val <$> chooseInt (-1000, 1000)
  shrink (Val n) = Val <$> shrink n

$( mkStrategies
     [|qcRunArb qcDefaults Naive|]
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

test_UnionUnionIdem = qcRunArb qcDefaults Naive prop_UnionUnionIdem
