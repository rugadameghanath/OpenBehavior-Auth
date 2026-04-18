CREATE OR REPLACE PROCEDURE ARCHIVE_OLD_SESSIONS AS
    v_cutoff TIMESTAMP;
BEGIN
    -- 1. Define the cutoff (6 months ago)
    v_cutoff := ADD_MONTHS(CURRENT_TIMESTAMP, -6);

    -- 2. Safely move old data to the Archive table
    INSERT INTO BehaviorLogs_Archive
    SELECT * FROM BehaviorLogs 
    WHERE created_at < v_cutoff;

    -- 3. Delete only the rows we just archived
    DELETE FROM BehaviorLogs 
    WHERE created_at < v_cutoff;

    -- 4. Save changes
    COMMIT;

EXCEPTION
    WHEN OTHERS THEN
        ROLLBACK; -- If a crash happens, undo everything to prevent data loss
        RAISE;
END;
/
