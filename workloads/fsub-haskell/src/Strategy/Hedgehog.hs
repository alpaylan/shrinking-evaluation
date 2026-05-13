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

-- Naive Typ generator (mirrors Strategy.Quick's generic-random recursion):
-- equal-weighted across the four Typ constructors with a depth budget of 4.
genTypH :: Int -> HH.Gen Typ
genTypH n
  | n <= 0 = pure Top
  | otherwise =
      Gen.frequency
        [ (1, pure Top)
        , (1, TVar <$> Gen.int (Range.linearFrom 0 (-1000) 1000))
        , (1, Arr <$> genTypH (n - 1) <*> genTypH (n - 1))
        , (1, All <$> genTypH (n - 1) <*> genTypH (n - 1))
        ]

-- Naive Term generator: equal-weighted across the five Term constructors
-- with a depth budget of 4. Var-only at depth 0 mirrors Strategy.Quick's
-- `withBaseCase (Var 0)`.
genTermH :: Int -> HH.Gen Term
genTermH n
  | n <= 0 = Var <$> Gen.int (Range.linearFrom 0 (-1000) 1000)
  | otherwise =
      Gen.frequency
        [ (1, Var <$> Gen.int (Range.linearFrom 0 (-1000) 1000))
        , (1, Abs <$> genTypH (n - 1) <*> genTermH (n - 1))
        , (1, App <$> genTermH (n - 1) <*> genTermH (n - 1))
        , (1, TAbs <$> genTypH (n - 1) <*> genTermH (n - 1))
        , (1, TApp <$> genTermH (n - 1) <*> genTypH (n - 1))
        ]

instance HGen Typ where
  hgen = genTypH 4

instance HGen Term where
  hgen = genTermH 4

$( mkStrategies
     [|hhRunGen hhDefaults Naive hgen|]
     [ 'prop_SinglePreserve,
       'prop_MultiPreserve
     ]
 )
