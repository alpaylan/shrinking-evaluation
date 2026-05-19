{-# LANGUAGE FlexibleInstances #-}
{-# LANGUAGE TemplateHaskell #-}

module Strategy.HedgehogCBC where

import Etna.Lib
import qualified Hedgehog as HH
import qualified Hedgehog.Gen as Gen
import qualified Hedgehog.Range as Range
import Hedgehog.Range (Size (..))
import Impl
import Spec

-- Correct-by-construction STLC generator (Hedgehog flavour). Mirrors
-- Strategy.Correct: pick a target type, then build a well-typed Expr.
-- Depth is taken from Hedgehog's ambient `Size` (Gen.sized) so it grows
-- during testing — matching stlc Strategy.Correct's QC `sized` behaviour.
-- Wired with `Correct` (no precondition filter).

genTypHCBC :: Int -> HH.Gen Typ
genTypHCBC n
  | n <= 0 = pure TBool
  | otherwise =
      Gen.choice
        [ pure TBool
        , TFun <$> genTypHCBC (n `div` 2) <*> genTypHCBC (n `div` 2)
        ]

genExactExprH :: Ctx -> Typ -> HH.Gen Expr
genExactExprH ctx0 t0 = Gen.sized $ \(Size sz) -> go sz ctx0 t0
  where
    go n ctx t
      | n <= 0 = case genVar ctx t of
          [] -> genOne ctx t
          vs -> Gen.choice (genOne ctx t : vs)
      | otherwise =
          Gen.choice
            ( [genOne ctx t]
                ++ [genAbs ctx t1 t2 | TFun t1 t2 <- [t]]
                ++ [genApp ctx t]
                ++ genVar ctx t
            )
      where
        genAbs c t1 t2 = Abs t1 <$> go (n - 1) (t1 : c) t2

        genApp c tgt = do
          t' <- genTypHCBC (max 1 (n `div` 2))
          e1 <- go (n `div` 2) c (TFun t' tgt)
          e2 <- go (n `div` 2) c t'
          pure (App e1 e2)

    genOne _ TBool = Bool <$> Gen.element [True, False]
    genOne c (TFun t1 t2) = Abs t1 <$> genOne (t1 : c) t2

    genVar :: Ctx -> Typ -> [HH.Gen Expr]
    genVar c t = [Var <$> Gen.element vars | not (null vars)]
      where
        vars = filter (\i -> c !! i == t) [0 .. length c - 1]

class HGen a where
  hgen :: HH.Gen a

instance HGen Typ where
  hgen = Gen.sized $ \(Size sz) -> genTypHCBC sz

instance HGen Expr where
  hgen = do
    t <- Gen.sized $ \(Size sz) -> genTypHCBC sz
    genExactExprH [] t

$( mkStrategies
     [|hhRunGen hhDefaults Naive hgen|]
     [ 'prop_SinglePreserve,
       'prop_MultiPreserve
     ]
 )
