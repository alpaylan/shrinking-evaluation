{-# LANGUAGE FlexibleInstances #-}
{-# LANGUAGE TemplateHaskell #-}

module Strategy.FalsifyCBC2 where

import Data.List.NonEmpty (NonEmpty (..))
import Etna.Lib
import Impl
import Spec
import qualified Test.Falsify.Generator as Gen
import Test.Falsify.Generator (Gen)
import qualified Test.Falsify.Range as Range

-- FalsifyCBC v2: same type-directed body as FalsifyCBC, but the term
-- depth is sampled from a shrinkable Range so smaller depths arise
-- naturally during shrinking. We also use `firstThen` at each
-- recursion step to bias the choice between an interior node and a
-- leaf — the first sample picks "interior", but shrinking flips it
-- to "leaf", giving subtree-promotion-style minimisation.

oneofF :: [Gen a] -> Gen a
oneofF gs = Gen.frequency [(1, g) | g <- gs]

genTypFCBC2 :: Word -> Gen Typ
genTypFCBC2 n
  | n == 0 = pure TBool
  | otherwise =
      Gen.frequency
        [ (1, pure TBool)
        , (1, TFun <$> genTypFCBC2 (n `div` 2) <*> genTypFCBC2 (n `div` 2))
        ]

-- Sample depth from 0..maxDepth shrinking toward 0. The starting size
-- (4) matches Correct.hs's sized default for stlc.
maxDepth :: Word
maxDepth = 4

-- `firstThen interior leaf` returns `interior` first; shrinking flips to `leaf`.
-- This is the idiomatic Falsify pattern for "bigger version is a shrink of smaller".
chooseLeafOrInterior :: Gen a -> Gen a -> Gen a
chooseLeafOrInterior interior leaf = do
  pickInterior <- Gen.firstThen True False
  if pickInterior then interior else leaf

genExactExprF2 :: Ctx -> Typ -> Gen Expr
genExactExprF2 ctx0 t0 = do
  -- Term depth ∈ [0, maxDepth], shrinking toward 0.
  n <- fromIntegral <$> Gen.int (Range.between (0, fromIntegral maxDepth :: Int))
  go (n :: Word) ctx0 t0
  where
    go n ctx t
      | n == 0 = case genVar ctx t of
          [] -> genOne ctx t
          vs -> oneofF (genOne ctx t : vs)
      | otherwise =
          -- firstThen biases toward the interior recipe but lets shrinking pick the leaf-only path.
          chooseLeafOrInterior (interior n ctx t) (genOne ctx t)
      where
        interior k ctx' t' =
          oneofF
            ( [genOne ctx' t']
                ++ [genAbs k ctx' t1 t2 | TFun t1 t2 <- [t']]
                ++ [genApp k ctx' t']
                ++ genVar ctx' t'
            )

        genAbs k c t1 t2 = Abs t1 <$> go (k - 1) (t1 : c) t2

        genApp k c tgt = do
          t' <- genTypFCBC2 (max 1 (k `div` 2))
          e1 <- go (k `div` 2) c (TFun t' tgt)
          e2 <- go (k `div` 2) c t'
          pure (App e1 e2)

    genOne _ TBool = Bool <$> Gen.elem (True :| [False])
    genOne c (TFun t1 t2) = Abs t1 <$> genOne (t1 : c) t2

    genVar :: Ctx -> Typ -> [Gen Expr]
    genVar c t = case vars of
      []     -> []
      (v:vs) -> [Var <$> Gen.elem (v :| vs)]
      where
        vars = filter (\i -> c !! i == t) [0 .. length c - 1]

class FGen2 a where
  fgen2 :: Gen a

instance FGen2 Typ where
  fgen2 = do
    n <- fromIntegral <$> Gen.int (Range.between (0, fromIntegral maxDepth :: Int))
    genTypFCBC2 (n :: Word)

instance FGen2 Expr where
  fgen2 = do
    n <- fromIntegral <$> Gen.int (Range.between (0, fromIntegral maxDepth :: Int))
    t <- genTypFCBC2 (n :: Word)
    genExactExprF2 [] t

$( mkStrategies
     [|fsRunGen fsDefaults Correct fgen2|]
     [ 'prop_SinglePreserve,
       'prop_MultiPreserve
     ]
 )
