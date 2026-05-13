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

-- Unified Typ generator (matches Strategy.Quick / Strategy.Falsify):
-- frequency [(1, TBool), (3, TFun ...)] with a fixed depth budget of 4.
genTypH :: Int -> HH.Gen Typ
genTypH n
  | n <= 0 = pure TBool
  | otherwise =
      Gen.frequency
        [ (1, pure TBool)
        , (3, TFun <$> genTypH (n - 1) <*> genTypH (n - 1))
        ]

-- Unified Expr generator: equal-weighted frequencies across the four
-- constructors, fixed depth budget of 4.
genExprH :: Int -> HH.Gen Expr
genExprH n
  | n <= 0 =
      Gen.frequency
        [ (1, Var <$> Gen.int (Range.linearFrom 0 (-1000) 1000))
        , (1, Bool <$> Gen.choice [pure True, pure False])
        ]
  | otherwise =
      Gen.frequency
        [ (1, Var <$> Gen.int (Range.linearFrom 0 (-1000) 1000))
        , (1, Bool <$> Gen.choice [pure True, pure False])
        , (1, Abs <$> genTypH (n - 1) <*> genExprH (n - 1))
        , (1, App <$> genExprH (n - 1) <*> genExprH (n - 1))
        ]

instance HGen Typ where
  hgen = genTypH 4

instance HGen Expr where
  hgen = genExprH 4

$( mkStrategies
     [|hhRunGen hhDefaults Naive hgen|]
     [ 'prop_SinglePreserve,
       'prop_MultiPreserve
     ]
 )
