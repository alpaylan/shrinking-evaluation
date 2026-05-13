{-# LANGUAGE DeriveGeneric #-}

module Etna.Lib.Types where

import Data.Aeson (FromJSON)
import Data.Functor
import GHC.Generics

data Result = Result
  { status :: String,
    tests :: Int,
    discards :: Maybe Int,
    counterexample :: String,
    pre_counterexample :: String,
    -- Phase timing (seconds). exec_* = time inside the property body.
    -- time_pre_failure = wall-clock from trial start to first failure;
    -- time_shrinking = wall-clock from first failure to trial end.
    exec_time_pre :: Double,
    exec_time_shrink :: Double,
    time_pre_failure :: Double,
    time_shrinking :: Double,
    -- Property evaluations during the shrinking phase, classified by
    -- outcome. 0 for strategies without a shrinking phase.
    shrinking_passed :: Int,
    shrinking_failed :: Int,
    shrinking_discarded :: Int
  }
  deriving (Show)

type Cap = Int

type PropPair = (Bool, Bool) -- (precondition, postcondition)

(-->) :: Bool -> Bool -> PropPair
(-->) = (,)

infixr 0 -->

type Task a = a -> PropPair

type Strategy a = Task a -> IO Result

data Approach = Correct | Naive

data ExpArgs = ExpArgs
  { workload :: String,
    strategy :: String,
    property :: String,
    timeout :: Maybe Double
  }
  deriving (Generic, Show)

instance FromJSON ExpArgs

data SampleArgs = SampleArgs
  { sstrategy :: String,
    sproperty :: String,
    stests    :: Int
  }
  deriving (Generic, Show)

instance FromJSON SampleArgs