{-# LANGUAGE TemplateHaskell #-}

module Main where

import Etna.Lib
import Data.List (lookup)
import Data.Maybe
import Strategy.Correct as Correct
import Strategy.Falsify as Falsify
import Strategy.FalsifyCBC as FalsifyCBC
import Strategy.FalsifyCBC2 as FalsifyCBC2
import Strategy.FalsifyGbE as FalsifyGbE
import Strategy.Hedgehog as Hedgehog
import Strategy.HedgehogCBC as HedgehogCBC
import Strategy.HedgehogCBC2 as HedgehogCBC2
import Strategy.HedgehogGbE as HedgehogGbE
import Strategy.Lean as Lean
import Strategy.LeanRev as LeanRev
import Strategy.Quick as Quick
import Strategy.QuickCBC as QuickCBC
import Strategy.QuickGbE as QuickGbE
import Strategy.Small as Small
import Strategy.SmallRev as SmallRev
import System.Environment (getArgs)

$( mkMain
     ( return
         [ "Correct",
           "Falsify",
           "FalsifyCBC",
           "FalsifyCBC2",
           "FalsifyGbE",
           "Hedgehog",
           "HedgehogCBC",
           "HedgehogCBC2",
           "HedgehogGbE",
           "Lean",
           "LeanRev",
           "Quick",
           "QuickCBC",
           "QuickGbE",
           "Small",
           "SmallRev"
         ]
     )
     (allProps "src/Spec.hs")
 )
