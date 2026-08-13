DELIMITER $$

DROP PROCEDURE IF EXISTS GetCarrierListByName$$

CREATE PROCEDURE GetCarrierListByName(
    IN p_search VARCHAR(250),
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
       Total Carrier Count
       ========================================= */

    SELECT COUNT(*)
    INTO v_total_count
    FROM
    (
        SELECT DISTINCT Carrier
        FROM
        (
            SELECT TRIM(COALESCE(ISHB.`carrier`, '')) AS Carrier
            FROM `tabImport Sea House Bill` ISHB
            WHERE ISHB.`docstatus` = 1

            UNION ALL

            SELECT TRIM(COALESCE(IAHB.`airlines`, '')) AS Carrier
            FROM `tabImport Air House Bill` IAHB
            WHERE IAHB.`docstatus` = 1

            UNION ALL

            SELECT TRIM(COALESCE(ESHB.`shipping_line`, '')) AS Carrier
            FROM `tabExport Sea House Bill` ESHB
            WHERE ESHB.`docstatus` = 1

            UNION ALL

            SELECT TRIM(COALESCE(EAHB.`airlines`, '')) AS Carrier
            FROM `tabExport Air House Bill` EAHB
            WHERE EAHB.`docstatus` = 1
        ) AS AllCarriers

        WHERE Carrier <> ''
          AND (
                p_search IS NULL
                OR p_search = ''
                OR Carrier LIKE CONCAT('%', p_search, '%')
              )
    ) AS DistinctCarriers;


    SET v_total_pages = CEIL(v_total_count / v_page_size);


    /* =========================================
       Single JSON Response
       ========================================= */

    SELECT JSON_OBJECT(

        'data',
        COALESCE(
            (
                SELECT JSON_ARRAYAGG(Carrier)
                FROM
                (
                    SELECT DISTINCT Carrier
                    FROM
                    (
                        SELECT TRIM(COALESCE(ISHB.`carrier`, '')) AS Carrier
                        FROM `tabImport Sea House Bill` ISHB
                        WHERE ISHB.`docstatus` = 1

                        UNION ALL

                        SELECT TRIM(COALESCE(IAHB.`airlines`, '')) AS Carrier
                        FROM `tabImport Air House Bill` IAHB
                        WHERE IAHB.`docstatus` = 1

                        UNION ALL

                        SELECT TRIM(COALESCE(ESHB.`shipping_line`, '')) AS Carrier
                        FROM `tabExport Sea House Bill` ESHB
                        WHERE ESHB.`docstatus` = 1

                        UNION ALL

                        SELECT TRIM(COALESCE(EAHB.`airlines`, '')) AS Carrier
                        FROM `tabExport Air House Bill` EAHB
                        WHERE EAHB.`docstatus` = 1

                    ) AS AllCarriers

                    WHERE Carrier <> ''
                      AND (
                            p_search IS NULL
                            OR p_search = ''
                            OR Carrier LIKE CONCAT('%', p_search, '%')
                          )

                    ORDER BY Carrier ASC
                    LIMIT v_offset, v_page_size

                ) AS PaginatedCarriers
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