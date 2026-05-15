{-# LANGUAGE FlexibleInstances #-}
{-# LANGUAGE TemplateHaskell #-}

module Strategy.HedgehogCBC2 where

import Etna.Lib
import qualified Hedgehog as HH
import qualified Hedgehog.Gen as Gen
import Hedgehog.Range (Size (..))
import Impl (Term (..), Typ (..))
import Spec
import Strategy.HedgehogCBC (genExactTermH, genExactTypH)
import Util

-- HedgehogCBC v2: same backtracking type-directed generator as
-- HedgehogCBC, but the term-depth budget is taken from Hedgehog's
-- ambient Size via Gen.sized — mirroring Strategy.Correct's QC `sized`.
-- The fixed-depth-4 in v1 misses counterexamples for weak fsub
-- mutations (subtree-promotion-only term shapes); growing depth should
-- expose them.

class HGen2 a where
  hgen2 :: HH.Gen a

instance HGen2 Typ where
  hgen2 = Gen.sized $ \(Size sz) -> genExactTypH sz Empty

instance HGen2 Term where
  hgen2 = Gen.sized $ \(Size sz) -> do
    ty <- genExactTypH sz Empty
    mt <- genExactTermH sz Empty ty
    case mt of
      Just t  -> pure t
      Nothing -> Gen.discard

$( mkStrategies
     [|hhRunGen hhDefaults Correct hgen2|]
     [ 'prop_SinglePreserve,
       'prop_MultiPreserve
     ]
 )
