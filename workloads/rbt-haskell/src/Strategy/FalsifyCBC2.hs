{-# LANGUAGE FlexibleInstances #-}
{-# LANGUAGE TemplateHaskell #-}

-- Falsify CBC RBT generator using the canonical subtree-promotion shrinking
-- pattern from Test.Falsify.Generator.bst (firstThen id (const Leaf)).
-- Same generation distribution as FalsifyCBC, but each recursive subtree is
-- wrapped so the shrinker can collapse it to E directly.
module Strategy.FalsifyCBC2 where

import Etna.Lib
import Impl
import Spec
import qualified Test.Falsify.Generator as Gen
import Test.Falsify.Generator (Gen)
import qualified Test.Falsify.Range as Range

collapseSubtree :: Gen RBT -> Gen RBT
collapseSubtree g = Gen.firstThen id (const E) <*> g

-- See Strategy.QuickCBC for design rationale of the bh-aware key
-- padding. CBC2 wraps each recursive subtree in @collapseSubtree@ so
-- Falsify's shrinker can collapse it directly to E during shrinking.
--
-- IMPORTANT: collapseSubtree replaces a subtree with E during *shrinking*,
-- not during *generation* — so it can break the consistent-black-height
-- invariant when shrinking fires. The Naive precondition will discard
-- such candidates, which is the expected behaviour.
genRBTCBCF2 :: Int -> Int -> Bool -> Int -> Gen RBT
genRBTCBCF2 lo hi parentRed bh
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
            l <- collapseSubtree (genRBTCBCF2 lo k False (bh - 1))
            r <- collapseSubtree (genRBTCBCF2 k hi False (bh - 1))
            pure (T B l (Key k) (Val v) r)
          redOpt = do
            k <- Gen.int (Range.between (lo + redPad, hi - redPad))
            v <- Gen.int (Range.withOrigin (-1000, 1000) 0)
            l <- collapseSubtree (genRBTCBCF2 lo k True bh)
            r <- collapseSubtree (genRBTCBCF2 k hi True bh)
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

blackenRootF2 :: RBT -> RBT
blackenRootF2 E = E
blackenRootF2 (T _ l k v r) = T B l k v r

genRBTRootF2 :: Gen RBT
genRBTRootF2 = do
  bh <- Gen.int (Range.between (1, 3))
  blackenRootF2 <$> genRBTCBCF2 (-1000) 1000 False bh

class FGen2 a where
  fgen2 :: Gen a

instance FGen2 RBT where
  fgen2 = genRBTRootF2

instance FGen2 Key where
  fgen2 = Key <$> Gen.int (Range.withOrigin (-1000, 1000) 0)

instance FGen2 Val where
  fgen2 = Val <$> Gen.int (Range.withOrigin (-1000, 1000) 0)

instance FGen2 Color where
  fgen2 = Gen.bool False >>= \b -> pure (if b then R else B)

instance (FGen2 a, FGen2 b) => FGen2 (a, b) where
  fgen2 = (,) <$> fgen2 <*> fgen2

instance (FGen2 a, FGen2 b, FGen2 c) => FGen2 (a, b, c) where
  fgen2 = (,,) <$> fgen2 <*> fgen2 <*> fgen2

instance (FGen2 a, FGen2 b, FGen2 c, FGen2 d) => FGen2 (a, b, c, d) where
  fgen2 = (,,,) <$> fgen2 <*> fgen2 <*> fgen2 <*> fgen2

instance (FGen2 a, FGen2 b, FGen2 c, FGen2 d, FGen2 e) => FGen2 (a, b, c, d, e) where
  fgen2 = (,,,,) <$> fgen2 <*> fgen2 <*> fgen2 <*> fgen2 <*> fgen2

$( mkStrategies
     [|fsRunGen fsDefaults Naive fgen2|]
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
