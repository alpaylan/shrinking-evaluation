{-# LANGUAGE FlexibleInstances #-}
{-# LANGUAGE TemplateHaskell #-}

module Strategy.Falsify where

import Data.List.NonEmpty (NonEmpty (..))
import Etna.Lib
import Impl
import Spec
import qualified Test.Falsify.Generator as Gen
import Test.Falsify.Generator (Gen)
import qualified Test.Falsify.Range as Range

class FGen a where
  fgen :: Gen a

instance FGen Key where
  fgen = Key <$> Gen.int (Range.withOrigin (-1000, 1000) 0)

instance FGen Val where
  fgen = Val <$> Gen.int (Range.withOrigin (-1000, 1000) 0)

instance FGen Color where
  fgen = Gen.elem (R :| [B])

-- Unified RBT generator (matches Strategy.Quick / Strategy.Hedgehog):
-- frequency [(1, E), (3, T ...)] with a fixed depth budget of 5.
genRBTF :: Int -> Gen RBT
genRBTF n
  | n <= 0 = pure E
  | otherwise =
      Gen.frequency
        [ (1, pure E)
        , (3, T <$> fgen <*> genRBTF (n - 1) <*> fgen <*> fgen <*> genRBTF (n - 1))
        ]

instance FGen RBT where
  fgen = genRBTF 5

instance (FGen a, FGen b) => FGen (a, b) where
  fgen = (,) <$> fgen <*> fgen

instance (FGen a, FGen b, FGen c) => FGen (a, b, c) where
  fgen = (,,) <$> fgen <*> fgen <*> fgen

instance (FGen a, FGen b, FGen c, FGen d) => FGen (a, b, c, d) where
  fgen = (,,,) <$> fgen <*> fgen <*> fgen <*> fgen

instance (FGen a, FGen b, FGen c, FGen d, FGen e) => FGen (a, b, c, d, e) where
  fgen = (,,,,) <$> fgen <*> fgen <*> fgen <*> fgen <*> fgen

$( mkStrategies
     [|fsRunGen fsDefaults Naive fgen|]
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
