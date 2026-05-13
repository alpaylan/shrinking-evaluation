{-# LANGUAGE FlexibleInstances #-}
{-# LANGUAGE TemplateHaskell #-}

-- BST CBC using Hedgehog's `Gen.recursive` combinator instead of manual
-- depth recursion. `Gen.recursive` uses Hedgehog's `sized` to gate the
-- recursion: at size <= 1 only base cases fire, otherwise both base and
-- recursive cases (with `small` halving the size for recursive calls).
-- Differences vs HedgehogCBC:
--   * depth comes from Hedgehog's Size parameter, not a manual counter
--   * Gen.recursive uses uniform Gen.choice (no 1:3 base:rec weighting)
--   * the outer (lo, hi) interval still narrows on recursion to maintain
--     BST sortedness
module Strategy.HedgehogCBC2 where

import Etna.Lib
import qualified Hedgehog as HH
import qualified Hedgehog.Gen as Gen
import qualified Hedgehog.Range as Range
import Impl
import Spec

genBSTCBCH2 :: Int -> Int -> HH.Gen BST
genBSTCBCH2 lo hi
  | lo + 1 >= hi = pure E
  | otherwise =
      Gen.recursive Gen.choice
        [ pure E ]
        [ do
            k <- Gen.int (Range.linearFrom 0 (lo + 1) (hi - 1))
            v <- Gen.int (Range.linearFrom 0 (-1000) 1000)
            left  <- genBSTCBCH2 lo k
            right <- genBSTCBCH2 k hi
            pure (T left (Key k) (Val v) right)
        ]

class HGen2 a where
  hgen2 :: HH.Gen a

instance HGen2 BST where
  hgen2 = genBSTCBCH2 (-1000) 1000

instance HGen2 Key where
  hgen2 = Key <$> Gen.int (Range.linearFrom 0 (-1000) 1000)

instance HGen2 Val where
  hgen2 = Val <$> Gen.int (Range.linearFrom 0 (-1000) 1000)

instance (HGen2 a, HGen2 b) => HGen2 (a, b) where
  hgen2 = (,) <$> hgen2 <*> hgen2

instance (HGen2 a, HGen2 b, HGen2 c) => HGen2 (a, b, c) where
  hgen2 = (,,) <$> hgen2 <*> hgen2 <*> hgen2

instance (HGen2 a, HGen2 b, HGen2 c, HGen2 d) => HGen2 (a, b, c, d) where
  hgen2 = (,,,) <$> hgen2 <*> hgen2 <*> hgen2 <*> hgen2

instance (HGen2 a, HGen2 b, HGen2 c, HGen2 d, HGen2 e) => HGen2 (a, b, c, d, e) where
  hgen2 = (,,,,) <$> hgen2 <*> hgen2 <*> hgen2 <*> hgen2 <*> hgen2

$( mkStrategies
     [|hhRunGen hhDefaults Correct hgen2|]
     [ 'prop_InsertValid,
       'prop_DeleteValid,
       'prop_UnionValid,
       'prop_InsertPost,
       'prop_DeletePost,
       'prop_UnionPost,
       'prop_InsertModel,
       'prop_DeleteModel,
       'prop_UnionModel,
       'prop_InsertInsert,
       'prop_InsertDelete,
       'prop_InsertUnion,
       'prop_DeleteInsert,
       'prop_DeleteDelete,
       'prop_DeleteUnion,
       'prop_UnionDeleteInsert,
       'prop_UnionUnionAssoc
     ]
 )

test_UnionUnionIdem = hhRunGen hhDefaults Correct hgen2 prop_UnionUnionIdem
