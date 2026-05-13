{-# LANGUAGE FlexibleInstances #-}
{-# LANGUAGE TemplateHaskell #-}

module Strategy.HedgehogGbE where

import Etna.Lib
import qualified Hedgehog as HH
import qualified Hedgehog.Gen as Gen
import qualified Hedgehog.Range as Range
import Impl
import Spec

-- Generation-by-execution: produce a list of (Key, Val) pairs and fold
-- the correct insert function over them. The resulting tree is always a
-- valid BST, so we wire with `Correct` (no precondition filter).
correctInsert :: Key -> Val -> Tree Key Val -> Tree Key Val
correctInsert k v E = T E k v E
correctInsert k v (T l k' v' r)
  | k < k' = T (correctInsert k v l) k' v' r
  | k > k' = T l k' v' (correctInsert k v r)
  | otherwise = T l k' v r

genBSTGbEH :: HH.Gen BST
genBSTGbEH = do
  kvs <-
    Gen.list
      (Range.linear 0 32)
      ( (,)
          <$> (Key <$> Gen.int (Range.linearFrom 0 (-1000) 1000))
          <*> (Val <$> Gen.int (Range.linearFrom 0 (-1000) 1000))
      )
  pure $ foldr (uncurry correctInsert) E kvs

class HGen a where
  hgen :: HH.Gen a

instance HGen BST where
  hgen = genBSTGbEH

instance HGen Key where
  hgen = Key <$> Gen.int (Range.linearFrom 0 (-1000) 1000)

instance HGen Val where
  hgen = Val <$> Gen.int (Range.linearFrom 0 (-1000) 1000)

instance (HGen a, HGen b) => HGen (a, b) where
  hgen = (,) <$> hgen <*> hgen

instance (HGen a, HGen b, HGen c) => HGen (a, b, c) where
  hgen = (,,) <$> hgen <*> hgen <*> hgen

instance (HGen a, HGen b, HGen c, HGen d) => HGen (a, b, c, d) where
  hgen = (,,,) <$> hgen <*> hgen <*> hgen <*> hgen

instance (HGen a, HGen b, HGen c, HGen d, HGen e) => HGen (a, b, c, d, e) where
  hgen = (,,,,) <$> hgen <*> hgen <*> hgen <*> hgen <*> hgen

$( mkStrategies
     [|hhRunGen hhDefaults Correct hgen|]
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

test_UnionUnionIdem = hhRunGen hhDefaults Correct hgen prop_UnionUnionIdem
