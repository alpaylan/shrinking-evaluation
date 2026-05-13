{-# LANGUAGE NamedFieldPuns #-}
{-# LANGUAGE RecordWildCards #-}

module Etna.Lib.Util
  ( maxCap,
    readEnv,
    parseExpArgs,
    parseSampleArgs,
    allProps,
    mapExample,
    mapExample',
    ShrinkMode (..),
    shrinkModeFromEnv,
    shrinkModeName,
    shrinkModeNumber,
    nowSec,
    leanResumeFromEnv,
    leanCheckpointFromEnv,
    leanCheckpointEvery,
  )
where

import Etna.Lib.Types (ExpArgs, SampleArgs, Result (..))
import Data.Aeson (decode)
import Data.Char (isAlphaNum, isSpace)
import Data.List (elemIndex, isPrefixOf, nub)
import Data.String (fromString)
import GHC.IO (unsafePerformIO)
import System.Clock (Clock (Monotonic), getTime, toNanoSecs)
import System.Environment (getEnv, lookupEnv)

maxCap :: Int
maxCap = maxBound
-- Effectively unlimited test budget; only the wall-clock timeout
-- imposed by the etna driver should stop a trial.

readEnv :: Read a => String -> a
readEnv s = read $ unsafePerformIO $ getEnv s

-- ETNA_SHRINKS selects the shrink budget mode for property-based
-- shrinkers. Three encodings:
--   unset / empty / "default" -> ShrinkDefault (use the framework's
--                                built-in cap; intentionally different
--                                across QC/HH/Falsify)
--   "none"                    -> ShrinkNone (no shrinking-phase work;
--                                Falsify also skips the lazy explanation
--                                forcing that drives its shrink loop)
--   numeric N                 -> ShrinkFixed N (override the framework
--                                cap to N; semantics differ per framework)
data ShrinkMode = ShrinkDefault | ShrinkNone | ShrinkFixed Int
  deriving (Show, Eq)

shrinkModeFromEnv :: ShrinkMode
shrinkModeFromEnv =
  case unsafePerformIO (lookupEnv "ETNA_SHRINKS") of
    Nothing               -> ShrinkDefault
    Just s | null s       -> ShrinkDefault
           | s == "default" -> ShrinkDefault
           | s == "none"    -> ShrinkNone
           | otherwise      -> ShrinkFixed (read s)
{-# NOINLINE shrinkModeFromEnv #-}

shrinkModeName :: ShrinkMode -> String
shrinkModeName ShrinkDefault   = "default"
shrinkModeName ShrinkNone      = "none"
shrinkModeName (ShrinkFixed _) = "fixed"

-- Numeric companion to shrinkModeName for the FullResult.shrinks field.
-- Default and None both report 0; only Fixed carries a meaningful number.
shrinkModeNumber :: ShrinkMode -> Int
shrinkModeNumber ShrinkDefault   = 0
shrinkModeNumber ShrinkNone      = 0
shrinkModeNumber (ShrinkFixed n) = n

-- Resume offset for LeanCheck enumeration. Set ETNA_LEAN_RESUME=<N>
-- to skip the first N values of `list` before testing. Unset/empty/
-- non-numeric -> 0. Lets a timed-out LeanCheck trial be picked up by
-- a follow-up runner without redoing the property work.
leanResumeFromEnv :: IO Int
leanResumeFromEnv = do
  m <- lookupEnv "ETNA_LEAN_RESUME"
  case m of
    Nothing -> pure 0
    Just s | null s -> pure 0
           | otherwise -> pure (read s)

-- Optional checkpoint file path. If ETNA_LEAN_CHECKPOINT=<path> is set,
-- LeanCheck writes the current cumulative test index to that path every
-- leanCheckpointEvery iterations using atomic write-temp+rename. The
-- next run reads the file and passes it back via ETNA_LEAN_RESUME.
leanCheckpointFromEnv :: IO (Maybe FilePath)
leanCheckpointFromEnv = lookupEnv "ETNA_LEAN_CHECKPOINT"

leanCheckpointEvery :: Int
leanCheckpointEvery = 10000

-- Monotonic wall-clock as fractional seconds. Used by the strategy
-- modules to time the property body and pre-failure / shrinking phases.
nowSec :: IO Double
nowSec = do
  t <- getTime Monotonic
  pure $! fromIntegral (toNanoSecs t) * 1e-9

parseExpArgs :: String -> ExpArgs
parseExpArgs s = case decode . fromString $ s of
  Nothing -> error $ "Could not parse " ++ s
  Just a -> a

parseSampleArgs :: String -> SampleArgs
parseSampleArgs s = case decode . fromString $ s of
  Nothing -> error $ "Could not parse " ++ s
  Just a -> a

-- Closely adapted from Test.QuickCheck.All
allProps :: String -> IO [String]
allProps file = do
  ls <- lines <$> readFile file
  return $ nub $ filter ("prop_" `isPrefixOf`) $ prefixes ls
  where
    prefixes =
      map
        ( takeWhile (\c -> isAlphaNum c || c == '_' || c == '\'')
            . dropWhile (\c -> isSpace c || c == '>')
        )

parseTuple :: Read b => String -> b
parseTuple s@('(' : s') =
  case elemIndex ',' s' of
    Just i -> read $ take i s'
    Nothing -> read s
parseTuple s = read s

mapExample :: Read b => (b -> String) -> IO Result -> IO Result
mapExample f ir = do
  r@Result {counterexample, ..} <- ir
  if null counterexample
    then return r
    else return Result {counterexample = f (parseTuple counterexample), ..}

mapExample' :: (String -> String) -> IO Result -> IO Result
mapExample' f ir = do
  r@Result {counterexample, ..} <- ir
  if null counterexample
    then return r
    else return Result {counterexample = f counterexample, ..}