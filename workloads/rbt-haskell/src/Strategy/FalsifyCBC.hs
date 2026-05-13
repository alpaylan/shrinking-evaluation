{-# LANGUAGE FlexibleInstances #-}
{-# LANGUAGE TemplateHaskell #-}

module Strategy.FalsifyCBC where

import Etna.Lib
import Impl
import Spec
import qualified Test.Falsify.Generator as Gen
import Test.Falsify.Generator (Gen)
import qualified Test.Falsify.Range as Range

-- Correct-by-construction RBT generator (Falsify flavour). See
-- Strategy.QuickCBC for design rationale of the bh-aware key padding.
genRBTCBCF :: Int -> Int -> Bool -> Int -> Gen RBT
genRBTCBCF lo hi parentRed bh
  | bh <= 1 = pure E
  | otherwise =
      let blackPad = max 1 (minWidth (bh - 1))
          redPad   = max 1 (minWidth bh)
          width    = hi - lo
          canBlack = width >= 2 * blackPad
          canRed   = not parentRed && width >= 2 * redPad
          blackOpt = do
            k <- Gen.int (Range.between (lo + blackPad, hi - blackPad))
            v <- Gen.int (Range.withOrigin (-1000, 1000) 0)
            l <- genRBTCBCF lo k False (bh - 1)
            r <- genRBTCBCF k hi False (bh - 1)
            pure (T B l (Key k) (Val v) r)
          redOpt = do
            k <- Gen.int (Range.between (lo + redPad, hi - redPad))
            v <- Gen.int (Range.withOrigin (-1000, 1000) 0)
            l <- genRBTCBCF lo k True bh
            r <- genRBTCBCF k hi True bh
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

blackenRootF :: RBT -> RBT
blackenRootF E = E
blackenRootF (T _ l k v r) = T B l k v r

genRBTRootF :: Gen RBT
genRBTRootF = do
  bh <- Gen.int (Range.between (1, 3))
  blackenRootF <$> genRBTCBCF (-1000) 1000 False bh

class FGen a where
  fgen :: Gen a

instance FGen RBT where
  fgen = genRBTRootF

instance FGen Key where
  fgen = Key <$> Gen.int (Range.withOrigin (-1000, 1000) 0)

instance FGen Val where
  fgen = Val <$> Gen.int (Range.withOrigin (-1000, 1000) 0)

instance FGen Color where
  fgen = Gen.bool False >>= \b -> pure (if b then R else B)

instance (FGen a, FGen b) => FGen (a, b) where
  fgen = (,) <$> fgen <*> fgen

instance (FGen a, FGen b, FGen c) => FGen (a, b, c) where
  fgen = (,,) <$> fgen <*> fgen <*> fgen

instance (FGen a, FGen b, FGen c, FGen d) => FGen (a, b, c, d) where
  fgen = (,,,) <$> fgen <*> fgen <*> fgen <*> fgen

instance (FGen a, FGen b, FGen c, FGen d, FGen e) => FGen (a, b, c, d, e) where
  fgen = (,,,,) <$> fgen <*> fgen <*> fgen <*> fgen <*> fgen

$( mkStrategies
     [|fsRunGen fsDefaults Naive fgen|]
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
