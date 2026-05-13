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
-- valid RBT.
correctInsertRBT :: Key -> Val -> Tree Key Val -> Tree Key Val
correctInsertRBT k v s = blacken (ins k v s)
  where
    ins x vx E = T R E x vx E
    ins x vx (T rb a y vy b)
      | x < y = balance rb (ins x vx a) y vy b
      | x > y = balance rb a y vy (ins x vx b)
      | otherwise = T rb a y vx b

    blacken E = E
    blacken (T _ a y vy b) = T B a y vy b

    balance B (T R (T R a x vx b) y vy c) z vz d = T R (T B a x vx b) y vy (T B c z vz d)
    balance B (T R a x vx (T R b y vy c)) z vz d = T R (T B a x vx b) y vy (T B c z vz d)
    balance B a x vx (T R (T R b y vy c) z vz d) = T R (T B a x vx b) y vy (T B c z vz d)
    balance B a x vx (T R b y vy (T R c z vz d)) = T R (T B a x vx b) y vy (T B c z vz d)
    balance rb a x vx b = T rb a x vx b

genRBTGbEF :: Gen RBT
genRBTGbEF = do
  kvs <-
    Gen.list
      (Range.between (0, 32))
      ( (,)
          <$> (Key <$> Gen.int (Range.withOrigin (-1000, 1000) 0))
          <*> (Val <$> Gen.int (Range.withOrigin (-1000, 1000) 0))
      )
  pure $ foldr (uncurry correctInsertRBT) E kvs

class FGen a where
  fgen :: Gen a

instance FGen RBT where
  fgen = genRBTGbEF

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
