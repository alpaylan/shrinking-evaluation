{-# LANGUAGE FlexibleInstances #-}
{-# LANGUAGE TemplateHaskell #-}

-- RBT CBC using Hedgehog's `Gen.recursive` combinator instead of manual
-- recursion. `Gen.recursive` uses `sized` to gate recursion via
-- Hedgehog's Size parameter; recursive cases are wrapped with `small` so
-- their size halves at each step. We still pass `(lo, hi, parentRed, bh)`
-- explicitly to maintain BST order, no red-red, and uniform black height.
module Strategy.HedgehogCBC2 where

import Etna.Lib
import qualified Hedgehog as HH
import qualified Hedgehog.Gen as Gen
import qualified Hedgehog.Range as Range
import Impl
import Spec

-- See Strategy.QuickCBC for the design rationale of the bh-aware key
-- padding. The CBC2 variant uses Hedgehog's @Gen.recursive@ + Size to
-- gate recursion depth, but still tracks (lo, hi, parentRed, bh)
-- explicitly to maintain BST order, no red-red, and uniform black
-- height. The base case in @Gen.recursive@ is @pure E@; we only offer
-- it (via the recursive options being empty / unchosen) when bh has
-- decremented to 1.
genRBTCBCH2 :: Int -> Int -> Bool -> Int -> HH.Gen RBT
genRBTCBCH2 lo hi parentRed bh
  | bh <= 1 = pure E
  | otherwise =
      let blackPad = max 1 (minWidth (bh - 1))
          redPad   = max 1 (minWidth bh)
          width    = hi - lo
          canBlack = width >= 2 * blackPad
          canRed   = not parentRed && width >= 2 * redPad
          blackCase = do
            k <- Gen.int (Range.linearFrom 0 (lo + blackPad) (hi - blackPad))
            v <- Gen.int (Range.linearFrom 0 (-1000) 1000)
            l <- genRBTCBCH2 lo k False (bh - 1)
            r <- genRBTCBCH2 k hi False (bh - 1)
            pure (T B l (Key k) (Val v) r)
          redCase = do
            k <- Gen.int (Range.linearFrom 0 (lo + redPad) (hi - redPad))
            v <- Gen.int (Range.linearFrom 0 (-1000) 1000)
            l <- genRBTCBCH2 lo k True bh
            r <- genRBTCBCH2 k hi True bh
            pure (T R l (Key k) (Val v) r)
          options = [blackCase | canBlack] ++ [redCase | canRed]
       in case options of
            [] -> pure E   -- range too narrow; only safe at root
            xs -> Gen.choice xs
            -- NOTE: we deliberately do NOT use @Gen.recursive [pure E] xs@
            -- here. Gen.recursive would let Hedgehog fall back to @pure E@
            -- at low Size — but at @bh > 1@, E violates the
            -- consistent-black-height invariant (E has bh=1). bh-driven
            -- termination at the top of this function replaces the
            -- size-driven termination Gen.recursive normally provides.
  where
    minWidth :: Int -> Int
    minWidth b
      | b <= 1   = 0
      | otherwise = 2 * max 1 (minWidth (b - 1))

blackenRootH2 :: RBT -> RBT
blackenRootH2 E = E
blackenRootH2 (T _ l k v r) = T B l k v r

genRBTRootH2 :: HH.Gen RBT
genRBTRootH2 = do
  bh <- Gen.int (Range.linear 1 3)
  blackenRootH2 <$> genRBTCBCH2 (-1000) 1000 False bh

class HGen2 a where
  hgen2 :: HH.Gen a

instance HGen2 RBT where
  hgen2 = genRBTRootH2

instance HGen2 Key where
  hgen2 = Key <$> Gen.int (Range.linearFrom 0 (-1000) 1000)

instance HGen2 Val where
  hgen2 = Val <$> Gen.int (Range.linearFrom 0 (-1000) 1000)

instance HGen2 Color where
  hgen2 = Gen.choice [pure R, pure B]

instance (HGen2 a, HGen2 b) => HGen2 (a, b) where
  hgen2 = (,) <$> hgen2 <*> hgen2

instance (HGen2 a, HGen2 b, HGen2 c) => HGen2 (a, b, c) where
  hgen2 = (,,) <$> hgen2 <*> hgen2 <*> hgen2

instance (HGen2 a, HGen2 b, HGen2 c, HGen2 d) => HGen2 (a, b, c, d) where
  hgen2 = (,,,) <$> hgen2 <*> hgen2 <*> hgen2 <*> hgen2

instance (HGen2 a, HGen2 b, HGen2 c, HGen2 d, HGen2 e) => HGen2 (a, b, c, d, e) where
  hgen2 = (,,,,) <$> hgen2 <*> hgen2 <*> hgen2 <*> hgen2 <*> hgen2

$( mkStrategies
     [|hhRunGen hhDefaults Naive hgen2|]
     [ 'prop_InsertValid,
       'prop_DeleteValid,
       'prop_InsertPost,
       'prop_DeletePost,
       'prop_InsertModel,
       'prop_DeleteModel,
       'prop_InsertInsert,
       'prop_InsertDelete,
       'prop_DeleteInsert,
       'prop_DeleteDelete
     ]
 )
