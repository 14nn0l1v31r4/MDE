-- Migration 001: Enforce mandatory resource ownership on datasets and analysis_results
-- Run audit check first: abort if orphaned records exist

DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM datasets WHERE user_id IS NULL OR user_id = '')
       OR EXISTS (SELECT 1 FROM analysis_results WHERE user_id IS NULL OR user_id = '') THEN
        RAISE EXCEPTION 'Ownership migration required before enforcing NOT NULL: found records without user_id';
    END IF;
END $$;

ALTER TABLE datasets ALTER COLUMN user_id SET NOT NULL;
ALTER TABLE analysis_results ALTER COLUMN user_id SET NOT NULL;

