{-# LANGUAGE FlexibleInstances #-}
{-# LANGUAGE TemplateHaskell #-}

module Strategy.Hedgehog where

import Etna.Lib
import qualified Hedgehog as HH
import qualified Hedgehog.Gen as Gen
import qualified Hedgehog.Range as Range
import Impl
import Spec

class HGen a where
  hgen :: HH.Gen a

instance HGen Key where
  hgen = Key <$> Gen.int (Range.linearFrom 0 (-1000) 1000)

instance HGen Val where
  hgen = Val <$> Gen.int (Range.linearFrom 0 (-1000) 1000)

instance HGen Color where
  hgen = Gen.choice [pure R, pure B]

-- Unified RBT generator (matches Strategy.Quick / Strategy.Falsify):
-- frequency [(1, E), (3, T ...)] with a fixed depth budget of 5.
genRBTH :: Int -> HH.Gen RBT
genRBTH n
  | n <= 0 = pure E
  | otherwise =
      Gen.frequency
        [ (1, pure E)
        , (3, T <$> hgen <*> genRBTH (n - 1) <*> hgen <*> hgen <*> genRBTH (n - 1))
        ]

instance HGen RBT where
  hgen = genRBTH 5

instance (HGen a, HGen b) => HGen (a, b) where
  hgen = (,) <$> hgen <*> hgen

instance (HGen a, HGen b, HGen c) => HGen (a, b, c) where
  hgen = (,,) <$> hgen <*> hgen <*> hgen

instance (HGen a, HGen b, HGen c, HGen d) => HGen (a, b, c, d) where
  hgen = (,,,) <$> hgen <*> hgen <*> hgen <*> hgen

instance (HGen a, HGen b, HGen c, HGen d, HGen e) => HGen (a, b, c, d, e) where
  hgen = (,,,,) <$> hgen <*> hgen <*> hgen <*> hgen <*> hgen

$( mkStrategies
     [|hhRunGen hhDefaults Naive hgen|]
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
