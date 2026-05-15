{-# LANGUAGE FlexibleInstances #-}
{-# LANGUAGE TemplateHaskell #-}
{-# LANGUAGE TupleSections #-}

module Strategy.FalsifyCBC where

import Data.List.NonEmpty (NonEmpty (..))
import Etna.Lib
import Impl (Term (..), Typ (..))
import Spec
import qualified Test.Falsify.Generator as Gen
import Test.Falsify.Generator (Gen)
import qualified Test.Falsify.Range as Range
import Util

-- Correct-by-construction System F<: generator (Falsify flavour). Mirrors
-- Strategy.Correct / Strategy.HedgehogCBC.
--
-- Falsify's Gen monad has no `discard`, so we replace the QC pattern
-- `maybe discard return mt` at the top level with a Var-0 fallback. The
-- property's `isJust (getTyp 40 Empty t)` precondition will then make
-- that test case vacuously true rather than counting as a real run, so
-- the fallback is safe (just slightly wasteful).

-- Falsify port of Etna.Lib.Strategy.QuickCheck.backtrack.
backtrackF :: [(Word, Gen (Maybe a))] -> Gen (Maybe a)
backtrackF gs0 = go (sum (map fst gs0)) gs0
  where
    go _ [] = pure Nothing
    go tot gs = do
      n <- Gen.int (Range.between (1, fromIntegral tot))
      let (k, g, gs') = pickDrop (fromIntegral n) gs
      ma <- g
      case ma of
        Just _  -> pure ma
        Nothing -> go (tot - k) gs'

    pickDrop :: Word -> [(Word, Gen (Maybe a))] -> (Word, Gen (Maybe a), [(Word, Gen (Maybe a))])
    pickDrop _ [] = (0, pure Nothing, [])
    pickDrop n ((k, g) : rest)
      | n <= k    = (k, g, rest)
      | otherwise =
          let (k', g', rest') = pickDrop (n - k) rest
           in (k', g', (k, g) : rest')

oneofF :: [Gen a] -> Gen a
oneofF gs = Gen.frequency [(1, g) | g <- gs]

oneofF_ :: Gen a -> [Gen a] -> Gen a
oneofF_ base [] = base
oneofF_ _    gs = oneofF gs

elementsF_ :: a -> [a] -> Gen a
elementsF_ base []     = pure base
elementsF_ _    (x:xs) = Gen.elem (x :| xs)

frequencyF_ :: Gen a -> [(Word, Gen a)] -> Gen a
frequencyF_ base ias =
  case filter ((> 0) . fst) ias of
    [] -> base
    xs -> Gen.frequency xs

(<$$>) :: (Functor f, Functor g) => (a -> b) -> f (g a) -> f (g b)
(<$$>) = fmap . fmap

-- Generator for types --

genExactTypF :: Int -> Env -> Gen Typ
genExactTypF 0 e = genExactTyp0F e
genExactTypF n' e =
  Gen.frequency [(2, genAll), (2, genArr), (1, genExactTyp0F e)]
  where
    n = n' - 1

    genAll = do
      ty1 <- oneofF [pure Top, genExactTypF n e]
      ty2 <- genExactTypF n (EBound e ty1)
      pure (All ty1 ty2)

    genArr = do
      ty1 <- oneofF_ (genExactTypF n e) (genExactTVar0F' e)
      ty2 <- genExactTypF n (EVar e ty1)
      pure (Arr ty1 ty2)

genExactTyp0F :: Env -> Gen Typ
genExactTyp0F e =
  let base = pure (All Top (Arr (TVar 0) (TVar 0)))
      gs =
        map
          ( \g -> do
              ty <- g
              pure (Arr ty ty)
          )
          (genExactTVar0F' e)
   in frequencyF_ base (map (1,) gs)

genExactTVar0F' :: Env -> [Gen Typ]
genExactTVar0F' e =
  case countTVar e of
    0 -> []
    n -> [TVar <$> Gen.int (Range.between (0, n - 1))]

countTVar :: Env -> Int
countTVar Empty        = 0
countTVar (EVar e _)   = countTVar e
countTVar (EBound e _) = 1 + countTVar e

-- Generator for terms --

genExactTermF :: Int -> Env -> Typ -> Gen (Maybe Term)
genExactTermF 0 e ty = genExactTerm0F e ty
genExactTermF n' e ty =
  backtrackF [(1, g0), (1, g1), (1, g2), (1, g3), (1, g4)]
  where
    n = n' - 1

    g0 = genExactTerm0F e ty

    g1 = case ty of
      Arr ty1 ty2 -> Abs  ty1 <$$> genExactTermF n (EVar e ty1)  ty2
      All ty1 ty2 -> TAbs ty1 <$$> genExactTermF n (EBound e ty1) ty2
      _ -> pure Nothing

    g2 = do
      ty1 <- genExactTypF n e
      t1  <- genExactTermF n e (Arr ty1 ty)
      t2  <- genExactTermF n e ty1
      pure (App <$> t1 <*> t2)

    g3 = do
      ty1 <- genExactTypF n e
      t1  <- genExactTermF n e (All ty1 (tshift 0 ty))
      pure (TApp <$> t1 <*> Just ty1)

    g4 = do
      tup <- genReplaceF ty
      case tup of
        Nothing -> pure Nothing
        Just (ty2, ty12) -> do
          t1 <- genExactTermF n e (All ty2 ty12)
          pure (TApp <$> t1 <*> Just ty2)

genExactTerm0F :: Env -> Typ -> Gen (Maybe Term)
genExactTerm0F e ty = backtrackF [(1, g), (1, genBoundVarsF e ty)]
  where
    g = case ty of
      Arr ty1 ty2 -> Abs  ty1 <$$> genExactTerm0F (EVar e ty1)  ty2
      All ty1 ty2 -> TAbs ty1 <$$> genExactTerm0F (EBound e ty1) ty2
      _ -> pure Nothing

genBoundVarsF :: Env -> Typ -> Gen (Maybe Term)
genBoundVarsF e ty =
  case candidates of
    []     -> pure Nothing
    (x:xs) -> Just <$> Gen.elem (x :| xs)
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

genReplaceF :: Typ -> Gen (Maybe (Typ, Typ))
genReplaceF ty = do
  mty1 <- genCandF ty
  case mty1 of
    Nothing  -> pure Nothing
    Just ty1 -> do
      ty2 <- replaceTypF 0 (tshift 0 ty) (tshift 0 ty1)
      pure (Just (ty1, ty2))

genCandF :: Typ -> Gen (Maybe Typ)
genCandF ty = case fetchCandidateTyps ty of
  []     -> pure Nothing
  (x:xs) -> Just <$> Gen.elem (x :| xs)

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

replaceTypF :: Int -> Typ -> Typ -> Gen Typ
replaceTypF n ty ty' = frequencyF_ (pure ty) ((fromIntegral (n + 2), g2) : g1)
  where
    g1 = if ty == ty' then [(fromIntegral (n + 2), pure (TVar n))] else [(1, pure ty)]

    g2 = case ty of
      Arr ty1 ty2 -> do
        ty1' <- replaceTypF n ty1 ty'
        ty2' <- replaceTypF n ty2 ty'
        pure (Arr ty1' ty2')
      All ty1 ty2 -> do
        ty1' <- replaceTypF n ty1 ty'
        ty2' <- replaceTypF (n + 1) ty2 (tshift 0 ty')
        pure (All ty1' ty2')
      _ -> frequencyF_ (pure ty) g1

tshift :: Int -> Typ -> Typ
tshift x (TVar y)
  | x <= y    = TVar (1 + y)
  | otherwise = TVar y
tshift _ Top = Top
tshift x (Arr ty1 ty2) = Arr (tshift x ty1) (tshift x ty2)
tshift x (All ty1 ty2) = All (tshift x ty1) (tshift (1 + x) ty2)

class FGen a where
  fgen :: Gen a

instance FGen Typ where
  fgen = genExactTypF 4 Empty

instance FGen Term where
  fgen = do
    ty <- genExactTypF 4 Empty
    mt <- genExactTermF 4 Empty ty
    case mt of
      Just t  -> pure t
      Nothing -> pure (Var 0)  -- vacuous: getTyp will return Nothing, precondition fails

$( mkStrategies
     [|fsRunGen fsDefaults Correct fgen|]
     [ 'prop_SinglePreserve,
       'prop_MultiPreserve
     ]
 )
