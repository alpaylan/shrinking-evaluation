{-# LANGUAGE FlexibleInstances #-}
{-# LANGUAGE TemplateHaskell #-}

module Strategy.Falsify where

import Etna.Lib
import Impl
import Spec
import qualified Test.Falsify.Generator as Gen
import Test.Falsify.Generator (Gen)
import qualified Test.Falsify.Range as Range

class FGen a where
  fgen :: Gen a

instance FGen Key where
  fgen = Key <$> Gen.int (Range.withOrigin (-1000, 1000) 0)

instance FGen Val where
  fgen = Val <$> Gen.int (Range.withOrigin (-1000, 1000) 0)

-- Unified BST generator (matches Strategy.Quick / Strategy.Hedgehog):
-- frequency [(1, E), (3, T ...)] with a fixed depth budget of 5.
genBSTF :: Int -> Gen BST
genBSTF n
  | n <= 0 = pure E
  | otherwise =
      Gen.frequency
        [ (1, pure E)
        , (3, T <$> genBSTF (n - 1) <*> fgen <*> fgen <*> genBSTF (n - 1))
        ]

instance FGen BST where
  fgen = genBSTF 5

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
