{-# LANGUAGE RecordWildCards #-}

module Etna.Lib.Strategy.Hedgehog
  ( hhDefaults,
    hhRunGen,
  )
where

import Control.Monad (when)
import Data.IORef (IORef, modifyIORef', newIORef, readIORef, writeIORef)
import Etna.Lib.Types
import Etna.Lib.Util (ShrinkMode (..), maxCap, nowSec, shrinkModeFromEnv)
import qualified Hedgehog as HH

hhDefaults :: Int
hhDefaults = maxCap

hhRunGen :: (Show a) => Int -> Approach -> HH.Gen a -> Strategy a
hhRunGen cap app gen task = do
  testsRef          <- newIORef 0
  discardsRef       <- newIORef 0
  counterexampleRef <- newIORef ""
  preRef            <- newIORef ""
  -- Phase timing accumulators.
  failureMarkRef <- newIORef (Nothing :: Maybe Double)
  execPreRef     <- newIORef 0
  execShrinkRef  <- newIORef 0
  shrinkPassedRef    <- newIORef 0
  shrinkFailedRef    <- newIORef 0
  shrinkDiscardedRef <- newIORef 0

  -- Combined accumulator: time the postcondition force, route to the
  -- right phase bucket, and record the first observed failure
  -- timestamp + counterexample atomically so phase boundaries stay
  -- consistent.
  let timePost a post = HH.evalIO $ do
        t0 <- nowSec
        post `seq` pure ()
        t1 <- nowSec
        mf <- readIORef failureMarkRef
        modifyIORef' (case mf of Nothing -> execPreRef; Just _ -> execShrinkRef) (+ (t1 - t0))
        case mf of
          Just _  ->
            modifyIORef' (if post then shrinkPassedRef else shrinkFailedRef) (+ 1)
          Nothing -> pure ()
        when (not post) $ do
          mf2 <- readIORef failureMarkRef
          case mf2 of
            Nothing -> writeIORef failureMarkRef (Just t1)
            Just _  -> pure ()
          p <- readIORef preRef
          when (null p) $ writeIORef preRef (show a)

      applyShrinkMode = case shrinkModeFromEnv of
        ShrinkDefault   -> id
        ShrinkNone      -> HH.withShrinks 0
        ShrinkFixed n   -> HH.withShrinks (fromIntegral n)
      prop =
        HH.withTests (fromIntegral cap) $
          applyShrinkMode $
            HH.withDiscards (fromIntegral cap) $
              HH.property $ do
                a <- HH.forAll gen
                HH.evalIO $ writeIORef counterexampleRef (show a)
                let (pre, post) = task a
                case app of
                  Naive ->
                    if pre
                      then do
                        HH.evalIO $ modifyIORef' testsRef (+ 1)
                        timePost a post
                        HH.assert post
                      else do
                        HH.evalIO $ do
                          modifyIORef' discardsRef (+ 1)
                          mf <- readIORef failureMarkRef
                          case mf of
                            Just _  -> modifyIORef' shrinkDiscardedRef (+ 1)
                            Nothing -> pure ()
                        HH.discard
                  Correct -> do
                    HH.evalIO $ modifyIORef' testsRef (+ 1)
                    timePost a post
                    HH.assert post

  trialStart <- nowSec
  ok <- HH.check prop
  trialEnd <- nowSec
  tests <- readIORef testsRef
  discards <- Just <$> readIORef discardsRef
  counterexample <- readIORef counterexampleRef
  pre_counterexample <- readIORef preRef
  exec_time_pre    <- readIORef execPreRef
  exec_time_shrink <- readIORef execShrinkRef
  shrinking_passed    <- readIORef shrinkPassedRef
  shrinking_failed    <- readIORef shrinkFailedRef
  shrinking_discarded <- readIORef shrinkDiscardedRef
  mFail <- readIORef failureMarkRef
  let (time_pre_failure, time_shrinking) = case mFail of
        Just f  -> (f - trialStart, trialEnd - f)
        Nothing -> (trialEnd - trialStart, 0)
  let status = if ok then "Finished" else "Failed"
  if ok
    then return Result {counterexample = "", pre_counterexample = "", ..}
    else return Result {..}
