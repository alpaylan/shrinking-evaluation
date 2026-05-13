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

-- Unified Typ generator (matches Strategy.Quick / Strategy.Hedgehog):
-- frequency [(1, TBool), (3, TFun ...)] with a fixed depth budget of 4.
genTypF :: Int -> Gen Typ
genTypF n
  | n <= 0 = pure TBool
  | otherwise =
      Gen.frequency
        [ (1, pure TBool)
        , (3, TFun <$> genTypF (n - 1) <*> genTypF (n - 1))
        ]

-- Unified Expr generator: equal-weighted frequencies across the four
-- constructors, fixed depth budget of 4.
genExprF :: Int -> Gen Expr
genExprF n
  | n <= 0 =
      Gen.frequency
        [ (1, Var <$> Gen.int (Range.withOrigin (-1000, 1000) 0))
        , (1, Bool <$> Gen.elem (True :| [False]))
        ]
  | otherwise =
      Gen.frequency
        [ (1, Var <$> Gen.int (Range.withOrigin (-1000, 1000) 0))
        , (1, Bool <$> Gen.elem (True :| [False]))
        , (1, Abs <$> genTypF (n - 1) <*> genExprF (n - 1))
        , (1, App <$> genExprF (n - 1) <*> genExprF (n - 1))
        ]

instance FGen Typ where
  fgen = genTypF 4

instance FGen Expr where
  fgen = genExprF 4

$( mkStrategies
     [|fsRunGen fsDefaults Naive fgen|]
     [ 'prop_SinglePreserve,
       'prop_MultiPreserve
     ]
 )
