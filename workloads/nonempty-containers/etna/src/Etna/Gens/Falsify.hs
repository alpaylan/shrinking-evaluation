module Etna.Gens.Falsify where

import           Data.List.NonEmpty (NonEmpty (..))
import qualified Test.Falsify.Generator as F
import qualified Test.Falsify.Range     as FR

import Etna.Properties

------------------------------------------------------------------------------
-- Upstream-style PBT generators (Falsify flavour). Mirrors the
-- QuickCheck and Hedgehog modules: keys span [-100, 100], values are
-- chars in 'a'..'z', and lists are sized 1..8. Distinct-key invariants
-- are preserved by drawing from a wide pool and rejecting collisions in
-- a bounded loop.

ne :: [a] -> NonEmpty a
ne []     = error "Etna.Gens.Falsify.ne: empty list"
ne (x:xs) = x :| xs

-- | One key, drawn uniformly from [-100, 100].
genKeyFS :: F.Gen Int
genKeyFS = F.inRange (FR.withOrigin (-100 :: Int, 100) 0)

genValFS :: F.Gen Char
genValFS = F.elem (ne ['a' .. 'z'])

-- | A non-empty list of distinct keys, sized minSize..15. We draw the
-- size first (so the distribution actually spans the full 1..8 range,
-- rather than always saturating at 15), then accumulate that many
-- distinct keys via rejection. The wide [-100, 100] key space makes
-- collisions rare so this terminates quickly.
genDistinctKeyListFS :: Int -> F.Gen [Int]
genDistinctKeyListFS minSize = do
  nW <- F.inRange (FR.between (fromIntegral minSize :: Word, 8))
  let n = fromIntegral nW :: Int
  go n []
  where
    go 0 acc = pure acc
    go k acc = do
      x <- genKeyFS
      if x `elem` acc then go k acc else go (k - 1) (x : acc)

genNeKeyValListFS :: Int -> F.Gen (NonEmpty (Int, Char))
genNeKeyValListFS minSize = do
  ks <- genDistinctKeyListFS minSize
  vs <- mapM (const genValFS) ks
  case zip ks vs of
    []       -> error "genNeKeyValListFS: empty"
    (p : ps) -> pure (p :| ps)

genNeIntListFS :: Int -> F.Gen (NonEmpty Int)
genNeIntListFS minSize = do
  ks <- genDistinctKeyListFS minSize
  case ks of
    []       -> error "genNeIntListFS: empty"
    (k : ks') -> pure (k :| ks')

------------------------------------------------------------------------------

gen_delete_max_ne_map_keys_shrink :: F.Gen NeMapPairs
gen_delete_max_ne_map_keys_shrink = NeMapPairs <$> genNeKeyValListFS 1

gen_delete_max_ne_int_map_keys_shrink :: F.Gen NeIntMapPairs
gen_delete_max_ne_int_map_keys_shrink = NeIntMapPairs <$> genNeKeyValListFS 1

gen_delete_max_ne_set_shrink :: F.Gen NeSetElems
gen_delete_max_ne_set_shrink = NeSetElems <$> genNeIntListFS 1

gen_delete_max_ne_int_set_shrink :: F.Gen NeIntSetElems
gen_delete_max_ne_int_set_shrink = NeIntSetElems <$> genNeIntListFS 1

gen_intersperse_length_invariant :: F.Gen NeSeqElems
gen_intersperse_length_invariant = do
  n <- fromIntegral <$> F.inRange (FR.between (1 :: Word, 8))
  xs  <- mapM (const genKeyFS) [1 .. (n :: Int)]
  sep <- genKeyFS
  case xs of
    []     -> error "gen_intersperse: empty"
    (x:rs) -> pure (NeSeqElems (x :| rs) sep)

gen_split_left_partition_at_upper_bound :: F.Gen SplitArgs
gen_split_left_partition_at_upper_bound =
  SplitArgs <$> genNeKeyValListFS 2

gen_is_submap_of_reflexive_and_key_exists :: F.Gen SubmapArgs
gen_is_submap_of_reflexive_and_key_exists = do
  a <- genNeKeyValListFS 1
  b <- genNeKeyValListFS 1
  pure (SubmapArgs a b)

gen_update_lookup_returns_original :: F.Gen UpdLookupArgs
gen_update_lookup_returns_original = do
  pairs <- genNeKeyValListFS 1
  bit   <- F.inRange (FR.between (0 :: Word, 1))
  let mode = fromIntegral bit
  pure (UpdLookupArgs pairs mode)
