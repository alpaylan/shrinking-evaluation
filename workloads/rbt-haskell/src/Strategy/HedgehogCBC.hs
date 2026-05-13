{-# LANGUAGE FlexibleInstances #-}
{-# LANGUAGE TemplateHaskell #-}

module Strategy.HedgehogCBC where

import Etna.Lib
import qualified Hedgehog as HH
import qualified Hedgehog.Gen as Gen
import qualified Hedgehog.Range as Range
import Impl
import Spec

-- Correct-by-construction RBT generator (Hedgehog flavour). Mirrors
-- Strategy.QuickCBC; see that module for the design rationale of the
-- bh-aware key padding.
genRBTCBCH :: Int -> Int -> Bool -> Int -> HH.Gen RBT
genRBTCBCH lo hi parentRed bh
  | bh <= 1 = pure E
  | otherwise =
      let blackPad = max 1 (minWidth (bh - 1))
          redPad   = max 1 (minWidth bh)
          width    = hi - lo
          canBlack = width >= 2 * blackPad
          canRed   = not parentRed && width >= 2 * redPad
          blackOpt = do
            k <- Gen.int (Range.linearFrom 0 (lo + blackPad) (hi - blackPad))
            v <- Gen.int (Range.linearFrom 0 (-1000) 1000)
            l <- genRBTCBCH lo k False (bh - 1)
            r <- genRBTCBCH k hi False (bh - 1)
            pure (T B l (Key k) (Val v) r)
          redOpt = do
            k <- Gen.int (Range.linearFrom 0 (lo + redPad) (hi - redPad))
            v <- Gen.int (Range.linearFrom 0 (-1000) 1000)
            l <- genRBTCBCH lo k True bh
            r <- genRBTCBCH k hi True bh
            pure (T R l (Key k) (Val v) r)
       in case (canBlack, canRed) of
            (True, True)   -> Gen.frequency [(1, blackOpt), (1, redOpt)]
            (True, False)  -> blackOpt
            (False, _)     -> pure E
  where
    minWidth :: Int -> Int
    minWidth b
      | b <= 1   = 0
      | otherwise = 2 * max 1 (minWidth (b - 1))

blackenRootH :: RBT -> RBT
blackenRootH E = E
blackenRootH (T _ l k v r) = T B l k v r

genRBTRootH :: HH.Gen RBT
genRBTRootH = do
  bh <- Gen.int (Range.linear 1 3)
  blackenRootH <$> genRBTCBCH (-1000) 1000 False bh

class HGen a where
  hgen :: HH.Gen a

instance HGen RBT where
  hgen = genRBTRootH

instance HGen Key where
  hgen = Key <$> Gen.int (Range.linearFrom 0 (-1000) 1000)

instance HGen Val where
  hgen = Val <$> Gen.int (Range.linearFrom 0 (-1000) 1000)

instance HGen Color where
  hgen = Gen.choice [pure R, pure B]

instance (HGen a, HGen b) => HGen (a, b) where
  hgen = (,) <$> hgen <*> hgen

instance (HGen a, HGen b, HGen c) => HGen (a, b, c) where
  hgen = (,,) <$> hgen <*> hgen <*> hgen

instance (HGen a, HGen b, HGen c, HGen d) => HGen (a, b, c, d) where
  hgen = (,,,) <$> hgen <*> hgen <*> hgen <*> hgen

instance (HGen a, HGen b, HGen c, HGen d, HGen e) => HGen (a, b, c, d, e) where
  hgen = (,,,,) <$> hgen <*> hgen <*> hgen <*> hgen <*> hgen

$( mkStrategies
     [|hhRunGen hhDefaults Naive hgen|]
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
