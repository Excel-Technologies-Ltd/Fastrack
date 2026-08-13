DELIMITER $$

DROP PROCEDURE IF EXISTS GetLcNoByName$$

CREATE PROCEDURE GetLcNoByName(
    IN p_search VARCHAR(200),
    IN p_page INT,
    IN p_page_size INT
)
BEGIN

    DECLARE v_page INT DEFAULT 1;
    DECLARE v_page_size INT DEFAULT 20;
    DECLARE v_offset INT DEFAULT 0;
    DECLARE v_total_count INT DEFAULT 0;
    DECLARE v_total_pages INT DEFAULT 0;

    -- Page validation
    IF p_page IS NOT NULL AND p_page > 0 THEN
        SET v_page = p_page;
    END IF;

    -- Page size validation
    IF p_page_size IS NOT NULL AND p_page_size > 0 THEN
        SET v_page_size = p_page_size;
    END IF;

    SET v_offset = (v_page - 1) * v_page_size;


    /* =========================================
       Total L/C No. Count
       ========================================= */

    SELECT COUNT(*)
    INTO v_total_count
    FROM
    (
        SELECT DISTINCT LcNo
        FROM
        (
            -- Import Sea
            SELECT
                TRIM(COALESCE(ISHB.`lc`, '')) AS LcNo
            FROM `tabImport Sea House Bill` ISHB
            WHERE ISHB.`docstatus` = 1

            UNION ALL

            -- Import Air
            SELECT
                TRIM(COALESCE(IAHB.`lc_number`, '')) AS LcNo
            FROM `tabImport Air House Bill` IAHB
            WHERE IAHB.`docstatus` = 1

            UNION ALL

            -- Import D2D
            SELECT
                TRIM(COALESCE(ID2D.`lc_number`, '')) AS LcNo
            FROM `tabImport D2D Bill` ID2D
            WHERE ID2D.`docstatus` = 1

            UNION ALL

            -- Export Sea
            SELECT
                TRIM(COALESCE(ESHB.`lc_no`, '')) AS LcNo
            FROM `tabExport Sea House Bill` ESHB
            WHERE ESHB.`docstatus` = 1

            UNION ALL

            -- Export Air
            SELECT
                TRIM(COALESCE(EAHB.`lc_number`, '')) AS LcNo
            FROM `tabExport Air House Bill` EAHB
            WHERE EAHB.`docstatus` = 1

            UNION ALL

            -- Export D2D
            SELECT
                TRIM(COALESCE(ED2D.`lc_number`, '')) AS LcNo
            FROM `tabExport D2D Bill` ED2D
            WHERE ED2D.`docstatus` = 1

        ) AS AllLcNos

        WHERE LcNo <> ''
          AND (
                p_search IS NULL
                OR p_search = ''
                OR LcNo LIKE CONCAT('%', p_search, '%')
              )

    ) AS DistinctLcNos;


    SET v_total_pages = CEIL(v_total_count / v_page_size);


    /* =========================================
       Single JSON Response
       ========================================= */

    SELECT JSON_OBJECT(

        'data',
        COALESCE(
            (
                SELECT JSON_ARRAYAGG(LcNo)
                FROM
                (
                    SELECT DISTINCT LcNo
                    FROM
                    (
                        -- Import Sea
                        SELECT
                            TRIM(COALESCE(ISHB.`lc`, '')) AS LcNo
                        FROM `tabImport Sea House Bill` ISHB
                        WHERE ISHB.`docstatus` = 1

                        UNION ALL

                        -- Import Air
                        SELECT
                            TRIM(COALESCE(IAHB.`lc_number`, '')) AS LcNo
                        FROM `tabImport Air House Bill` IAHB
                        WHERE IAHB.`docstatus` = 1

                        UNION ALL

                        -- Import D2D
                        SELECT
                            TRIM(COALESCE(ID2D.`lc_number`, '')) AS LcNo
                        FROM `tabImport D2D Bill` ID2D
                        WHERE ID2D.`docstatus` = 1

                        UNION ALL

                        -- Export Sea
                        SELECT
                            TRIM(COALESCE(ESHB.`lc_no`, '')) AS LcNo
                        FROM `tabExport Sea House Bill` ESHB
                        WHERE ESHB.`docstatus` = 1

                        UNION ALL

                        -- Export Air
                        SELECT
                            TRIM(COALESCE(EAHB.`lc_number`, '')) AS LcNo
                        FROM `tabExport Air House Bill` EAHB
                        WHERE EAHB.`docstatus` = 1

                        UNION ALL

                        -- Export D2D
                        SELECT
                            TRIM(COALESCE(ED2D.`lc_number`, '')) AS LcNo
                        FROM `tabExport D2D Bill` ED2D
                        WHERE ED2D.`docstatus` = 1

                    ) AS AllLcNos

                    WHERE LcNo <> ''
                      AND (
                            p_search IS NULL
                            OR p_search = ''
                            OR LcNo LIKE CONCAT('%', p_search, '%')
                          )

                    ORDER BY LcNo ASC
                    LIMIT v_offset, v_page_size

                ) AS PaginatedLcNos
            ),
            JSON_ARRAY()
        ),

        'pagination',
        JSON_OBJECT(
            'page', v_page,
            'pageSize', v_page_size,
            'totalCount', v_total_count,
            'totalPages', v_total_pages
        )

    ) AS Result;

END$$

DELIMITER ;