-- ============================================================================
-- Blockchain Indexer Database Schema
-- ============================================================================
--
-- This schema defines the database structure for storing blockchain blocks
-- and transactions. Optimized for PostgreSQL.
--
-- Features:
--   - Primary and foreign key constraints
--   - Indexes for common queries
--   - ON CONFLICT handling for idempotency
--   - Timestamps for auditing
--
-- Author: Don Fox
-- Date: 2025-12-09
-- ============================================================================

-- Drop existing tables (careful in production!)
-- DROP TABLE IF EXISTS transactions CASCADE;
-- DROP TABLE IF EXISTS blocks CASCADE;

-- ============================================================================
-- BLOCKS TABLE
-- ============================================================================
CREATE TABLE IF NOT EXISTS blocks (
    block_height BIGINT PRIMARY KEY,
    block_hash VARCHAR(128) NOT NULL UNIQUE,
    timestamp TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),

    CONSTRAINT valid_height CHECK (block_height >= 0)
);

-- Indexes for blocks table
CREATE INDEX IF NOT EXISTS idx_blocks_timestamp ON blocks(timestamp);
CREATE INDEX IF NOT EXISTS idx_blocks_created_at ON blocks(created_at);
CREATE INDEX IF NOT EXISTS idx_blocks_hash ON blocks(block_hash);

-- Comment on blocks table
COMMENT ON TABLE blocks IS 'Stores blockchain block metadata';
COMMENT ON COLUMN blocks.block_height IS 'Block height/number (primary key)';
COMMENT ON COLUMN blocks.block_hash IS 'Unique block hash identifier';
COMMENT ON COLUMN blocks.timestamp IS 'Block timestamp from blockchain';
COMMENT ON COLUMN blocks.created_at IS 'When this record was inserted';

-- ============================================================================
-- TRANSACTIONS TABLE
-- ============================================================================
CREATE TABLE IF NOT EXISTS transactions (
    tx_hash VARCHAR(128) PRIMARY KEY,
    block_height BIGINT NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),

    CONSTRAINT fk_block FOREIGN KEY (block_height)
        REFERENCES blocks(block_height)
        ON DELETE CASCADE
);

-- Indexes for transactions table
CREATE INDEX IF NOT EXISTS idx_transactions_block ON transactions(block_height);
CREATE INDEX IF NOT EXISTS idx_transactions_created_at ON transactions(created_at);

-- Comment on transactions table
COMMENT ON TABLE transactions IS 'Stores blockchain transaction hashes';
COMMENT ON COLUMN transactions.tx_hash IS 'Transaction hash (primary key)';
COMMENT ON COLUMN transactions.block_height IS 'Block this transaction belongs to';
COMMENT ON COLUMN transactions.created_at IS 'When this record was inserted';

-- ============================================================================
-- USEFUL VIEWS
-- ============================================================================

-- View: Block summary with transaction counts
CREATE OR REPLACE VIEW block_summary AS
SELECT
    b.block_height,
    b.block_hash,
    b.timestamp,
    COUNT(t.tx_hash) AS tx_count,
    b.created_at
FROM blocks b
LEFT JOIN transactions t ON b.block_height = t.block_height
GROUP BY b.block_height, b.block_hash, b.timestamp, b.created_at
ORDER BY b.block_height DESC;

COMMENT ON VIEW block_summary IS 'Block summary with transaction counts';

-- View: Recent blocks (last 100)
CREATE OR REPLACE VIEW recent_blocks AS
SELECT * FROM block_summary
ORDER BY block_height DESC
LIMIT 100;

COMMENT ON VIEW recent_blocks IS 'Most recent 100 blocks with transaction counts';

-- ============================================================================
-- HELPER FUNCTIONS
-- ============================================================================

-- Function: Get total number of blocks
CREATE OR REPLACE FUNCTION get_total_blocks()
RETURNS BIGINT AS $$
BEGIN
    RETURN (SELECT COUNT(*) FROM blocks);
END;
$$ LANGUAGE plpgsql;

-- Function: Get total number of transactions
CREATE OR REPLACE FUNCTION get_total_transactions()
RETURNS BIGINT AS $$
BEGIN
    RETURN (SELECT COUNT(*) FROM transactions);
END;
$$ LANGUAGE plpgsql;

-- Function: Detect gaps in block sequence
CREATE OR REPLACE FUNCTION detect_block_gaps()
RETURNS TABLE(gap_start BIGINT, gap_end BIGINT, gap_size BIGINT) AS $$
BEGIN
    RETURN QUERY
    SELECT
        b1.block_height + 1 AS gap_start,
        b2.block_height - 1 AS gap_end,
        b2.block_height - b1.block_height - 1 AS gap_size
    FROM blocks b1
    JOIN blocks b2 ON b2.block_height > b1.block_height
    WHERE NOT EXISTS (
        SELECT 1 FROM blocks b3
        WHERE b3.block_height > b1.block_height
        AND b3.block_height < b2.block_height
    )
    AND b2.block_height - b1.block_height > 1
    ORDER BY gap_start;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION detect_block_gaps() IS 'Detects gaps in the block sequence';

-- ============================================================================
-- GRANTS (adjust as needed for your user)
-- ============================================================================
-- GRANT SELECT, INSERT, UPDATE, DELETE ON blocks TO donfox1;
-- GRANT SELECT, INSERT, UPDATE, DELETE ON transactions TO donfox1;
-- GRANT SELECT ON block_summary TO donfox1;
-- GRANT SELECT ON recent_blocks TO donfox1;

-- ============================================================================
-- COMPLETION MESSAGE
-- ============================================================================
DO $$
BEGIN
    RAISE NOTICE '========================================';
    RAISE NOTICE 'Blockchain Indexer Schema Created';
    RAISE NOTICE 'Tables: blocks, transactions';
    RAISE NOTICE 'Views: block_summary, recent_blocks';
    RAISE NOTICE 'Functions: get_total_blocks(), get_total_transactions(), detect_block_gaps()';
    RAISE NOTICE '========================================';
END $$;
