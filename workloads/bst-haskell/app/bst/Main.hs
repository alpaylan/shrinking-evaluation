{-# LANGUAGE TemplateHaskell #-}

module Main where

import Etna.Lib
import Data.List (lookup)
import Data.Maybe
import Strategy.Falsify as Falsify
import Strategy.FalsifyCBC as FalsifyCBC
import Strategy.FalsifyCBC2 as FalsifyCBC2
import Strategy.FalsifyCBC3 as FalsifyCBC3
import Strategy.FalsifyCBC4 as FalsifyCBC4
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
import Strategy.Size as Size
import Strategy.Small as Small
import Strategy.SmallRev as SmallRev
import System.Environment (getArgs)

-- Naming convention for the BST strategies:
--   Quick / QuickCBC / QuickGbE         = QuickCheck + (Naive | CBC | GbE)
--   Hedgehog / HedgehogCBC / HedgehogGbE = Hedgehog   + (Naive | CBC | GbE)
--   Falsify / FalsifyCBC / FalsifyGbE    = Falsify    + (Naive | CBC | GbE)
--   Lean / LeanRev                       = LeanCheck enumeration (no shrink)
--   Small / SmallRev                     = SmallCheck enumeration (no shrink)
--   Size                                 = parameterised input-size sweep
$( mkMain
     ( return
         [ "Falsify",
           "FalsifyCBC",
           "FalsifyCBC2",
           "FalsifyCBC3",
           "FalsifyCBC4",
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
           "Size",
           "Small",
           "SmallRev"
         ]
     )
     (allProps "src/Spec.hs")
 )
