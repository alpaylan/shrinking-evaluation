{-# LANGUAGE DeriveGeneric #-}
{-# LANGUAGE FlexibleInstances #-}
{-# LANGUAGE StandaloneDeriving #-}
{-# LANGUAGE TemplateHaskell #-}

module Strategy.Quick where

import Etna.Lib
import GHC.Generics
import Generic.Random
import Impl
import Spec
import Test.QuickCheck as QC hiding (Result)

deriving instance Generic RBT
deriving instance Generic Color

-- Unified RBT generator (matches Strategy.Hedgehog / Strategy.Falsify):
-- frequency [(1, E), (3, T ...)] with a fixed depth budget of 5.
genRBTQ :: Int -> Gen RBT
genRBTQ n
  | n <= 0 = pure E
  | otherwise = frequency
      [ (1, pure E)
      , (3, T <$> arbitrary <*> genRBTQ (n - 1) <*> arbitrary <*> arbitrary <*> genRBTQ (n - 1))
      ]

instance Arbitrary RBT where
  arbitrary = genRBTQ 5
  shrink = genericShrink

instance Arbitrary Key where
  arbitrary = Key <$> chooseInt (-1000, 1000)
  shrink (Key n) = Key <$> shrink n

instance Arbitrary Val where
  arbitrary = Val <$> chooseInt (-1000, 1000)
  shrink (Val n) = Val <$> shrink n

instance Arbitrary Color where
  arbitrary = oneof [return R, return B]
  shrink = genericShrink

$( mkStrategies
     [|qcRunArb qcDefaults Naive|]
     [ 'prop_InsertValid,
       'prop_DeleteValid,
       'prop_InsertPost,
       'prop_DeletePost,
       'prop_InsertModel,
       'prop_DeleteModel,
       'prop_InsertInsert,
       'prop_InsertDelete,
       'prop_DeleteInsert,
       'prop_DeleteDelete
     ]
 )