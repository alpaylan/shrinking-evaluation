{-# LANGUAGE FlexibleInstances #-}
{-# LANGUAGE TemplateHaskell #-}

module Strategy.HedgehogCBC where

import Etna.Lib
import qualified Hedgehog as HH
import qualified Hedgehog.Gen as Gen
import qualified Hedgehog.Range as Range
import Impl
import Spec

-- Correct-by-construction STLC generator (Hedgehog flavour). Mirrors
-- Strategy.Correct: pick a target type, then build an expression of that
-- type so typeCheck is satisfied by construction. Wired with `Correct`
-- (no precondition filter).

genTypHCBC :: Int -> HH.Gen Typ
genTypHCBC n
  | n <= 0 = pure TBool
  | otherwise =
      Gen.choice
        [ pure TBool
        , TFun <$> genTypHCBC (n `div` 2) <*> genTypHCBC (n `div` 2)
        ]

genExactExprH :: Ctx -> Typ -> HH.Gen Expr
genExactExprH = go 4
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
          t' <- genTypHCBC 4
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
  hgen = genTypHCBC 4

instance HGen Expr where
  hgen = do
    t <- genTypHCBC 4
    genExactExprH [] t

$( mkStrategies
     [|hhRunGen hhDefaults Correct hgen|]
     [ 'prop_SinglePreserve,
       'prop_MultiPreserve
     ]
 )
