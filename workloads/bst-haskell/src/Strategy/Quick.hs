{-# LANGUAGE DeriveGeneric #-}
{-# LANGUAGE FlexibleInstances #-}
{-# LANGUAGE StandaloneDeriving #-}
{-# LANGUAGE TemplateHaskell #-}

module Strategy.Quick where

import Etna.Lib
import GHC.Generics (Generic)
import Impl
import Spec
import Test.QuickCheck

deriving instance Generic BST

-- Unified BST generator (matches Strategy.Hedgehog / Strategy.Falsify):
-- frequency [(1, E), (3, T ...)] with a fixed depth budget of 5.
genBSTQ :: Int -> Gen BST
genBSTQ n
  | n <= 0 = pure E
  | otherwise = frequency
      [ (1, pure E)
      , (3, T <$> genBSTQ (n - 1) <*> arbitrary <*> arbitrary <*> genBSTQ (n - 1))
      ]

instance Arbitrary BST where
  arbitrary = genBSTQ 5
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

-- TODO: library expects tuple
test_UnionUnionIdem = qcRunArb qcDefaults Correct prop_UnionUnionIdem
