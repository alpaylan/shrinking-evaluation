{-# LANGUAGE FlexibleInstances #-}
{-# LANGUAGE MultiParamTypeClasses #-}
{-# LANGUAGE RecordWildCards #-}
{-# LANGUAGE ScopedTypeVariables #-}
{-# LANGUAGE UndecidableInstances #-}

module Etna.Lib.Strategy.QuickCheck
  ( qcDefaults,
    qcMakeProp,
    qcMakeResult,
    qcRunArb,
    qcRunArb',
    backtrack,
  )
where

import Control.Monad (when)
import Data.IORef (modifyIORef', newIORef, readIORef, writeIORef)
import Data.List (intercalate)
import Etna.Lib.Types
import Etna.Lib.Util (ShrinkMode (..), maxCap, nowSec, shrinkModeFromEnv)
import System.IO.Silently (capture)
import Test.QuickCheck hiding (Result)
import qualified Test.QuickCheck as QC
import qualified Test.QuickCheck.Property as QCP

-- To use QuickCheck, can just implement an Arbitrary instance
-- and call (qcRunArb qcDefaults [approach]), where approach
-- should be Naive if your generator does not necessarily generate 
-- inputs that satisfy the precondition, and Correct otherwise.

qcDefaults :: Args
qcDefaults =
  -- By default, use timeout instead of max tests. ETNA_SHRINKS picks
  -- the shrink-budget mode (default/none/<N>); ShrinkDefault leaves
  -- maxShrinks at QC's stdArgs value of maxBound (effectively unlimited).
  let base = stdArgs {maxSuccess = maxCap}
   in case shrinkModeFromEnv of
        ShrinkDefault   -> base
        ShrinkNone      -> base {maxShrinks = 0}
        ShrinkFixed n   -> base {maxShrinks = n}

qcMakeProp :: Approach -> Task a -> (a -> Property)
qcMakeProp Naive task =
  -- Filter based on precondition.
  uncurry (==>) . task
qcMakeProp Correct task =
  -- Only evaluate postcondition.
  QC.property . snd . task

qcMakeResult :: IO QC.Result -> IO Result
qcMakeResult ioresult = do
  (_, result) <- capture ioresult
  let (status, foundbug, counterexample) =
        case result of
          Failure {failingTestCase = [ex]} -> ("Failed", True, ex)
          NoExpectedFailure {} -> ("No Expected Failure", True, "")
          r -> ("Finished", False, "")
      discards = Just $ numDiscarded result
      tests = numTests result - (if foundbug then 1 else 0)
      pre_counterexample = ""
      exec_time_pre = 0
      exec_time_shrink = 0
      time_pre_failure = 0
      time_shrinking = 0
      shrinking_passed = 0
      shrinking_failed = 0
      shrinking_discarded = 0
  return Result {..}

qcRunArb :: (Show a, Arbitrary a) => Args -> Approach -> Strategy a
qcRunArb args app = qcRunArb' args . qcMakeProp app

qcRunArb' :: (Show a, Arbitrary a) => Args -> (a -> Property) -> IO Result
qcRunArb' args propFn = do
  preRef         <- newIORef ""
  testStartRef   <- newIORef 0
  trialStart     <- nowSec
  failureMarkRef <- newIORef Nothing
  execPreRef     <- newIORef 0
  execShrinkRef  <- newIORef 0
  shrinkPassedRef    <- newIORef 0
  shrinkFailedRef    <- newIORef 0
  shrinkDiscardedRef <- newIORef 0
  -- PostTest fires after each property evaluation (including each
  -- shrink attempt). We compute exec time from the per-test start
  -- snapshot recorded by idempotentIOProperty below, and route to the
  -- pre-failure or shrinking accumulator based on whether we've yet
  -- observed a failing case.
  let mkCb a = QCP.PostTest QCP.NotCounterexample $ \_ res -> do
        tEnd  <- nowSec
        tStart <- readIORef testStartRef
        mFail  <- readIORef failureMarkRef
        let dur = tEnd - tStart
        case mFail of
          Nothing -> modifyIORef' execPreRef    (+ dur)
          Just _  -> do
            modifyIORef' execShrinkRef (+ dur)
            case QCP.ok res of
              Just True  -> modifyIORef' shrinkPassedRef    (+ 1)
              Just False -> modifyIORef' shrinkFailedRef    (+ 1)
              Nothing    -> modifyIORef' shrinkDiscardedRef (+ 1)
        case QCP.ok res of
          Just False -> do
            cur <- readIORef preRef
            when (null cur) (writeIORef preRef (show a))
            mf <- readIORef failureMarkRef
            case mf of
              Nothing -> writeIORef failureMarkRef (Just tEnd)
              Just _  -> pure ()
          _ -> return ()
      -- idempotentIOProperty runs the IO once before the property is
      -- evaluated, giving us a per-test entry hook.
      propFn' a = QCP.callback (mkCb a) $
                  QCP.idempotentIOProperty $ do
                    t <- nowSec
                    writeIORef testStartRef t
                    pure (propFn a)
  base     <- qcMakeResult (quickCheckWithResult args propFn')
  trialEnd <- nowSec
  pre      <- readIORef preRef
  ePre     <- readIORef execPreRef
  eShr     <- readIORef execShrinkRef
  sPass    <- readIORef shrinkPassedRef
  sFail    <- readIORef shrinkFailedRef
  sDisc    <- readIORef shrinkDiscardedRef
  mFail    <- readIORef failureMarkRef
  let (tPre, tShr) = case mFail of
        Just f  -> (f - trialStart, trialEnd - f)
        Nothing -> (trialEnd - trialStart, 0)
  return base
    { pre_counterexample = pre
    , exec_time_pre = ePre
    , exec_time_shrink = eShr
    , time_pre_failure = tPre
    , time_shrinking = tShr
    , shrinking_passed = sPass
    , shrinking_failed = sFail
    , shrinking_discarded = sDisc
    }

---------

type Freq a = [(Int, Gen (Maybe a))]

-- Based on QuickChick
backtrack :: Freq a -> Gen (Maybe a)
backtrack gs = go (sum $ map fst gs) gs
  where
    go _ [] = return Nothing
    go tot gs = do
      n <- chooseInt (1, tot)
      let (k, g, gs') = pickDrop n gs
      ma <- g
      case ma of
        Just _ -> return ma
        Nothing -> go (tot - k) gs'

    pickDrop :: Int -> Freq a -> (Int, Gen (Maybe a), Freq a)
    pickDrop _ [] = (0, return Nothing, [])
    pickDrop n ((k, g) : gs)
      | n <= k = (k, g, gs)
      | otherwise =
          let (k', g', gs') = pickDrop (n - k) gs
           in (k', g', (k, g) : gs')