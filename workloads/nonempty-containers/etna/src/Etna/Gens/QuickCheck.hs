{-# LANGUAGE OverloadedStrings #-}

-- | Upstream-style PBT generators (broadened from the bug-targeted ones
-- the workload originally shipped with). The shape mirrors
-- @nonempty-containers/test/Tests/Util.hs@: keys span @[-100, 100]@,
-- values are characters in @['a'..'z']@, and the size range is
-- 1..8 (a bit wider than upstream's 1..8 so that shrinkers have more
-- material to reduce). All generators preserve the "distinct keys"
-- invariant required by the underlying NEMap-based properties.
module Etna.Gens.QuickCheck where

import qualified Data.List.NonEmpty as NE
import           Data.List.NonEmpty (NonEmpty (..))
import qualified Test.QuickCheck    as QC

import Etna.Properties

------------------------------------------------------------------------------
-- Generic building blocks.

genKey :: QC.Gen Int
genKey = QC.choose (-100, 100)

genVal :: QC.Gen Char
genVal = QC.elements ['a' .. 'z']

-- | Non-empty list of distinct keys with size in [minSize..15]. Loops
-- with rejection until we accumulate the requested number of unique
-- keys (the key space is wide enough that this terminates quickly).
genDistinctKeyList :: Int -> QC.Gen [Int]
genDistinctKeyList minSize = do
  n <- QC.choose (minSize, 8)
  go n []
  where
    go 0 acc = pure acc
    go k acc = do
      x <- genKey
      if x `elem` acc then go k acc else go (k - 1) (x : acc)

genNeKeyValList :: Int -> QC.Gen (NonEmpty (Int, Char))
genNeKeyValList minSize = do
  ks <- genDistinctKeyList minSize
  vs <- QC.vectorOf (length ks) genVal
  case zip ks vs of
    []       -> error "genNeKeyValList: empty"
    (x : xs) -> pure (x :| xs)

genNeIntList :: Int -> QC.Gen (NonEmpty Int)
genNeIntList minSize = do
  ks <- genDistinctKeyList minSize
  case ks of
    []       -> error "genNeIntList: empty"
    (x : xs) -> pure (x :| xs)

------------------------------------------------------------------------------

gen_delete_max_ne_map_keys_shrink :: QC.Gen NeMapPairs
gen_delete_max_ne_map_keys_shrink = NeMapPairs <$> genNeKeyValList 1

gen_delete_max_ne_int_map_keys_shrink :: QC.Gen NeIntMapPairs
gen_delete_max_ne_int_map_keys_shrink = NeIntMapPairs <$> genNeKeyValList 1

gen_delete_max_ne_set_shrink :: QC.Gen NeSetElems
gen_delete_max_ne_set_shrink = NeSetElems <$> genNeIntList 1

gen_delete_max_ne_int_set_shrink :: QC.Gen NeIntSetElems
gen_delete_max_ne_int_set_shrink = NeIntSetElems <$> genNeIntList 1

gen_intersperse_length_invariant :: QC.Gen NeSeqElems
gen_intersperse_length_invariant = do
  -- Wide list of small ints; duplicates allowed (NESeq permits them).
  n   <- QC.choose (1, 8)
  xs  <- QC.vectorOf n (QC.choose (-100, 100))
  sep <- QC.choose (-100, 100)
  case xs of
    []     -> error "gen_intersperse: empty"
    (x:rs) -> pure (NeSeqElems (x :| rs) sep)

gen_split_left_partition_at_upper_bound :: QC.Gen SplitArgs
gen_split_left_partition_at_upper_bound =
  -- Property needs ≥ 2 distinct keys to split.
  SplitArgs <$> genNeKeyValList 2

gen_is_submap_of_reflexive_and_key_exists :: QC.Gen SubmapArgs
gen_is_submap_of_reflexive_and_key_exists = do
  a <- genNeKeyValList 1
  b <- genNeKeyValList 1
  pure (SubmapArgs a b)

gen_update_lookup_returns_original :: QC.Gen UpdLookupArgs
gen_update_lookup_returns_original = do
  pairs <- genNeKeyValList 1
  mode  <- QC.elements [0, 1]
  pure (UpdLookupArgs pairs mode)

------------------------------------------------------------------------------
-- Shrink functions. The runner passes these alongside the generators
-- via @forAllShrink@; without them QuickCheck has nothing to walk on
-- (the args types have no @Arbitrary@ instance).

-- | Shrink a 'NonEmpty' by either reducing the head, reducing the tail
-- as a list, or dropping the head (if the tail is non-empty so the
-- result is still 'NonEmpty').
shrinkNeList :: (a -> [a]) -> NonEmpty a -> [NonEmpty a]
shrinkNeList sh (x :| xs) =
  [x' :| xs   | x'  <- sh x] ++
  [x  :| xs'  | xs' <- QC.shrinkList sh xs] ++
  case xs of
    []      -> []
    (y:ys)  -> [y :| ys]

shrinkPair :: (Int, Char) -> [(Int, Char)]
shrinkPair (k, v) =
  [(k', v) | k' <- QC.shrink k] ++ [(k, v') | v' <- QC.shrink v]

shrinkInt :: Int -> [Int]
shrinkInt = QC.shrink

------------------------------------------------------------------------------

shrink_delete_max_ne_map_keys_shrink :: NeMapPairs -> [NeMapPairs]
shrink_delete_max_ne_map_keys_shrink (NeMapPairs ne) =
  NeMapPairs <$> shrinkNeList shrinkPair ne

shrink_delete_max_ne_int_map_keys_shrink :: NeIntMapPairs -> [NeIntMapPairs]
shrink_delete_max_ne_int_map_keys_shrink (NeIntMapPairs ne) =
  NeIntMapPairs <$> shrinkNeList shrinkPair ne

shrink_delete_max_ne_set_shrink :: NeSetElems -> [NeSetElems]
shrink_delete_max_ne_set_shrink (NeSetElems ne) =
  NeSetElems <$> shrinkNeList shrinkInt ne

shrink_delete_max_ne_int_set_shrink :: NeIntSetElems -> [NeIntSetElems]
shrink_delete_max_ne_int_set_shrink (NeIntSetElems ne) =
  NeIntSetElems <$> shrinkNeList shrinkInt ne

shrink_intersperse_length_invariant :: NeSeqElems -> [NeSeqElems]
shrink_intersperse_length_invariant (NeSeqElems ne sep) =
  [ NeSeqElems ne' sep  | ne'  <- shrinkNeList shrinkInt ne ] ++
  [ NeSeqElems ne sep'  | sep' <- shrinkInt sep ]

shrink_split_left_partition_at_upper_bound :: SplitArgs -> [SplitArgs]
shrink_split_left_partition_at_upper_bound (SplitArgs ne) =
  -- Property requires >= 2 distinct keys; refuse to shrink to a
  -- singleton (would make the property vacuously discard).
  [ SplitArgs ne' | ne' <- shrinkNeList shrinkPair ne, NE.length ne' >= 2 ]

shrink_is_submap_of_reflexive_and_key_exists :: SubmapArgs -> [SubmapArgs]
shrink_is_submap_of_reflexive_and_key_exists (SubmapArgs a b) =
  [ SubmapArgs a' b  | a' <- shrinkNeList shrinkPair a ] ++
  [ SubmapArgs a b'  | b' <- shrinkNeList shrinkPair b ]

shrink_update_lookup_returns_original :: UpdLookupArgs -> [UpdLookupArgs]
shrink_update_lookup_returns_original (UpdLookupArgs pairs mode) =
  [ UpdLookupArgs pairs' mode  | pairs' <- shrinkNeList shrinkPair pairs ]
  -- Don't shrink mode -- it's a discrete 0/1 toggle.
