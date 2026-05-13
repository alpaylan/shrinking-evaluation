{-# LANGUAGE BangPatterns #-}
{-# LANGUAGE RecordWildCards #-}
{-# OPTIONS_GHC -fno-full-laziness #-}
{-# OPTIONS_GHC -fno-cse #-}

module Etna.Lib.Strategy.LeanCheck (lcRun) where

import Data.IORef (modifyIORef', newIORef, readIORef)
import Data.Maybe (isJust)
import Etna.Lib.Types
import Etna.Lib.Util
  ( leanCheckpointEvery,
    leanCheckpointFromEnv,
    leanResumeFromEnv,
    nowSec,
  )
import System.Directory (renameFile)
import Test.LeanCheck (Listable, list, (==>))

makeProp :: Approach -> Task a -> (a -> Bool)
makeProp Naive task   = uncurry (==>) . task
makeProp Correct task = snd . task

-- Atomic write-then-rename. Avoids a partial-file race if the runner
-- is killed mid-write.
writeCheckpoint :: FilePath -> Int -> IO ()
writeCheckpoint path n = do
  let tmp = path ++ ".tmp"
  writeFile tmp (show n)
  renameFile tmp path

-- Stream-iterate `list :: [a]` checking each, stopping at the first
-- failure (`prop x == False`) or when `cap` tests have been performed.
-- ETNA_LEAN_RESUME=<N> skips the first N values; ETNA_LEAN_CHECKPOINT
-- (file path) persists the running absolute index every
-- `leanCheckpointEvery` iterations. Both env vars are no-ops when
-- unset, so behaviour is identical to before for un-instrumented runs.
lcRun :: (Show a, Listable a) => Approach -> Int -> Strategy a
lcRun app cap task = do
  execAccum <- newIORef (0 :: Double)
  resume <- leanResumeFromEnv
  mCkpt <- leanCheckpointFromEnv
  let prop = makeProp app task
      go !n []     = pure (n, Nothing)
      go !n (x:xs)
        | n >= cap  = pure (n, Nothing)
        | otherwise = do
            case mCkpt of
              Just p | n > 0 && n `mod` leanCheckpointEvery == 0 ->
                writeCheckpoint p n
              _ -> pure ()
            t0 <- nowSec
            let !r = prop x
            t1 <- nowSec
            modifyIORef' execAccum (+ (t1 - t0))
            if r
              then go (n + 1) xs
              else pure (n + 1, Just x)
  trialStart <- nowSec
  (tested, mfail) <- go resume (drop resume list)
  trialEnd <- nowSec
  exec_time_pre <- readIORef execAccum
  let foundbug = isJust mfail
      tests = if foundbug then tested - 1 else tested
      discards = Nothing
      cexStr = maybe "" show mfail
      counterexample = cexStr
      pre_counterexample = cexStr
      status = if foundbug then "Failed" else "Finished"
      exec_time_shrink = 0
      time_pre_failure = trialEnd - trialStart
      time_shrinking = 0
      shrinking_passed = 0
      shrinking_failed = 0
      shrinking_discarded = 0
  return Result {..}
