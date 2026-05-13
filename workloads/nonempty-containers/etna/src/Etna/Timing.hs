{-# LANGUAGE BangPatterns #-}
{-# OPTIONS_GHC -fno-full-laziness #-}
{-# OPTIONS_GHC -fno-cse #-}

-- | Phase-timing helpers shared by the framework drivers.
--
-- Mirrors the helper set in
-- @shrinking-evaluation/workloads/<wl>-haskell/etna-lib/src/Etna/Lib/Util.hs@
-- and the @Falsify@ / @Hedgehog@ / @QuickCheck@ strategy modules of the
-- BST/RBT/STLC workloads.
module Etna.Timing
  ( nowSec
  , ShrinkMode (..)
  , shrinkModeFromEnv
  , shrinkModeName
  , shrinkModeNumber
  , markStart
  , accumExec
  , markFailure
  , bumpShrink
  ) where

import           Control.Monad     (when)
import           Data.IORef        (IORef, modifyIORef', newIORef, readIORef, writeIORef)
import           System.Clock      (Clock (Monotonic), getTime, toNanoSecs)
import           System.Environment (lookupEnv)
import           System.IO.Unsafe  (unsafePerformIO)

-- | Monotonic wall-clock as fractional seconds.
nowSec :: IO Double
nowSec = do
  t <- getTime Monotonic
  pure $! fromIntegral (toNanoSecs t) * 1e-9

-- | ETNA_SHRINKS shrink-budget mode. See bst-haskell's etna-lib/Util.hs
-- for the full doc; in short:
--   unset / "" / "default" -> ShrinkDefault (no override; framework default)
--   "none"                 -> ShrinkNone    (cap at 0)
--   numeric N              -> ShrinkFixed N (cap at N; semantics differ by framework)
data ShrinkMode = ShrinkDefault | ShrinkNone | ShrinkFixed Int
  deriving (Show, Eq)

shrinkModeFromEnv :: ShrinkMode
shrinkModeFromEnv =
  case unsafePerformIO (lookupEnv "ETNA_SHRINKS") of
    Nothing                  -> ShrinkDefault
    Just s | null s          -> ShrinkDefault
           | s == "default"  -> ShrinkDefault
           | s == "none"     -> ShrinkNone
           | otherwise       -> ShrinkFixed (read s)
{-# NOINLINE shrinkModeFromEnv #-}

shrinkModeName :: ShrinkMode -> String
shrinkModeName ShrinkDefault   = "default"
shrinkModeName ShrinkNone      = "none"
shrinkModeName (ShrinkFixed _) = "fixed"

shrinkModeNumber :: ShrinkMode -> Int
shrinkModeNumber ShrinkDefault   = 0
shrinkModeNumber ShrinkNone      = 0
shrinkModeNumber (ShrinkFixed n) = n

-- | Stamp the current time into a reusable @IORef Double@. Combined
-- with 'accumExec' below, this brackets per-test execution time within
-- a Falsify-style pure property monad.
markStart :: IORef Double -> ()
markStart ref = unsafePerformIO $ do
  t <- nowSec
  writeIORef ref t
{-# NOINLINE markStart #-}

-- | Compute @now - lastStart@ and add it to either the pre-failure or
-- shrinking accumulator, depending on whether we've already observed
-- the first failure.
accumExec
  :: IORef Double
  -> IORef (Maybe Double)
  -> IORef Double
  -> IORef Double
  -> ()
accumExec startRef failRef preAccum shrinkAccum = unsafePerformIO $ do
  s  <- readIORef startRef
  e  <- nowSec
  mf <- readIORef failRef
  modifyIORef' (case mf of Nothing -> preAccum; Just _ -> shrinkAccum) (+ (e - s))
{-# NOINLINE accumExec #-}

-- | Record the timestamp of the first observed failure. Subsequent
-- calls are no-ops, so the boundary stays stable across the shrink loop.
markFailure :: IORef (Maybe Double) -> ()
markFailure ref = unsafePerformIO $ do
  mf <- readIORef ref
  when (mf == Nothing) $ do
    t <- nowSec
    writeIORef ref (Just t)
{-# NOINLINE markFailure #-}

-- | Bump @counter@ iff the failure mark is already set, i.e. we are in
-- the shrinking phase. Used by the Falsify driver where the property
-- monad is pure-ish; the caller seq's this before @markFailure@ at the
-- first failure site so the unshrunk failure stays in the pre bucket.
bumpShrink :: IORef (Maybe Double) -> IORef Int -> ()
bumpShrink failRef counter = unsafePerformIO $ do
  mf <- readIORef failRef
  case mf of
    Just _  -> modifyIORef' counter (+ 1)
    Nothing -> pure ()
{-# NOINLINE bumpShrink #-}
