{-# LANGUAGE BangPatterns #-}
{-# LANGUAGE FlexibleContexts #-}
{-# LANGUAGE FlexibleInstances #-}
{-# LANGUAGE LambdaCase #-}
{-# LANGUAGE MultiParamTypeClasses #-}
{-# LANGUAGE RecordWildCards #-}
{-# OPTIONS_GHC -fno-full-laziness #-}
{-# OPTIONS_GHC -fno-cse #-}

module Etna.Lib.Strategy.SmallCheck (scDefaults, scRun) where

import Data.IORef
import Data.Maybe (isJust)
import Etna.Lib.Types
import Etna.Lib.Util (maxCap, nowSec)
import System.IO.Unsafe (unsafePerformIO)
import Test.SmallCheck
import Test.SmallCheck.Drivers
import Test.SmallCheck.Series

type Args = (Depth, Cap)

scDefaults :: Args
scDefaults = (maxCap, maxCap)

makeProp :: Approach -> Task a -> (a -> Property IO)
makeProp Naive task =
  -- Filter based on precondition.
  test . uncurry (==>) . task
makeProp Correct task =
  -- Only evaluate postcondition.
  test . snd . task

scRun :: (Show a, Serial IO a) => Approach -> Args -> Strategy a
scRun app (depth, cap) task = do
  good <- newIORef 0
  bad <- newIORef 0
  execAccum <- newIORef 0
  trialStart <- nowSec
  final <- smallCheckWithHook depth (update good bad) (prop execAccum)
  trialEnd <- nowSec

  let (status, foundbug, counterexample) = case final of
        Nothing -> ("Finished", False, "")
        Just (CounterExample (ex : _) _) -> ("Failed", True, ex)
        Just _ -> ("Failed", True, "")
      pre_counterexample = counterexample
  tests <- (\i -> i - if foundbug then 1 else 0) <$> readIORef good
  discards <- Just <$> readIORef bad
  exec_time_pre <- readIORef execAccum
  -- Enumerator: no shrinking phase.
  let exec_time_shrink = 0
      time_pre_failure = trialEnd - trialStart
      time_shrinking   = 0
      shrinking_passed = 0
      shrinking_failed = 0
      shrinking_discarded = 0
  return Result {..}
  where
    prop ref = over (limit cap series) (timedSCProp ref (makeProp app task))

    update good bad = \case
      GoodTest -> modifyIORef good (+ 1)
      BadTest -> modifyIORef bad (+ 1)

-- Time each property invocation. SmallCheck's `Property IO` is
-- effectful, so we route through a wrapper that evaluates the inner
-- predicate in IO with bracketed timestamps.
timedSCProp :: IORef Double -> (a -> Property IO) -> a -> Property IO
timedSCProp ref f a = unsafePerformIO $ do
  t0 <- nowSec
  let !p = f a
  t1 <- nowSec
  modifyIORef' ref (+ (t1 - t0))
  pure p
{-# NOINLINE timedSCProp #-}