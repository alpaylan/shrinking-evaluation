{-# LANGUAGE BangPatterns #-}
{-# LANGUAGE RecordWildCards #-}
{-# OPTIONS_GHC -fno-full-laziness #-}
{-# OPTIONS_GHC -fno-cse #-}

module Etna.Lib.Strategy.Falsify
  ( fsDefaults,
    fsRunGen,
  )
where

import Control.Monad (unless, when)
import Data.IORef (IORef, modifyIORef', newIORef, readIORef, writeIORef)
import Data.List (isPrefixOf)
import Etna.Lib.Types
import Etna.Lib.Util (ShrinkMode (..), maxCap, nowSec, shrinkModeFromEnv)
import System.IO.Unsafe (unsafePerformIO)
import Test.Falsify.Generator (Gen)
import Test.Falsify.Property
import Test.Tasty.Falsify
import Test.Tasty.Runners hiding (Result)
import qualified Test.Tasty.Providers as TP

fsDefaults :: Int
fsDefaults = maxCap

updateCounter :: IORef Int -> ()
updateCounter ref = unsafePerformIO (modifyIORef' ref (+ 1))
{-# NOINLINE updateCounter #-}

record :: (Show a) => IORef String -> a -> ()
record ref a = unsafePerformIO (writeIORef ref (show a))
{-# NOINLINE record #-}

-- Like @record@ but only writes if the IORef is still empty, so the
-- first observed input wins (the unshrunk failure).
recordOnce :: (Show a) => IORef String -> a -> ()
recordOnce ref a = unsafePerformIO $ do
  cur <- readIORef ref
  when (null cur) (writeIORef ref (show a))
{-# NOINLINE recordOnce #-}

-- Extract Falsify's final shrunk counterexample from a tasty failure
-- description. Falsify's NotVerbose renderer (Test.Falsify.Internal.Driver)
-- formats failures as:
--   line 1: "failed after <n successful tests, ...>"
--   line 2: <Show-rendered final counterexample>
--   line 3: "Logs for failed test run:"
--   ...
-- The IORef-based "last evaluated input" approach captures shrink
-- candidates the runner explored but did not accept (especially visible
-- at maxShrinks=0, where ~80% of FalsifyGbE trials show pre /= post).
-- Parsing line 2 of the renderer's output gives Falsify's actual final.
extractFalsifyFinalCex :: String -> Maybe String
extractFalsifyFinalCex desc =
  case dropWhile (not . ("failed after " `isPrefixOf`)) (lines desc) of
    (_failedAfter : cex : _) -> Just cex
    _                        -> Nothing

-- Phase-timing helpers. They thread through Falsify's pure Property
-- monad via the established `unsafePerformIO + NOINLINE + seq` pattern
-- (see `record` above). The fno-cse / fno-full-laziness pragmas at the
-- top of this file preserve evaluation order.
markStart :: IORef Double -> ()
markStart ref = unsafePerformIO $ do
  t <- nowSec
  writeIORef ref t
{-# NOINLINE markStart #-}

accumExec :: IORef Double -> IORef (Maybe Double) -> IORef Double -> IORef Double -> ()
accumExec startRef failRef preAccum shrinkAccum = unsafePerformIO $ do
  s  <- readIORef startRef
  e  <- nowSec
  mf <- readIORef failRef
  modifyIORef' (case mf of Nothing -> preAccum; Just _ -> shrinkAccum) (+ (e - s))
{-# NOINLINE accumExec #-}

markFailure :: IORef (Maybe Double) -> ()
markFailure ref = unsafePerformIO $ do
  mf <- readIORef ref
  case mf of
    Nothing -> do
      t <- nowSec
      writeIORef ref (Just t)
    Just _  -> pure ()
{-# NOINLINE markFailure #-}

-- Bump @counter@ iff the failure mark is already set, i.e. we are in
-- the shrinking phase. Must be evaluated before @markFailure@ at the
-- first failure site so the unshrunk failure stays in the pre bucket.
bumpShrink :: IORef (Maybe Double) -> IORef Int -> ()
bumpShrink failRef counter = unsafePerformIO $ do
  mf <- readIORef failRef
  case mf of
    Just _  -> modifyIORef' counter (+ 1)
    Nothing -> pure ()
{-# NOINLINE bumpShrink #-}

fsRunGen :: (Show a) => Int -> Approach -> Gen a -> Strategy a
fsRunGen cap app g task = do
  testsRef <- newIORef 0
  discardsRef <- newIORef 0
  counterexampleRef <- newIORef ""
  preRef <- newIORef ""
  -- Phase timing accumulators.
  testStartRef   <- newIORef 0
  failureMarkRef <- newIORef (Nothing :: Maybe Double)
  execPreRef     <- newIORef 0
  execShrinkRef  <- newIORef 0
  shrinkPassedRef    <- newIORef 0
  shrinkFailedRef    <- newIORef 0
  shrinkDiscardedRef <- newIORef 0

  let shouldDiscard pre =
        case app of
          Naive -> not pre
          Correct -> False

      prop = do
        a <- gen g
        let (pre, post) = task a
        if shouldDiscard pre
          then do
            bumpShrink failureMarkRef shrinkDiscardedRef `seq`
              updateCounter discardsRef `seq` discard
          else do
            updateCounter testsRef `seq` pure ()
            -- Time the postcondition force, then route to phase bucket.
            markStart testStartRef `seq` pure ()
            post `seq` pure ()
            accumExec testStartRef failureMarkRef execPreRef execShrinkRef `seq` pure ()
            if post
              then bumpShrink failureMarkRef shrinkPassedRef `seq` pure ()
              else do
                recordOnce preRef a `seq` pure ()
                bumpShrink failureMarkRef shrinkFailedRef `seq`
                  markFailure failureMarkRef `seq` testFailed (show a)

      shrinkMode = shrinkModeFromEnv
      testOptions = TestOptions
          { expectFailure = DontExpectFailure,
            overrideVerbose = Nothing,
            -- ShrinkDefault leaves overrideMaxShrinks=Nothing so Falsify's
            -- own default (no cap) applies. ShrinkNone/ShrinkFixed override.
            overrideMaxShrinks = case shrinkMode of
              ShrinkDefault -> Nothing
              ShrinkNone    -> Just 0
              ShrinkFixed n -> Just (fromIntegral n),
            overrideNumTests = Just (fromIntegral cap),
            overrideMaxRatio = Just (fromIntegral cap)
          }
      go (SingleTest _ t) = TP.run mempty t (\_ -> pure ())

  trialStart <- nowSec
  tastyResult <- go $ testPropertyWith testOptions "falsify" prop
  -- Force the test output so the lazy ShrinkExplanation inside
  -- `failureRun` actually evaluates. Tasty's IsTest instance for
  -- Falsify already calls renderTestResult internally (see
  -- Test.Falsify.Internal.Driver.Tasty), which forces the tree —
  -- so this `length` is mostly redundant via that path, and a true
  -- zero in ShrinkNone is not achievable through the Tasty
  -- integration: forcing the first node of the explanation tree
  -- requires running the property on candidates. ShrinkNone still
  -- caps at maxShrinks=0 so the chain truncates to ShrinkingStopped,
  -- but the FIRST forcing pass leaks ~few property evaluations.
  let !_forceShrink = case shrinkMode of
        ShrinkNone -> 0
        _          -> length (resultDescription tastyResult)
  trialEnd <- nowSec

  let ok = resultSuccessful tastyResult
      status = if ok then "Finished" else "Failed"

  tests <- readIORef testsRef
  discardsCount <- readIORef discardsRef
  counterexample <-
    if ok then pure ""
    else case extractFalsifyFinalCex (resultDescription tastyResult) of
      Just cex -> pure cex
      Nothing  -> readIORef counterexampleRef
  pre_counterexample <- if ok then (pure "") else (readIORef preRef)
  exec_time_pre    <- readIORef execPreRef
  exec_time_shrink <- readIORef execShrinkRef
  shrinking_passed    <- readIORef shrinkPassedRef
  shrinking_failed    <- readIORef shrinkFailedRef
  shrinking_discarded <- readIORef shrinkDiscardedRef
  mFail <- readIORef failureMarkRef
  let (time_pre_failure, time_shrinking) = case mFail of
        Just f  -> (f - trialStart, trialEnd - f)
        Nothing -> (trialEnd - trialStart, 0)

  return Result { discards = Just discardsCount, ..}
