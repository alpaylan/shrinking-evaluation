{-# LANGUAGE BangPatterns #-}
{-# LANGUAGE LambdaCase #-}
{-# LANGUAGE RecordWildCards #-}
{-# LANGUAGE ScopedTypeVariables #-}

-- | ETNA runner for the nonempty-containers workload.
--
-- This runner has been adapted to emit the same per-trial JSON schema
-- as the rest of the @shrinking-evaluation@ experiment (see
-- @workloads/bst-haskell/etna-lib/src/Etna/Lib/Trial.hs@). On top of
-- the original status/tests/counterexample fields it carries:
--
--   * @pre_counterexample@       - first failing input observed (before shrinking)
--   * @shrinks@                  - the @ETNA_SHRINKS@ value used for this trial
--   * @exec_time_pre@            - cumulative property-body time before first failure
--   * @exec_time_shrink@         - cumulative property-body time during shrinking
--   * @time_pre_failure@         - wall-clock from trial start to first failure
--   * @time_shrinking@           - wall-clock from first failure to trial end
--
-- These let downstream analysis (AnalyzeShrinking.py) decompose the
-- @time@ field into pre-failure / shrinking phases for each strategy.
module Main where

import           Control.Exception     (SomeException, bracket, try)
import           Control.Monad         (unless, when)
import           Data.IORef            (IORef, modifyIORef', newIORef, readIORef, writeIORef)
import           System.Environment    (getArgs)
import           System.Exit           (exitWith, ExitCode(..))
import           System.IO             ( hFlush, stdout
                                       , openFile, IOMode(..), hClose, hSetBuffering
                                       , BufferMode(..) )
import           GHC.IO.Handle         (hDuplicate, hDuplicateTo)
import           System.IO.Unsafe      (unsafePerformIO)
import           Text.Printf           (printf)

import           Etna.Result           (PropertyResult(..))
import           Etna.Timing           (nowSec, ShrinkMode (..), shrinkModeFromEnv, shrinkModeName, shrinkModeNumber, markStart, accumExec, markFailure, bumpShrink)
import qualified Etna.Properties       as P
import qualified Etna.Witnesses        as W
import qualified Etna.Gens.QuickCheck  as GQ
import qualified Etna.Gens.Hedgehog    as GH
import qualified Etna.Gens.Falsify     as GF
import qualified Etna.Gens.SmallCheck  as GS

import qualified Test.QuickCheck                    as QC
import qualified Test.QuickCheck.Property           as QCP
import qualified Hedgehog                           as HH
import qualified Test.Falsify.Generator             as FG
import qualified Test.Falsify.Property              as FP
import           Test.Tasty.Falsify
                   ( TestOptions (..)
                   , ExpectFailure (DontExpectFailure)
                   , testPropertyWith
                   )
import           Test.Tasty.Runners               (FailureReason (..), Result (..), TreeFold (..))
import qualified Test.Tasty.Runners               as TTR
import qualified Test.Tasty.Providers             as TP
import qualified Test.SmallCheck                    as SC
import qualified Test.SmallCheck.Drivers            as SCD
import qualified Test.SmallCheck.Series             as SCS

------------------------------------------------------------------------------
-- Workload-level metadata.

workloadName :: String
workloadName = "psqueues"

allProperties :: [String]
allProperties =
  [ "OrdPsqFromListLastOccurrenceWins"
  , "HashPsqInsertEqualPriorityKeyTieBreak"
  , "OrdPsqBalanceAfterOperations"
  ]

------------------------------------------------------------------------------
-- Result type carrying the full shrinking-evaluation schema.

data Outcome = Outcome
  { oStatus        :: String
  , oTests         :: Int
  , oCex           :: Maybe String
  , oPreCex        :: Maybe String
  , oErr           :: Maybe String
  , oExecPre       :: Double
  , oExecShrink    :: Double
  , oTimePre       :: Double
  , oTimeShrink    :: Double
  , oShrinkPassed     :: Int
  , oShrinkFailed     :: Int
  , oShrinkDiscarded  :: Int
  }

-- | Outcome with all the extras zero / unset. The driver-specific
-- runners build on top of this.
emptyOutcome :: String -> Int -> Maybe String -> Maybe String -> Outcome
emptyOutcome status tests cex err =
  Outcome status tests cex Nothing err 0 0 0 0 0 0 0

------------------------------------------------------------------------------
-- Entry point.

main :: IO ()
main = do
  argv <- getArgs
  case argv of
    [tool, prop] -> dispatch tool prop
    _            -> do
      putStrLn "{\"status\":\"aborted\",\"error\":\"usage: etna-runner <tool> <property>\"}"
      hFlush stdout
      exitWith (ExitFailure 2)

dispatch :: String -> String -> IO ()
dispatch tool prop
  | prop /= "All" && prop `notElem` allProperties =
      emit tool prop (emptyOutcome "aborted" 0 Nothing (Just $ "unknown property: " ++ prop)) 0
  | otherwise = do
      let targets = if prop == "All" then allProperties else [prop]
      mapM_ (runOne tool) targets

runOne :: String -> String -> IO ()
runOne tool prop = do
  t0 <- nowSec
  result <- try (driver tool prop) :: IO (Either SomeException Outcome)
  t1 <- nowSec
  let totalSec = t1 - t0
  case result of
    Left e   -> emit tool prop (emptyOutcome "aborted" 0 Nothing (Just (show e))) totalSec
    Right oc -> emit tool prop oc totalSec

driver :: String -> String -> IO Outcome
driver "etna"       p = runWitnesses p
driver "quickcheck" p = runQuickCheck p
driver "hedgehog"   p = runHedgehog   p
driver "falsify"    p = runFalsify    p
driver "smallcheck" p = runSmallCheck p
driver tool         _ = pure (emptyOutcome "aborted" 0 Nothing (Just ("unknown tool: " ++ tool)))

------------------------------------------------------------------------------
-- Tool: etna (witness replay) - timing fields stay at 0 (one-shot).

runWitnesses :: String -> IO Outcome
runWitnesses prop = case witnessesFor prop of
  []    -> pure (emptyOutcome "aborted" 0 Nothing (Just ("no witnesses for " ++ prop)))
  cs    -> go cs 0
  where
    go [] n = pure (emptyOutcome "passed" n Nothing Nothing)
    go ((name, r):rest) n = case r of
      Pass     -> go rest (n + 1)
      Discard  -> go rest (n + 1)
      Fail msg -> pure (emptyOutcome "failed" (n + 1) (Just name) (Just msg))

witnessesFor :: String -> [(String, PropertyResult)]
witnessesFor "OrdPsqFromListLastOccurrenceWins" =
  [ ("witness_ord_psq_from_list_last_occurrence_wins_case_two_dup", W.witness_ord_psq_from_list_last_occurrence_wins_case_two_dup)
  , ("witness_ord_psq_from_list_last_occurrence_wins_case_three_dup", W.witness_ord_psq_from_list_last_occurrence_wins_case_three_dup)
  ]
witnessesFor "HashPsqInsertEqualPriorityKeyTieBreak" =
  [ ("witness_hash_psq_insert_equal_priority_key_tie_break_case_descending", W.witness_hash_psq_insert_equal_priority_key_tie_break_case_descending)
  , ("witness_hash_psq_insert_equal_priority_key_tie_break_case_three_apart", W.witness_hash_psq_insert_equal_priority_key_tie_break_case_three_apart)
  ]
witnessesFor "OrdPsqBalanceAfterOperations" =
  [ ("witness_ord_psq_balance_after_operations_case_ascending_64", W.witness_ord_psq_balance_after_operations_case_ascending_64)
  , ("witness_ord_psq_balance_after_operations_case_ascending_128", W.witness_ord_psq_balance_after_operations_case_ascending_128)
  ]
witnessesFor _ = []

------------------------------------------------------------------------------
-- Tool: quickcheck (with idempotentIOProperty + PostTest phase tracking).

runQuickCheck :: String -> IO Outcome
runQuickCheck "OrdPsqFromListLastOccurrenceWins" =
  qcDrive GQ.gen_ord_psq_from_list_last_occurrence_wins GQ.shrink_ord_psq_from_list_last_occurrence_wins P.property_ord_psq_from_list_last_occurrence_wins
runQuickCheck "HashPsqInsertEqualPriorityKeyTieBreak" =
  qcDrive GQ.gen_hash_psq_insert_equal_priority_key_tie_break GQ.shrink_hash_psq_insert_equal_priority_key_tie_break P.property_hash_psq_insert_equal_priority_key_tie_break
runQuickCheck "OrdPsqBalanceAfterOperations" =
  qcDrive GQ.gen_ord_psq_balance_after_operations GQ.shrink_ord_psq_balance_after_operations P.property_ord_psq_balance_after_operations
runQuickCheck p = pure (emptyOutcome "aborted" 0 Nothing (Just ("unknown property: " ++ p)))

qcDrive :: forall a. (Show a) => QC.Gen a -> (a -> [a]) -> (a -> PropertyResult) -> IO Outcome
qcDrive gen shrinkFn f = do
  preRef          <- newIORef ""
  testStartRef    <- newIORef 0
  trialStart      <- nowSec
  failureMarkRef  <- newIORef Nothing
  execPreRef      <- newIORef 0
  execShrinkRef   <- newIORef 0
  shrinkPassedRef    <- newIORef 0
  shrinkFailedRef    <- newIORef 0
  shrinkDiscardedRef <- newIORef 0

  let mkCb a = QCP.PostTest QCP.NotCounterexample $ \_ res -> do
        tEnd  <- nowSec
        tStart <- readIORef testStartRef
        mFail  <- readIORef failureMarkRef
        let dur = tEnd - tStart
        case mFail of
          Nothing -> modifyIORef' execPreRef (+ dur)
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
          _ -> pure ()
      prop a = QCP.callback (mkCb a) $
               QCP.idempotentIOProperty $ do
                 t <- nowSec
                 writeIORef testStartRef t
                 pure $ qcProp f a

  let qcBase = QC.stdArgs { QC.maxSuccess = maxBound, QC.chatty = False }
      qcArgs = case shrinkModeFromEnv of
        ShrinkDefault   -> qcBase
        ShrinkNone      -> qcBase { QC.maxShrinks = 0 }
        ShrinkFixed n   -> qcBase { QC.maxShrinks = n }
  result   <- QC.quickCheckWithResult qcArgs (QC.forAllShrink gen shrinkFn prop)
  trialEnd <- nowSec
  pre      <- readIORef preRef
  ePre     <- readIORef execPreRef
  eShr     <- readIORef execShrinkRef
  sPass    <- readIORef shrinkPassedRef
  sFail    <- readIORef shrinkFailedRef
  sDisc    <- readIORef shrinkDiscardedRef
  mFail    <- readIORef failureMarkRef
  let (tPre, tShr) = case mFail of
        Just g  -> (g - trialStart, trialEnd - g)
        Nothing -> (trialEnd - trialStart, 0)
      preMaybe = if null pre then Nothing else Just pre

  pure $ case result of
    QC.Success { QC.numTests = n } ->
      Outcome "passed" n Nothing Nothing Nothing ePre eShr tPre tShr sPass sFail sDisc
    QC.Failure { QC.numTests = n, QC.failingTestCase = tc } ->
      Outcome "failed" n (Just (concat tc)) preMaybe Nothing ePre eShr tPre tShr sPass sFail sDisc
    QC.GaveUp  { QC.numTests = n } ->
      Outcome "aborted" n Nothing Nothing (Just "QuickCheck gave up") ePre eShr tPre tShr sPass sFail sDisc
    QC.NoExpectedFailure { QC.numTests = n } ->
      Outcome "aborted" n Nothing Nothing (Just "no expected failure") ePre eShr tPre tShr sPass sFail sDisc

qcProp :: (a -> PropertyResult) -> a -> QC.Property
qcProp f args = case f args of
  Pass     -> QC.property True
  Discard  -> QC.discard
  Fail msg -> QC.counterexample msg (QC.property False)

------------------------------------------------------------------------------
-- Tool: hedgehog (evalIO timestamps + withShrinks).

runHedgehog :: String -> IO Outcome
runHedgehog "OrdPsqFromListLastOccurrenceWins" =
  hhDrive GH.gen_ord_psq_from_list_last_occurrence_wins P.property_ord_psq_from_list_last_occurrence_wins
runHedgehog "HashPsqInsertEqualPriorityKeyTieBreak" =
  hhDrive GH.gen_hash_psq_insert_equal_priority_key_tie_break P.property_hash_psq_insert_equal_priority_key_tie_break
runHedgehog "OrdPsqBalanceAfterOperations" =
  hhDrive GH.gen_ord_psq_balance_after_operations P.property_ord_psq_balance_after_operations
runHedgehog p = pure (emptyOutcome "aborted" 0 Nothing (Just ("unknown property: " ++ p)))

hhDrive
  :: (Show a) => HH.Gen a -> (a -> PropertyResult) -> IO Outcome
hhDrive gen f = do
  preRef         <- newIORef ""
  failureMarkRef <- newIORef (Nothing :: Maybe Double)
  execPreRef     <- newIORef 0
  execShrinkRef  <- newIORef 0
  shrinkPassedRef    <- newIORef 0
  shrinkFailedRef    <- newIORef 0
  shrinkDiscardedRef <- newIORef 0
  let applyShrinkMode = case shrinkModeFromEnv of
        ShrinkDefault -> id
        ShrinkNone    -> HH.withShrinks 0
        ShrinkFixed n -> HH.withShrinks (fromIntegral n)
      test = HH.withTests (fromIntegral (maxBound :: Int)) $ applyShrinkMode $
             HH.property $ do
               args <- HH.forAll gen
               let res = f args
               -- Time the result evaluation; route to the right phase
               -- bucket; record first failure's timestamp + input.
               HH.evalIO $ do
                 t0 <- nowSec
                 res `seq` pure ()
                 t1 <- nowSec
                 mf <- readIORef failureMarkRef
                 modifyIORef' (case mf of Nothing -> execPreRef; Just _ -> execShrinkRef) (+ (t1 - t0))
                 case mf of
                   Just _  -> case res of
                     Pass    -> modifyIORef' shrinkPassedRef    (+ 1)
                     Fail _  -> modifyIORef' shrinkFailedRef    (+ 1)
                     Discard -> modifyIORef' shrinkDiscardedRef (+ 1)
                   Nothing -> pure ()
                 case res of
                   Fail _ -> do
                     mf2 <- readIORef failureMarkRef
                     case mf2 of
                       Nothing -> writeIORef failureMarkRef (Just t1)
                       Just _  -> pure ()
                     p <- readIORef preRef
                     when (null p) $ writeIORef preRef (show args)
                   _ -> pure ()
               case res of
                 Pass     -> pure ()
                 Discard  -> HH.discard
                 Fail msg -> HH.annotate msg >> HH.failure

  trialStart <- nowSec
  ok         <- silencingStdout (HH.check test)
  trialEnd   <- nowSec
  pre        <- readIORef preRef
  ePre       <- readIORef execPreRef
  eShr       <- readIORef execShrinkRef
  sPass      <- readIORef shrinkPassedRef
  sFail      <- readIORef shrinkFailedRef
  sDisc      <- readIORef shrinkDiscardedRef
  mFail      <- readIORef failureMarkRef
  let (tPre, tShr) = case mFail of
        Just g  -> (g - trialStart, trialEnd - g)
        Nothing -> (trialEnd - trialStart, 0)
      preMaybe = if null pre then Nothing else Just pre
  pure $ if ok
    then Outcome "passed" 200 Nothing Nothing Nothing ePre eShr tPre tShr sPass sFail sDisc
    else Outcome "failed" 1   (Just pre) preMaybe Nothing ePre eShr tPre tShr sPass sFail sDisc

silencingStdout :: IO a -> IO a
silencingStdout act =
  bracket
    (do hFlush stdout
        saved <- hDuplicate stdout
        nullH <- openFile "/dev/null" WriteMode
        hSetBuffering nullH NoBuffering
        hDuplicateTo nullH stdout
        hClose nullH
        pure saved)
    (\saved -> do
        hFlush stdout
        hDuplicateTo saved stdout
        hClose saved)
    (const act)

------------------------------------------------------------------------------
-- Tool: falsify (Test.Tasty.Falsify so we can override maxShrinks; the
-- pure Property monad is threaded with unsafePerformIO timing helpers,
-- mirroring the BST/RBT/STLC etna-lib pattern).

runFalsify :: String -> IO Outcome
runFalsify "OrdPsqFromListLastOccurrenceWins" =
  fsDrive GF.gen_ord_psq_from_list_last_occurrence_wins P.property_ord_psq_from_list_last_occurrence_wins
runFalsify "HashPsqInsertEqualPriorityKeyTieBreak" =
  fsDrive GF.gen_hash_psq_insert_equal_priority_key_tie_break P.property_hash_psq_insert_equal_priority_key_tie_break
runFalsify "OrdPsqBalanceAfterOperations" =
  fsDrive GF.gen_ord_psq_balance_after_operations P.property_ord_psq_balance_after_operations
runFalsify p = pure (emptyOutcome "aborted" 0 Nothing (Just ("unknown property: " ++ p)))

fsDrive
  :: (Show a)
  => FG.Gen a
  -> (a -> PropertyResult)
  -> IO Outcome
fsDrive gen f = do
  preRef         <- newIORef ""
  cexRef         <- newIORef ""
  testStartRef   <- newIORef 0
  failureMarkRef <- newIORef (Nothing :: Maybe Double)
  execPreRef     <- newIORef 0
  execShrinkRef  <- newIORef 0
  shrinkPassedRef    <- newIORef 0
  shrinkFailedRef    <- newIORef 0
  shrinkDiscardedRef <- newIORef 0
  let shrinkMode = shrinkModeFromEnv
      prop = do
        a <- FP.gen gen
        let res = f a
        markStart testStartRef `seq` pure ()
        res `seq` pure ()
        accumExec testStartRef failureMarkRef execPreRef execShrinkRef `seq` pure ()
        case res of
          Pass     -> bumpShrink failureMarkRef shrinkPassedRef    `seq` pure ()
          Discard  -> bumpShrink failureMarkRef shrinkDiscardedRef `seq` FP.discard
          Fail msg -> bumpShrink failureMarkRef shrinkFailedRef    `seq`
                      recordFsFailure cexRef preRef failureMarkRef a `seq`
                      FP.testFailed (show a ++ ": " ++ msg)

      testOptions = TestOptions
        { expectFailure       = DontExpectFailure
        , overrideVerbose     = Nothing
        -- ShrinkDefault leaves overrideMaxShrinks=Nothing so Falsify's own default
        -- (no cap) applies. ShrinkNone/ShrinkFixed override.
        , overrideMaxShrinks  = case shrinkMode of
            ShrinkDefault -> Nothing
            ShrinkNone    -> Just 0
            ShrinkFixed n -> Just (fromIntegral n)
        , overrideNumTests    = Just (fromIntegral (maxBound :: Int))
        , overrideMaxRatio    = Just (fromIntegral (maxBound :: Int))
        }
      go (TTR.SingleTest _ t) = TP.run mempty t (\_ -> pure ())

  trialStart <- nowSec
  tastyRes   <- go $ testPropertyWith testOptions "falsify" prop
  -- Force the lazy ShrinkExplanation so Falsify actually walks the tree;
  -- skip in ShrinkNone mode.
  let !_forceShrink = case shrinkMode of
        ShrinkNone -> 0
        _          -> length (TTR.resultDescription tastyRes)
  trialEnd   <- nowSec

  let ok    = TTR.resultSuccessful tastyRes
      cex   = case TTR.resultDescription tastyRes of
                "" -> Nothing
                s  -> Just s
  pre        <- readIORef preRef
  ePre       <- readIORef execPreRef
  eShr       <- readIORef execShrinkRef
  sPass      <- readIORef shrinkPassedRef
  sFail      <- readIORef shrinkFailedRef
  sDisc      <- readIORef shrinkDiscardedRef
  mFail      <- readIORef failureMarkRef
  let (tPre, tShr) = case mFail of
        Just g  -> (g - trialStart, trialEnd - g)
        Nothing -> (trialEnd - trialStart, 0)
      preMaybe = if null pre then Nothing else Just pre
  pure $ if ok
    then Outcome "passed" 100 Nothing Nothing Nothing ePre eShr tPre tShr sPass sFail sDisc
    else Outcome "failed" 1   cex      preMaybe Nothing ePre eShr tPre tShr sPass sFail sDisc

-- | Side-effecting helper: record both the running counterexample and
-- the first failure mark + pre-counterexample. Returns @()@; sequence
-- with @\`seq\` ...@ at the call site.
recordFsFailure
  :: (Show a)
  => IORef String
  -> IORef String
  -> IORef (Maybe Double)
  -> a
  -> ()
recordFsFailure cexRef preRef failureMarkRef a =
  markFailure failureMarkRef `seq`
  unsafeRecord cexRef a       `seq`
  unsafeRecordOnce preRef a   `seq` ()

unsafeRecord :: (Show a) => IORef String -> a -> ()
unsafeRecord ref a = unsafePerformIO (writeIORef ref (show a))
{-# NOINLINE unsafeRecord #-}

unsafeRecordOnce :: (Show a) => IORef String -> a -> ()
unsafeRecordOnce ref a = unsafePerformIO $ do
  cur <- readIORef ref
  when (null cur) (writeIORef ref (show a))
{-# NOINLINE unsafeRecordOnce #-}

------------------------------------------------------------------------------
-- Tool: smallcheck (enumerator: shrink fields are zero by construction).

runSmallCheck :: String -> IO Outcome
runSmallCheck "OrdPsqFromListLastOccurrenceWins" =
  scDrive GS.series_ord_psq_from_list_last_occurrence_wins P.property_ord_psq_from_list_last_occurrence_wins
runSmallCheck "HashPsqInsertEqualPriorityKeyTieBreak" =
  scDrive GS.series_hash_psq_insert_equal_priority_key_tie_break P.property_hash_psq_insert_equal_priority_key_tie_break
runSmallCheck "OrdPsqBalanceAfterOperations" =
  scDrive GS.series_ord_psq_balance_after_operations P.property_ord_psq_balance_after_operations
runSmallCheck p = pure (emptyOutcome "aborted" 0 Nothing (Just ("unknown property: " ++ p)))

scDrive
  :: (Show a)
  => SCS.Series IO a
  -> (a -> PropertyResult)
  -> IO Outcome
scDrive series f = do
  countRef  <- newIORef (0 :: Int)
  execAccum <- newIORef 0
  let depth = 5
      check args = SC.monadic $ do
        t0 <- nowSec
        modifyIORef' countRef (+1)
        let !r = case f args of
                   Pass    -> True
                   Discard -> True
                   Fail _  -> False
        t1 <- nowSec
        modifyIORef' execAccum (+ (t1 - t0))
        pure r
      smTest = SC.over series check

  trialStart <- nowSec
  res        <- try (SCD.smallCheckM depth smTest)
                 :: IO (Either SomeException (Maybe SCD.PropertyFailure))
  trialEnd   <- nowSec
  n          <- readIORef countRef
  ePre       <- readIORef execAccum
  let totalSec = trialEnd - trialStart
  pure $ case res of
    Left e          -> Outcome "failed" n Nothing Nothing (Just (show e)) ePre 0 totalSec 0 0 0 0
    Right Nothing   -> Outcome "passed" n Nothing Nothing Nothing         ePre 0 totalSec 0 0 0 0
    Right (Just pf) -> Outcome "failed" n (Just (show pf)) (Just (show pf)) Nothing ePre 0 totalSec 0 0 0 0

------------------------------------------------------------------------------
-- JSON emission (matching shrinking-evaluation's FullResult schema).

emit :: String -> String -> Outcome -> Double -> IO ()
emit tool prop Outcome{..} totalSec = do
  let q = quoteJSON
      esc Nothing  = "null"
      esc (Just s) = q s
      mtests = oTests
      mode = shrinkModeFromEnv
      shrinks = shrinkModeNumber mode
  printf "{\"workload\":%s,\"strategy\":%s,\"property\":%s,\"status\":%s,\"tests\":%d,\"discards\":0,\"time\":\"%.6fs\",\"counterexample\":%s,\"pre_counterexample\":%s,\"shrinks\":%d,\"shrink_mode\":%s,\"shrinking_passed\":%d,\"shrinking_failed\":%d,\"shrinking_discarded\":%d,\"exec_time_pre\":%.9f,\"exec_time_shrink\":%.9f,\"time_pre_failure\":%.9f,\"time_shrinking\":%.9f,\"error\":%s}\n"
    (q workloadName)
    (q tool)
    (q prop)
    (q oStatus)
    mtests
    totalSec
    (esc oCex)
    (esc oPreCex)
    shrinks
    (q (shrinkModeName mode))
    oShrinkPassed oShrinkFailed oShrinkDiscarded
    oExecPre oExecShrink oTimePre oTimeShrink
    (esc oErr)
  hFlush stdout

quoteJSON :: String -> String
quoteJSON s = '"' : concatMap esc s ++ "\""
  where
    esc '"'  = "\\\""
    esc '\\' = "\\\\"
    esc '\n' = "\\n"
    esc '\r' = "\\r"
    esc '\t' = "\\t"
    esc c | fromEnum c < 0x20 = printf "\\u%04x" (fromEnum c)
          | otherwise = [c]
