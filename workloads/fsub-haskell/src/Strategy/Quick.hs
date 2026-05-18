{-# LANGUAGE DeriveGeneric #-}
{-# LANGUAGE StandaloneDeriving #-}
{-# LANGUAGE TemplateHaskell #-}

module Strategy.Quick where

import Etna.Lib
import GHC.Generics (Generic)
import Impl
import Spec
import Test.QuickCheck hiding (Result)

deriving instance Generic Typ

deriving instance Generic Term

-- Var/TVar carry de Bruijn indices, so a small range keeps generated
-- variables usually in scope (matches Strategy.Hedgehog / Strategy.Falsify).
-- A wide range like +/-1000 makes nearly every term ill-typed, and fsub's
-- well-typedness precondition then discards everything -- the run finds no
-- bugs and just times out churning through discards.
genIdx :: Gen Int
genIdx = chooseInt (0, 3)

-- Naive Typ generator (matches Strategy.Hedgehog):
-- equal-weighted across the four Typ constructors with a depth budget of 4.
genTypQ :: Int -> Gen Typ
genTypQ n
  | n <= 0 = pure Top
  | otherwise = frequency
      [ (1, pure Top)
      , (1, TVar <$> genIdx)
      , (1, Arr <$> genTypQ (n - 1) <*> genTypQ (n - 1))
      , (1, All <$> genTypQ (n - 1) <*> genTypQ (n - 1))
      ]

-- Naive Term generator (matches Strategy.Hedgehog):
-- equal-weighted across the five Term constructors with a depth budget of 4.
-- Var-only at depth 0 mirrors the base case of the other strategies.
genTermQ :: Int -> Gen Term
genTermQ n
  | n <= 0 = Var <$> genIdx
  | otherwise = frequency
      [ (1, Var <$> genIdx)
      , (1, Abs <$> genTypQ (n - 1) <*> genTermQ (n - 1))
      , (1, App <$> genTermQ (n - 1) <*> genTermQ (n - 1))
      , (1, TAbs <$> genTypQ (n - 1) <*> genTermQ (n - 1))
      , (1, TApp <$> genTermQ (n - 1) <*> genTypQ (n - 1))
      ]

instance Arbitrary Typ where
  arbitrary = genTypQ 4
  shrink = genericShrink

instance Arbitrary Term where
  arbitrary = genTermQ 4
  shrink = genericShrink

$( mkStrategies
     [|qcRunArb qcDefaults Naive|]
     [ 'prop_SinglePreserve,
       'prop_MultiPreserve
     ]
 )

-- causes loop on mutant tshift_tvar_no_incr
t :: Term
t = TAbs Top (TAbs (TVar 0) (Abs (TVar 0) (App (Var 0) (Var 0))))
