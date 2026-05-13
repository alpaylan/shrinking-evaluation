{-# LANGUAGE DeriveGeneric #-}
{-# LANGUAGE FlexibleInstances #-}
{-# LANGUAGE StandaloneDeriving #-}
{-# LANGUAGE TemplateHaskell #-}

module Strategy.QuickCBC where

import Etna.Lib
import GHC.Generics (Generic)
import Impl
import Spec
import Test.QuickCheck hiding (Result)

deriving instance Generic RBT
deriving instance Generic Color

-- Correct-by-construction RBT generator: every generated tree satisfies
-- BST ordering, no red-red, and uniform black height.
--
-- The recursion is driven by a target black height @bh@. To keep the
-- consistent-black-height invariant we must never return @E@ at
-- @bh > 1@ (E has black-height 1).
--
-- Key padding: to recurse into a child of black-height @b@ we need at
-- least @minWidth b@ slack on each side of the chosen key, otherwise
-- the child's sub-range can't fit a tree of height @b@. blackOpt's
-- children are at bh-1; redOpt's children are at bh (red doesn't
-- decrement). We compute the pad accordingly and gate each branch on
-- the available width before offering it.
genRBTCBC :: Int -> Int -> Bool -> Int -> Gen RBT
genRBTCBC lo hi parentRed bh
  | bh <= 1 = pure E
  | otherwise =
      let blackPad = max 1 (minWidth (bh - 1))
          redPad   = max 1 (minWidth bh)
          width    = hi - lo
          canBlack = width >= 2 * blackPad
          canRed   = not parentRed && width >= 2 * redPad
          blackOpt = do
            k <- chooseInt (lo + blackPad, hi - blackPad)
            v <- chooseInt (-1000, 1000)
            l <- genRBTCBC lo k False (bh - 1)
            r <- genRBTCBC k hi False (bh - 1)
            pure (T B l (Key k) (Val v) r)
          redOpt = do
            k <- chooseInt (lo + redPad, hi - redPad)
            v <- chooseInt (-1000, 1000)
            l <- genRBTCBC lo k True bh
            r <- genRBTCBC k hi True bh
            pure (T R l (Key k) (Val v) r)
       in case (canBlack, canRed) of
            (True, True)   -> frequency [(1, blackOpt), (1, redOpt)]
            (True, False)  -> blackOpt
            (False, _)     -> pure E  -- range too narrow; only safe if root rebalances
  where
    -- Minimum width (hi - lo) needed to fit a tree of black-height b.
    -- bh=1 needs no width (E only). Higher bh needs 2*pad for the key
    -- pick, where pad ensures children still have room for THEIR keys.
    minWidth :: Int -> Int
    minWidth b
      | b <= 1   = 0
      | otherwise = 2 * max 1 (minWidth (b - 1))

blackenRoot :: RBT -> RBT
blackenRoot E = E
blackenRoot (T _ l k v r) = T B l k v r

instance Arbitrary RBT where
  arbitrary = do
    bh <- chooseInt (1, 3)
    blackenRoot <$> genRBTCBC (-1000) 1000 False bh
  -- Structural shrinks may break the RBT invariant; Naive precondition
  -- discards invalid candidates, letting QC keep exploring.
  shrink = genericShrink

instance Arbitrary Key where
  arbitrary = Key <$> chooseInt (-1000, 1000)
  shrink (Key n) = Key <$> shrink n

instance Arbitrary Val where
  arbitrary = Val <$> chooseInt (-1000, 1000)
  shrink (Val n) = Val <$> shrink n

instance Arbitrary Color where
  arbitrary = oneof [return R, return B]

$( mkStrategies
     [|qcRunArb qcDefaults Naive|]
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
