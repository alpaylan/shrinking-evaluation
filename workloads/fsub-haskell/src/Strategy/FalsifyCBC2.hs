{-# LANGUAGE FlexibleInstances #-}
{-# LANGUAGE TemplateHaskell #-}

module Strategy.FalsifyCBC2 where

import Etna.Lib
import Impl (Term (..), Typ (..))
import Spec
import Strategy.FalsifyCBC (genExactTermF, genExactTypF)
import qualified Test.Falsify.Generator as Gen
import Test.Falsify.Generator (Gen)
import qualified Test.Falsify.Range as Range
import Util

-- FalsifyCBC v2: reuses FalsifyCBC's backtracking type-directed
-- generator, but the term depth is sampled from a shrinkable Range so
-- smaller depths arise naturally during shrinking. Replaces v1's
-- hardcoded depth = 4.

maxDepth :: Int
maxDepth = 4

class FGen2 a where
  fgen2 :: Gen a

instance FGen2 Typ where
  fgen2 = do
    n <- Gen.int (Range.between (0, maxDepth))
    genExactTypF n Empty

instance FGen2 Term where
  fgen2 = do
    n <- Gen.int (Range.between (0, maxDepth))
    ty <- genExactTypF n Empty
    mt <- genExactTermF n Empty ty
    case mt of
      Just t  -> pure t
      Nothing -> pure (Var 0)  -- vacuous: getTyp fails, precondition trips

$( mkStrategies
     [|fsRunGen fsDefaults Correct fgen2|]
     [ 'prop_SinglePreserve,
       'prop_MultiPreserve
     ]
 )
