{-# LANGUAGE DeriveGeneric #-}
{-# LANGUAGE FlexibleInstances #-}
{-# LANGUAGE StandaloneDeriving #-}
{-# LANGUAGE TemplateHaskell #-}

module Strategy.QuickGbE where

import Etna.Lib
import GHC.Generics (Generic)
import Impl
import Spec
import Test.QuickCheck hiding (Result)

deriving instance Generic BST

correctInsert :: Key -> Val -> Tree Key Val -> Tree Key Val
correctInsert k v E = T E k v E
correctInsert k v (T l k' v' r)
  | k < k' = T (correctInsert k v l) k' v' r
  | k > k' = T l k' v' (correctInsert k v r)
  | otherwise = T l k' v r

instance Arbitrary BST where
  arbitrary = do
    kvs <- arbitrary :: Gen [(Key, Val)]
    return $ foldr (uncurry correctInsert) E kvs
  -- Structural shrinks may break the BST invariant; the precondition
  -- (Naive approach) discards invalid candidates and QC keeps exploring.
  shrink = genericShrink

instance Arbitrary Key where
  arbitrary = Key <$> arbitrary
  shrink (Key n) = Key <$> shrink n

instance Arbitrary Val where
  arbitrary = Val <$> arbitrary
  shrink (Val n) = Val <$> shrink n

$( mkStrategies
     [|qcRunArb qcDefaults Naive|]
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

-- TODO: library expects tuple
test_UnionUnionIdem = qcRunArb qcDefaults Naive prop_UnionUnionIdem