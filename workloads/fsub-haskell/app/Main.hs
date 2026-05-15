{-# LANGUAGE TemplateHaskell #-}

module Main where

import Etna.Lib
import Data.List (lookup)
import Data.Maybe (fromJust)
import Strategy.Correct as Correct
import Strategy.Falsify as Falsify
import Strategy.FalsifyCBC as FalsifyCBC
import Strategy.FalsifyCBC2 as FalsifyCBC2
import Strategy.Hedgehog as Hedgehog
import Strategy.HedgehogCBC as HedgehogCBC
import Strategy.HedgehogCBC2 as HedgehogCBC2
import Strategy.Lean as Lean
import Strategy.LeanRev as LeanRev
import Strategy.Quick as Quick
import Strategy.QuickIndex as QuickIndex
import Strategy.Small as Small
import Strategy.SmallRev as SmallRev
import System.Environment (getArgs)

$( mkMain
     ( return
         [ "Correct",
           "Falsify",
           "FalsifyCBC",
           "FalsifyCBC2",
           "Hedgehog",
           "HedgehogCBC",
           "HedgehogCBC2",
           "Lean",
           "LeanRev",
           "Quick",
           "QuickIndex",
           "Small",
           "SmallRev"
         ]
     )
     (allProps "src/Spec.hs")
 )