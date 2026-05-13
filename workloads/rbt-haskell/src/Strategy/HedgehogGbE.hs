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
-- valid RBT, so we can wire with `Correct` (no precondition discard).
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

genRBTGbEH :: HH.Gen RBT
genRBTGbEH = do
  kvs <-
    Gen.list
      (Range.linear 0 32)
      ( (,)
          <$> (Key <$> Gen.int (Range.linearFrom 0 (-1000) 1000))
          <*> (Val <$> Gen.int (Range.linearFrom 0 (-1000) 1000))
      )
  pure $ foldr (uncurry correctInsertRBT) E kvs

class HGen a where
  hgen :: HH.Gen a

instance HGen RBT where
  hgen = genRBTGbEH

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
