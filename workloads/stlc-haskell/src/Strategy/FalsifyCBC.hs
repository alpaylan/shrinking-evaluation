{-# LANGUAGE FlexibleInstances #-}
{-# LANGUAGE TemplateHaskell #-}

module Strategy.FalsifyCBC where

import Data.List.NonEmpty (NonEmpty (..))
import Etna.Lib
import Impl
import Spec
import qualified Test.Falsify.Generator as Gen
import Test.Falsify.Generator (Gen)
import qualified Test.Falsify.Range as Range

-- Correct-by-construction STLC generator (Falsify flavour). Mirrors
-- Strategy.Correct / Strategy.HedgehogCBC. Wired with `Correct` (no
-- precondition filter) because every generated Expr is well-typed.

-- Falsify has no `oneof`; we use equal-weighted `frequency` instead.
oneofF :: [Gen a] -> Gen a
oneofF gs = Gen.frequency [(1, g) | g <- gs]

genTypFCBC :: Int -> Gen Typ
genTypFCBC n
  | n <= 0 = pure TBool
  | otherwise =
      Gen.frequency
        [ (1, pure TBool)
        , (1, TFun <$> genTypFCBC (n `div` 2) <*> genTypFCBC (n `div` 2))
        ]

genExactExprF :: Ctx -> Typ -> Gen Expr
genExactExprF = go 4
  where
    go n ctx t
      | n <= 0 = case genVar ctx t of
          [] -> genOne ctx t
          vs -> oneofF (genOne ctx t : vs)
      | otherwise =
          oneofF
            ( [genOne ctx t]
                ++ [genAbs ctx t1 t2 | TFun t1 t2 <- [t]]
                ++ [genApp ctx t]
                ++ genVar ctx t
            )
      where
        genAbs c t1 t2 = Abs t1 <$> go (n - 1) (t1 : c) t2

        genApp c tgt = do
          t' <- genTypFCBC 4
          e1 <- go (n `div` 2) c (TFun t' tgt)
          e2 <- go (n `div` 2) c t'
          pure (App e1 e2)

    genOne _ TBool = Bool <$> Gen.elem (True :| [False])
    genOne c (TFun t1 t2) = Abs t1 <$> genOne (t1 : c) t2

    genVar :: Ctx -> Typ -> [Gen Expr]
    genVar c t = case vars of
      []     -> []
      (v:vs) -> [Var <$> Gen.elem (v :| vs)]
      where
        vars = filter (\i -> c !! i == t) [0 .. length c - 1]

class FGen a where
  fgen :: Gen a

instance FGen Typ where
  fgen = genTypFCBC 4

instance FGen Expr where
  fgen = do
    t <- genTypFCBC 4
    genExactExprF [] t

$( mkStrategies
     [|fsRunGen fsDefaults Correct fgen|]
     [ 'prop_SinglePreserve,
       'prop_MultiPreserve
     ]
 )
