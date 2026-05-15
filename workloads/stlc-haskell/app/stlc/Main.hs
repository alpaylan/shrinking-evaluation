{-# LANGUAGE TemplateHaskell #-}

module Main where

import Etna.Lib
import Data.List (lookup)
import Data.Maybe (fromJust)
import Strategy.Correct as Correct
import Strategy.Falsify as Falsify
import Strategy.FalsifyCBC as FalsifyCBC
import Strategy.Hedgehog as Hedgehog
import Strategy.HedgehogCBC as HedgehogCBC
import Strategy.Lean as Lean
import Strategy.LeanRev as LeanRev
import Strategy.Quick as Quick
import Strategy.Small as Small
import Strategy.SmallRev as SmallRev
import System.Environment (getArgs)

$( mkMain
     ( return
         [ "Correct",
           "Falsify",
           "FalsifyCBC",
           "Hedgehog",
           "HedgehogCBC",
           "Lean",
           "LeanRev",
           "Quick",
           "Small",
           "SmallRev"
         ]
     )
     (allProps "src/Spec.hs")
 )
