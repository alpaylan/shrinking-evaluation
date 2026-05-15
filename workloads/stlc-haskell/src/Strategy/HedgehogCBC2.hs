{-# LANGUAGE FlexibleInstances #-}
{-# LANGUAGE TemplateHaskell #-}

module Strategy.HedgehogCBC2 where

import Etna.Lib
import qualified Hedgehog as HH
import qualified Hedgehog.Gen as Gen
import qualified Hedgehog.Range as Range
import Hedgehog.Range (Size (..))
import Impl
import Spec

-- HedgehogCBC v2: same type-directed generator as HedgehogCBC, but the
-- term depth is taken from Hedgehog's ambient `Size` (Gen.sized) so it
-- grows during testing — mirroring Strategy.Correct's QC `sized`
-- behaviour. The fixed-depth-4 in v1 misses counterexamples for weak
-- mutations (shift_var_leq, subst_abs_no_shift); this should close
-- the gap.

genTypHCBC2 :: Int -> HH.Gen Typ
genTypHCBC2 n
  | n <= 0 = pure TBool
  | otherwise =
      Gen.choice
        [ pure TBool
        , TFun <$> genTypHCBC2 (n `div` 2) <*> genTypHCBC2 (n `div` 2)
        ]

genExactExprH2 :: Ctx -> Typ -> HH.Gen Expr
genExactExprH2 ctx0 t0 = Gen.sized $ \(Size sz) -> go sz ctx0 t0
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
          -- Type depth tracks term depth so types don't dominate.
          t' <- genTypHCBC2 (max 1 (n `div` 2))
          e1 <- go (n `div` 2) c (TFun t' tgt)
          e2 <- go (n `div` 2) c t'
          pure (App e1 e2)

    genOne _ TBool = Bool <$> Gen.element [True, False]
    genOne c (TFun t1 t2) = Abs t1 <$> genOne (t1 : c) t2

    genVar :: Ctx -> Typ -> [HH.Gen Expr]
    genVar c t = [Var <$> Gen.element vars | not (null vars)]
      where
        vars = filter (\i -> c !! i == t) [0 .. length c - 1]

class HGen2 a where
  hgen2 :: HH.Gen a

instance HGen2 Typ where
  hgen2 = Gen.sized $ \(Size sz) -> genTypHCBC2 sz

instance HGen2 Expr where
  hgen2 = do
    t <- Gen.sized $ \(Size sz) -> genTypHCBC2 sz
    genExactExprH2 [] t

$( mkStrategies
     [|hhRunGen hhDefaults Correct hgen2|]
     [ 'prop_SinglePreserve,
       'prop_MultiPreserve
     ]
 )
