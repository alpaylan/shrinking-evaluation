{-# LANGUAGE DeriveGeneric #-}
{-# LANGUAGE StandaloneDeriving #-}
{-# LANGUAGE TemplateHaskell #-}

module Strategy.Quick where

import Etna.Lib
import Data.Maybe
import GHC.Generics
import Generic.Random
import Impl
import Spec
import Test.QuickCheck hiding (Result)

deriving instance Generic Typ
deriving instance Generic Expr

-- Unified Typ generator (matches Strategy.Hedgehog / Strategy.Falsify):
-- frequency [(1, TBool), (3, TFun ...)] with a fixed depth budget of 4.
genTypQ :: Int -> Gen Typ
genTypQ n
  | n <= 0 = pure TBool
  | otherwise = frequency
      [ (1, pure TBool)
      , (3, TFun <$> genTypQ (n - 1) <*> genTypQ (n - 1))
      ]

-- Unified Expr generator: equal-weighted frequencies across the four
-- constructors, fixed depth budget of 4.
genExprQ :: Int -> Gen Expr
genExprQ n
  | n <= 0 = frequency
      [ (1, Var <$> chooseInt (-1000, 1000))
      , (1, Bool <$> arbitrary)
      ]
  | otherwise = frequency
      [ (1, Var <$> chooseInt (-1000, 1000))
      , (1, Bool <$> arbitrary)
      , (1, Abs <$> genTypQ (n - 1) <*> genExprQ (n - 1))
      , (1, App <$> genExprQ (n - 1) <*> genExprQ (n - 1))
      ]

instance Arbitrary Typ where
  arbitrary = genTypQ 4
  shrink = genericShrink

instance Arbitrary Expr where
  arbitrary = genExprQ 4
  shrink = genericShrink

$( mkStrategies
     [|qcRunArb qcDefaults Naive|]
     [ 'prop_SinglePreserve,
       'prop_MultiPreserve
     ]
 )