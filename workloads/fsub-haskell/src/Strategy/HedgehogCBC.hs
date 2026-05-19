{-# LANGUAGE FlexibleInstances #-}
{-# LANGUAGE TemplateHaskell #-}
{-# LANGUAGE TupleSections #-}

module Strategy.HedgehogCBC where

import Etna.Lib
import qualified Hedgehog as HH
import qualified Hedgehog.Gen as Gen
import qualified Hedgehog.Range as Range
import Impl (Term (..), Typ (..))
import Spec
import Util

-- Correct-by-construction System F<: generator (Hedgehog flavour).
-- Mirrors Strategy.Correct: type-directed generation of well-typed terms.
-- Wired with `Correct` (no precondition filter).

-- Hedgehog port of Etna.Lib.Strategy.QuickCheck.backtrack: try weighted
-- alternatives in random order until one returns Just; fall back to
-- Nothing if all fail.
backtrackH :: [(Int, HH.Gen (Maybe a))] -> HH.Gen (Maybe a)
backtrackH gs0 = go (sum (map fst gs0)) gs0
  where
    go _ [] = pure Nothing
    go tot gs = do
      n <- Gen.int (Range.constant 1 tot)
      let (k, g, gs') = pickDrop n gs
      ma <- g
      case ma of
        Just _  -> pure ma
        Nothing -> go (tot - k) gs'

    pickDrop _ [] = (0, pure Nothing, [])
    pickDrop n ((k, g) : rest)
      | n <= k    = (k, g, rest)
      | otherwise =
          let (k', g', rest') = pickDrop (n - k) rest
           in (k', g', (k, g) : rest')

oneofH_ :: HH.Gen a -> [HH.Gen a] -> HH.Gen a
oneofH_ base [] = base
oneofH_ _    gs = Gen.choice gs

elementsH_ :: a -> [a] -> HH.Gen a
elementsH_ base [] = pure base
elementsH_ _    xs = Gen.element xs

frequencyH_ :: HH.Gen a -> [(Int, HH.Gen a)] -> HH.Gen a
frequencyH_ base ias =
  case filter ((> 0) . fst) ias of
    [] -> base
    xs -> Gen.frequency xs

(<$$>) :: (Functor f, Functor g) => (a -> b) -> f (g a) -> f (g b)
(<$$>) = fmap . fmap

-- Generator for types --

genExactTypH :: Int -> Env -> HH.Gen Typ
genExactTypH 0 e = genExactTyp0H e
genExactTypH n' e =
  Gen.frequency [(2, genAll), (2, genArr), (1, genExactTyp0H e)]
  where
    n = n' - 1

    genAll = do
      ty1 <- Gen.choice [pure Top, genExactTypH n e]
      ty2 <- genExactTypH n (EBound e ty1)
      pure (All ty1 ty2)

    genArr = do
      ty1 <- oneofH_ (genExactTypH n e) (genExactTVar0H' e)
      ty2 <- genExactTypH n (EVar e ty1)
      pure (Arr ty1 ty2)

genExactTyp0H :: Env -> HH.Gen Typ
genExactTyp0H e =
  let base = pure (All Top (Arr (TVar 0) (TVar 0)))
      gs =
        map
          ( \g -> do
              ty <- g
              pure (Arr ty ty)
          )
          (genExactTVar0H' e)
   in frequencyH_ base (map (1,) gs)

genExactTVar0H' :: Env -> [HH.Gen Typ]
genExactTVar0H' e =
  case countTVar e of
    0 -> []
    n -> [TVar <$> Gen.int (Range.constant 0 (n - 1))]

countTVar :: Env -> Int
countTVar Empty        = 0
countTVar (EVar e _)   = countTVar e
countTVar (EBound e _) = 1 + countTVar e

-- Generator for terms --

genExactTermH :: Int -> Env -> Typ -> HH.Gen (Maybe Term)
genExactTermH 0 e ty = genExactTerm0H e ty
genExactTermH n' e ty =
  backtrackH [(1, g0), (1, g1), (1, g2), (1, g3), (1, g4)]
  where
    n = n' - 1

    g0 = genExactTerm0H e ty

    g1 = case ty of
      Arr ty1 ty2 -> Abs  ty1 <$$> genExactTermH n (EVar e ty1)  ty2
      All ty1 ty2 -> TAbs ty1 <$$> genExactTermH n (EBound e ty1) ty2
      _ -> pure Nothing

    g2 = do
      ty1 <- genExactTypH n e
      t1  <- genExactTermH n e (Arr ty1 ty)
      t2  <- genExactTermH n e ty1
      pure (App <$> t1 <*> t2)

    g3 = do
      ty1 <- genExactTypH n e
      t1  <- genExactTermH n e (All ty1 (tshift 0 ty))
      pure (TApp <$> t1 <*> Just ty1)

    g4 = do
      tup <- genReplaceH ty
      case tup of
        Nothing -> pure Nothing
        Just (ty2, ty12) -> do
          t1 <- genExactTermH n e (All ty2 ty12)
          pure (TApp <$> t1 <*> Just ty2)

genExactTerm0H :: Env -> Typ -> HH.Gen (Maybe Term)
genExactTerm0H e ty = backtrackH [(1, g), (1, genBoundVarsH e ty)]
  where
    g = case ty of
      Arr ty1 ty2 -> Abs  ty1 <$$> genExactTerm0H (EVar e ty1)  ty2
      All ty1 ty2 -> TAbs ty1 <$$> genExactTerm0H (EBound e ty1) ty2
      _ -> pure Nothing

genBoundVarsH :: Env -> Typ -> HH.Gen (Maybe Term)
genBoundVarsH e ty =
  case candidates of
    []     -> pure Nothing
    (x:xs) -> Just <$> Gen.element (x : xs)
  where
    candidates = go 0 0 e ty

    go _ _ Empty _ = []
    go i m (EBound e' _) t = go i (m + 1) e' t
    go i m (EVar   e' ty') t =
      let rest = go (i + 1) m e' t
       in if t == tlift m ty' then Var i : rest else rest

tlift :: Int -> Typ -> Typ
tlift 0 ty = ty
tlift k ty = tlift (k - 1) (tshift 0 ty)

genReplaceH :: Typ -> HH.Gen (Maybe (Typ, Typ))
genReplaceH ty = do
  mty1 <- genCandH ty
  case mty1 of
    Nothing  -> pure Nothing
    Just ty1 -> do
      ty2 <- replaceTypH 0 (tshift 0 ty) (tshift 0 ty1)
      pure (Just (ty1, ty2))

genCandH :: Typ -> HH.Gen (Maybe Typ)
genCandH ty = case fetchCandidateTyps ty of
  []     -> pure Nothing
  (x:xs) -> Just <$> Gen.element (x : xs)

fetchCandidateTyps :: Typ -> [Typ]
fetchCandidateTyps = f 0
  where
    f :: Int -> Typ -> [Typ]
    f k ty =
      let l1 = [tunshift k ty | fetchP k ty]
          l2 = case ty of
            Arr ty1 ty2 -> f k ty1 ++ f k ty2
            All ty1 ty2 -> f k ty1 ++ f (k + 1) ty2
            _ -> []
       in l1 ++ l2

    fetchP _ Top         = True
    fetchP k (TVar k')   = k <= k'
    fetchP k (Arr a b)   = fetchP k a && fetchP k b
    fetchP k (All a b)   = fetchP k a && fetchP (k + 1) b

    tunshift _ Top         = Top
    tunshift k (TVar k')   = TVar (k' - k)
    tunshift k (Arr a b)   = Arr (tunshift k a) (tunshift k b)
    tunshift k (All a b)   = All (tunshift k a) (tunshift (k + 1) b)

replaceTypH :: Int -> Typ -> Typ -> HH.Gen Typ
replaceTypH n ty ty' = frequencyH_ (pure ty) ((n + 2, g2) : g1)
  where
    g1 = if ty == ty' then [(n + 2, pure (TVar n))] else [(1, pure ty)]

    g2 = case ty of
      Arr ty1 ty2 -> do
        ty1' <- replaceTypH n ty1 ty'
        ty2' <- replaceTypH n ty2 ty'
        pure (Arr ty1' ty2')
      All ty1 ty2 -> do
        ty1' <- replaceTypH n ty1 ty'
        ty2' <- replaceTypH (n + 1) ty2 (tshift 0 ty')
        pure (All ty1' ty2')
      _ -> frequencyH_ (pure ty) g1

-- tshift: replicated from Strategy.Correct (the correct, non-mutated impl).
tshift :: Int -> Typ -> Typ
tshift x (TVar y)
  | x <= y    = TVar (1 + y)
  | otherwise = TVar y
tshift _ Top = Top
tshift x (Arr ty1 ty2) = Arr (tshift x ty1) (tshift x ty2)
tshift x (All ty1 ty2) = All (tshift x ty1) (tshift (1 + x) ty2)

-- Top-level: pick a target type, then build a well-typed term. If the
-- backtracking generator can't find one, signal Hedgehog to discard and
-- retry.
class HGen a where
  hgen :: HH.Gen a

instance HGen Typ where
  hgen = genExactTypH 4 Empty

instance HGen Term where
  hgen = do
    ty <- genExactTypH 4 Empty
    mt <- genExactTermH 4 Empty ty
    case mt of
      Just t  -> pure t
      Nothing -> Gen.discard

$( mkStrategies
     [|hhRunGen hhDefaults Naive hgen|]
     [ 'prop_SinglePreserve,
       'prop_MultiPreserve
     ]
 )
