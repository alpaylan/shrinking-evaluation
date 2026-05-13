{-# LANGUAGE FlexibleInstances #-}
{-# LANGUAGE TemplateHaskell #-}

module Strategy.FalsifyGbE where

import Etna.Lib
import Impl
import Spec
import qualified Test.Falsify.Generator as Gen
import Test.Falsify.Generator (Gen)
import qualified Test.Falsify.Range as Range

-- Generation-by-execution: produce a list of (Key, Val) pairs and fold
-- the correct insert function over them. The resulting tree is always a
-- valid BST, so we wire with `Correct` (no precondition filter).
correctInsert :: Key -> Val -> Tree Key Val -> Tree Key Val
correctInsert k v E = T E k v E
correctInsert k v (T l k' v' r)
  | k < k' = T (correctInsert k v l) k' v' r
  | k > k' = T l k' v' (correctInsert k v r)
  | otherwise = T l k' v r

genBSTGbEF :: Gen BST
genBSTGbEF = do
  kvs <-
    Gen.list
      (Range.between (0, 32))
      ( (,)
          <$> (Key <$> Gen.int (Range.withOrigin (-1000, 1000) 0))
          <*> (Val <$> Gen.int (Range.withOrigin (-1000, 1000) 0))
      )
  pure $ foldr (uncurry correctInsert) E kvs

class FGen a where
  fgen :: Gen a

instance FGen BST where
  fgen = genBSTGbEF

instance FGen Key where
  fgen = Key <$> Gen.int (Range.withOrigin (-1000, 1000) 0)

instance FGen Val where
  fgen = Val <$> Gen.int (Range.withOrigin (-1000, 1000) 0)

instance (FGen a, FGen b) => FGen (a, b) where
  fgen = (,) <$> fgen <*> fgen

instance (FGen a, FGen b, FGen c) => FGen (a, b, c) where
  fgen = (,,) <$> fgen <*> fgen <*> fgen

instance (FGen a, FGen b, FGen c, FGen d) => FGen (a, b, c, d) where
  fgen = (,,,) <$> fgen <*> fgen <*> fgen <*> fgen

instance (FGen a, FGen b, FGen c, FGen d, FGen e) => FGen (a, b, c, d, e) where
  fgen = (,,,,) <$> fgen <*> fgen <*> fgen <*> fgen <*> fgen

$( mkStrategies
     [|fsRunGen fsDefaults Correct fgen|]
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

test_UnionUnionIdem = fsRunGen fsDefaults Correct fgen prop_UnionUnionIdem
