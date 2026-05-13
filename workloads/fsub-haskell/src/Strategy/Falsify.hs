{-# LANGUAGE TemplateHaskell #-}

module Strategy.Falsify where

import Etna.Lib
import Impl
import Spec
import qualified Test.Falsify.Generator as Gen
import Test.Falsify.Generator (Gen)
import qualified Test.Falsify.Range as Range

class FGen a where
  fgen :: Gen a

-- Naive Typ generator (mirrors Strategy.Quick / Strategy.Hedgehog):
-- equal-weighted across the four Typ constructors with depth budget 4.
genTypF :: Int -> Gen Typ
genTypF n
  | n <= 0 = pure Top
  | otherwise =
      Gen.frequency
        [ (1, pure Top)
        , (1, TVar <$> Gen.int (Range.withOrigin (-1000, 1000) 0))
        , (1, Arr <$> genTypF (n - 1) <*> genTypF (n - 1))
        , (1, All <$> genTypF (n - 1) <*> genTypF (n - 1))
        ]

genTermF :: Int -> Gen Term
genTermF n
  | n <= 0 = Var <$> Gen.int (Range.withOrigin (-1000, 1000) 0)
  | otherwise =
      Gen.frequency
        [ (1, Var <$> Gen.int (Range.withOrigin (-1000, 1000) 0))
        , (1, Abs <$> genTypF (n - 1) <*> genTermF (n - 1))
        , (1, App <$> genTermF (n - 1) <*> genTermF (n - 1))
        , (1, TAbs <$> genTypF (n - 1) <*> genTermF (n - 1))
        , (1, TApp <$> genTermF (n - 1) <*> genTypF (n - 1))
        ]

instance FGen Typ where
  fgen = genTypF 4

instance FGen Term where
  fgen = genTermF 4

$( mkStrategies
     [|fsRunGen fsDefaults Naive fgen|]
     [ 'prop_SinglePreserve,
       'prop_MultiPreserve
     ]
 )
