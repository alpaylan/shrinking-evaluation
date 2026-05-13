{-# LANGUAGE DeriveGeneric #-}
{-# LANGUAGE DuplicateRecordFields #-}
{-# LANGUAGE RecordWildCards #-}

module Etna.Lib.Trial (run, sample) where

import Etna.Lib.Types (Result (Result))
import Etna.Lib.Util (shrinkModeFromEnv, shrinkModeName, shrinkModeNumber)
import qualified Etna.Lib.Types as B
import Control.Monad (forM)
import Data.Aeson (ToJSON, encode)
import Data.ByteString.Lazy.Char8 as B8 (appendFile)
import Data.Char (toLower)
import Data.IORef (modifyIORef, newIORef, readIORef)
import Data.List (intercalate)
import Data.Maybe (fromMaybe)
import GHC.Generics (Generic)
import System.Clock (Clock (..), getTime, toNanoSecs)
import System.IO.Silently (silence)
import System.TimeIt (timeItT)
import System.Timeout (timeout)
import Text.Printf (printf)
import qualified Data.ByteString.Lazy.Char8 as BL

import Test.QuickCheck hiding (Result, sample)
import Test.QuickCheck.Property hiding (Result)

import Data.IORef
import Data.Time.Clock
import Text.Printf

import Control.Monad
import Data.List



-- workload/strategy/property are intentionally NOT fields here. Etna seeds
-- the metric with those (from the test JSON's task fields) before merging
-- this output, and the merge lets runtime JSON override context. Echoing
-- them back from Haskell would shadow etna's bare task names with the
-- internally-prefixed `prop_X` form, which breaks `metric_matches` dedup
-- (etna2/src/driver.rs).
data FullResult = FullResult
  { status :: String,
    tests :: Maybe Int,
    discards :: Maybe Int,
    time :: String,
    counterexample :: String,
    pre_counterexample :: String,
    shrinks :: Int,
    shrink_mode :: String,
    exec_time_pre :: Double,
    exec_time_shrink :: Double,
    time_pre_failure :: Double,
    time_shrinking :: Double,
    shrinking_passed :: Maybe Int,
    shrinking_failed :: Maybe Int,
    shrinking_discarded :: Maybe Int
  }
  deriving (Generic)

instance ToJSON FullResult

type Timeout = Maybe Double

type Info = (String, String, String)

runOne :: Info -> Timeout -> IO Result -> IO FullResult
runOne (_workload, _strategy, _property) mtimeout test = do
  case mtimeout of
    Nothing -> run
    Just t -> fromMaybe (defaultResult (printf "%.6fs" t)) <$> timeout (fromSec t) run
  where
    run = do
      (time, Result {..}) <- myTimeIt $ eval $ silence test
      return FullResult
        { tests = Just tests
        , time = printf "%.6fs" time
        , shrinks = shrinkModeNumber shrinkModeFromEnv
        , shrink_mode = shrinkModeName shrinkModeFromEnv
        , shrinking_passed = Just shrinking_passed
        , shrinking_failed = Just shrinking_failed
        , shrinking_discarded = Just shrinking_discarded
        , ..
        }

    fromSec :: Double -> Int
    fromSec = round . (1000000 *)

    -- Returned if the trial timed out
    defaultResult time =
      FullResult
        { status = "Timed Out",
          tests = Nothing,
          discards = Nothing,
          counterexample = "",
          pre_counterexample = "",
          shrinks = shrinkModeNumber shrinkModeFromEnv,
          shrink_mode = shrinkModeName shrinkModeFromEnv,
          exec_time_pre = 0,
          exec_time_shrink = 0,
          time_pre_failure = 0,
          time_shrinking = 0,
          shrinking_passed = Nothing,
          shrinking_failed = Nothing,
          shrinking_discarded = Nothing,
          ..
        }

-- Based on `System.TimeIt`
myTimeIt :: IO a -> IO (Double, a)
myTimeIt ioa = do
  mt1 <- getTime Monotonic
  a <- ioa
  mt2 <- getTime Monotonic
  let t t2 t1 = fromIntegral (toNanoSecs t2 - toNanoSecs t1) * 1e-9
  return (t mt2 mt1, a)

-- Force evaluation (avoid laziness problems).
eval :: IO Result -> IO Result
eval ia = do
  Result {..} <- ia
  return Result {..}
{-# NOINLINE eval #-}

run :: Info -> Timeout -> IO Result -> IO ()
run info timeout test = do
  result <- runOne info timeout test
  putStrLn (BL.unpack (encode result))
  -- B8.appendFile file (encode result)
  -- Prelude.appendFile file "\n"



sample :: Int -> Property -> IO ()
sample tests property = quickSample tests property
  -- B8.appendFile file (encode result)
  -- Prelude.appendFile file "\n"



quickSample :: Int -> Property -> IO ()
quickSample n p = do
  let args = stdArgs{maxSuccess = n, chatty = False}
  ins <- newIORef []
  t <- getCurrentTime
  quickCheckWith args (callback (PostTest NotCounterexample (\_ res -> do
                                                                   t' <- getCurrentTime
                                                                   modifyIORef ins ((t', testCase res):))) p)
  cs <- readIORef ins
  tr <- newIORef t
  opts <- forM (reverse cs) $ \(t', c) -> do
    t0 <- readIORef tr
    writeIORef tr t'
    return ("{ \"time\" : \"" ++ show (diffUTCTime t' t0) ++ "\"," ++
            "  \"value\": \"" ++ unwords c ++ "\"}")
  putStrLn ("[" ++ intercalate ", " opts ++ "]")