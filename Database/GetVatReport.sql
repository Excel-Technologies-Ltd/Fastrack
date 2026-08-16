DELIMITER $$

DROP PROCEDURE IF EXISTS GetVatReport$$

CREATE PROCEDURE `GetVatReport`(
    -- Date Parameters
    IN p_start_date DATE,
    IN p_end_date DATE,
    
    -- Filter Parameters (NULL = get all)
    IN p_import_export VARCHAR(20),
    IN p_hbl_type VARCHAR(50),
    IN p_carrier VARCHAR(100),
    IN p_sales_person VARCHAR(100),
    IN p_shipper_name VARCHAR(200),
    IN p_customer_name VARCHAR(200),
    IN p_agent_name VARCHAR(200),
    IN p_mbl_consignee VARCHAR(200),
    IN p_notify_party VARCHAR(200),
    IN p_lc_no VARCHAR(100),
    IN p_mbl_no VARCHAR(100),
    IN p_hbl_no VARCHAR(100),
    IN p_inco_term VARCHAR(50)
)
BEGIN
    -- Declare variables for date filtering
    DECLARE v_start_date DATE;
    DECLARE v_end_date DATE;
    
    -- Set default date range if NULL
    IF p_start_date IS NULL THEN
        SET v_start_date = '2000-01-01';
    ELSE
        SET v_start_date = p_start_date;
    END IF;
    
    IF p_end_date IS NULL THEN
        SET v_end_date = '2099-12-31';
    ELSE
        SET v_end_date = p_end_date;
    END IF;

    -- Common Table Expressions
    WITH FSIAggregated AS (
        SELECT
            FSI.`parent`,
            SUM(CASE
                WHEN FSI.`item_code` IN ('Ocean Freight', 'Air Freight')
                THEN COALESCE(FSI.`base_net_amount`, 0)
                ELSE 0
            END) AS `Freight Charge BDT`,
            SUM(CASE
                WHEN FSI.`item_code` IN ('Ocean Freight', 'Air Freight')
                THEN COALESCE(FSI.`total_price`, 0)
                ELSE 0
            END) AS `Freight Charge USD`,
            SUM(CASE
                WHEN FSI.`item_code` = 'Service Commission'
                THEN COALESCE(FSI.`base_net_amount`, 0)
                ELSE 0
            END) AS `Service Commission BDT`,
            SUM(CASE
                WHEN FSI.`item_code` = 'Service Commission'
                THEN COALESCE(FSI.`total_price`, 0)
                ELSE 0
            END) AS `Service Commission USD`,
            SUM(CASE
                WHEN FSI.`item_code` = 'NOC Fee'
                THEN COALESCE(FSI.`base_net_amount`, 0)
                ELSE 0
            END) AS `NOC BDT`,
            SUM(CASE
                WHEN FSI.`item_code` = 'NOC Fee'
                THEN COALESCE(FSI.`total_price`, 0)
                ELSE 0
            END) AS `NOC USD`,
            SUM(CASE
                WHEN FSI.`item_code` NOT IN ('Ocean Freight', 'Air Freight', 'Service Commission', 'NOC Fee')
                THEN COALESCE(FSI.`base_net_amount`, 0)
                ELSE 0
            END) AS `Others Income BDT`,
            SUM(CASE
                WHEN FSI.`item_code` NOT IN ('Ocean Freight', 'Air Freight', 'Service Commission', 'NOC Fee')
                THEN COALESCE(FSI.`total_price`, 0)
                ELSE 0
            END) AS `Others Income USD`
        FROM `tabFastrack Sales Invoice` FSI
        GROUP BY FSI.`parent`
    ), 
    VATAggregated AS (
        SELECT
            VL.`parent`,
            SUM(COALESCE(VL.`vat_amount_bdt`, 0)) AS `VAT BDT`,
            SUM(COALESCE(VL.`vat_amount_usd`, 0)) AS `VAT USD`
        FROM `tabVAT List` VL
        GROUP BY VL.`parent`
    ),
    ImportSeaHouseBill AS (
        SELECT
            'Import' AS `Import/Export`,
            'Import Sea House Bill' AS `HBL Type`,
            COALESCE(ISHB.`carrier`, '') AS Carrier,
            COALESCE(ISHB.`sales_person`, '') AS `Sales Person`,
            COALESCE(ISHB.`hbl_shipper`, '') AS `Shipper Name`,
            COALESCE(ISHB.`customer`, '') AS `Customer Name`,
            COALESCE(ISHB.`agent_name`, '') AS `Agent Name`,
            COALESCE(ISHB.`notify_to`, '') AS `Notify Party`,
            COALESCE(IMB.`consignee`, '') AS `MBL Consignee`,
            COALESCE(ISHB.`lc`, '') AS `L/C No.`,
            COALESCE(ISHB.`lc_date`, '') AS `L/C Date`,
            COALESCE(ISHB.`mbl_no`, '') AS `MBL No.`,
            COALESCE(ISHB.`hbl_id`, '') AS `HBL No.`,
            COALESCE(ISHB.`hbl_etd`, '') AS ETD,
            COALESCE(ISHB.`eta`, '') AS ETA,
            COALESCE(FSI.`Freight Charge BDT`, 0) AS `Freight Charge BDT`,
            COALESCE(FSI.`Freight Charge USD`, 0) AS `Freight Charge USD`,
            COALESCE(FSI.`Service Commission BDT`, 0) AS `Service Commission BDT`,
            COALESCE(FSI.`Service Commission USD`, 0) AS `Service Commission USD`,
            COALESCE(FSI.`NOC BDT`, 0) AS `NOC BDT`,
            COALESCE(FSI.`NOC USD`, 0) AS `NOC USD`,
            COALESCE(FSI.`Others Income BDT`, 0) AS `Others Income BDT`,
            COALESCE(FSI.`Others Income USD`, 0) AS `Others Income USD`, 
            COALESCE(VL.`VAT BDT`, 0) AS `VAT (BDT)`, 
            COALESCE(VL.`VAT USD`, 0) AS `VAT (USD)`, 
            COALESCE(ISHB.`inco_term`, '') AS `Inco Term` 
        FROM 
            `tabImport Sea House Bill` ISHB 
            LEFT JOIN `tabImport Sea Master Bill` IMB ON ISHB.`mbl_no` = IMB.`mbl_no` 
            LEFT JOIN FSIAggregated FSI ON ISHB.`name` = FSI.`parent` 
            LEFT JOIN VATAggregated VL ON ISHB.`name` = VL.`parent` 
        WHERE 
            ISHB.`hbl_etd` >= v_start_date 
            AND ISHB.`hbl_etd` < DATE_ADD(v_end_date, INTERVAL 1 DAY)
            AND ISHB.`docstatus` = 1
    ),
    ImportAirHouseBill AS (
        SELECT
            'Import' AS `Import/Export`,
            'Import Air House Bill' AS `HBL Type`,
            COALESCE(IAHB.`airlines`, '') AS Carrier,
            COALESCE(IAHB.`sales_person`, '') AS `Sales Person`,
            COALESCE(IAHB.`shipper`, '') AS `Shipper Name`,
            COALESCE(IAHB.`customer`, '') AS `Customer Name`,
            COALESCE(IAHB.`agent`, '') AS `Agent Name`,
            COALESCE(IAHB.`notify_party`, '') AS `Notify Party`,
            COALESCE(IMB.`consignee`, '') AS `MBL Consignee`,
            COALESCE(IAHB.`lc_number`, '') AS `L/C No.`,
            COALESCE(IAHB.`lc_date`, '') AS `L/C Date`,
            COALESCE(IAHB.`mbl_no`, '') AS `MBL No.`,
            COALESCE(IAHB.`hbl_no`, '') AS `HBL No.`,
            IAHB.`flight_date` AS ETD,
            IAHB.`flight_date` AS ETA,
            COALESCE(FSI.`Freight Charge BDT`, 0) AS `Freight Charge BDT`,
            COALESCE(FSI.`Freight Charge USD`, 0) AS `Freight Charge USD`,
            COALESCE(FSI.`Service Commission BDT`, 0) AS `Service Commission BDT`,
            COALESCE(FSI.`Service Commission USD`, 0) AS `Service Commission USD`,
            COALESCE(FSI.`NOC BDT`, 0) AS `NOC BDT`,
            COALESCE(FSI.`NOC USD`, 0) AS `NOC USD`,
            COALESCE(FSI.`Others Income BDT`, 0) AS `Others Income BDT`, 
            COALESCE(FSI.`Others Income USD`, 0) AS `Others Income USD`,
            COALESCE(VL.`VAT BDT`, 0) AS `VAT (BDT)`,
            COALESCE(VL.`VAT USD`, 0) AS `VAT (USD)`,
            COALESCE(IAHB.`inco_term`, '') AS `Inco Term`
        FROM 
            `tabImport Air House Bill` IAHB
            LEFT JOIN `tabImport Air Master Bill` IMB ON IAHB.`mbl_no` = IMB.`mbl_no`
            LEFT JOIN FSIAggregated FSI ON IAHB.`name` = FSI.`parent`
            LEFT JOIN VATAggregated VL ON IAHB.`name` = VL.`parent` 
        WHERE 
            IAHB.`flight_date` >= v_start_date 
            AND IAHB.`flight_date` < DATE_ADD(v_end_date, INTERVAL 1 DAY)
            AND IAHB.`docstatus` = 1
    ),
    ImportD2DBill AS (
        SELECT
            'Import' AS `Import/Export`,
            'Import D2D Bill' AS `HBL Type`,
            '' AS Carrier,
            COALESCE(ID2D.`sales_person`, '') AS `Sales Person`,
            COALESCE(ID2D.`shipper`, '') AS `Shipper Name`,
            COALESCE(ID2D.`customer`, '') AS `Customer Name`,
            COALESCE(ID2D.`agent`, '') AS `Agent Name`,
            COALESCE(ID2D.`notify_party`, '') AS `Notify Party`,
            COALESCE(ID2D.`consignee`, '') AS `MBL Consignee`,
            COALESCE(ID2D.`lc_number`, '') AS `L/C No.`,
            COALESCE(ID2D.`lc_date`, '') AS `L/C Date`,
            COALESCE(ID2D.`mbl_no`, '') AS `MBL No.`,
            COALESCE(ID2D.`hbl_no`, '') AS `HBL No.`,
            COALESCE(ID2D.`etd`, '') AS ETD,
            COALESCE(ID2D.`eta`, '') AS ETA,
            COALESCE(FSI.`Freight Charge BDT`, 0) AS `Freight Charge BDT`, 
            COALESCE(FSI.`Freight Charge USD`, 0) AS `Freight Charge USD`, 
            COALESCE(FSI.`Service Commission BDT`, 0) AS `Service Commission BDT`, 
            COALESCE(FSI.`Service Commission USD`, 0) AS `Service Commission USD`, 
            COALESCE(FSI.`NOC BDT`, 0) AS `NOC BDT`,
            COALESCE(FSI.`NOC USD`, 0) AS `NOC USD`,
            COALESCE(FSI.`Others Income BDT`, 0) AS `Others Income BDT`,
            COALESCE(FSI.`Others Income USD`, 0) AS `Others Income USD`,
            COALESCE(VL.`VAT BDT`, 0) AS `VAT (BDT)`,
            COALESCE(VL.`VAT USD`, 0) AS `VAT (USD)`,
            '' AS `Inco Term`
        FROM 
            `tabImport D2D Bill` ID2D
            LEFT JOIN FSIAggregated FSI ON ID2D.`name` = FSI.`parent` 
            LEFT JOIN VATAggregated VL ON ID2D.`name` = VL.`parent` 
        WHERE 
            ID2D.`etd` >= v_start_date 
            AND ID2D.`etd` < DATE_ADD(v_end_date, INTERVAL 1 DAY)
            AND ID2D.`docstatus` = 1
    ),
    ExportSeaHouseBill AS (
        SELECT
            'Export' AS `Import/Export`,
            'Export Sea House Bill' AS `HBL Type`,
            COALESCE(ESHB.`shipping_line`, '') AS Carrier,
            COALESCE(ESHB.`sales_person`, '') AS `Sales Person`,
            COALESCE(ESHB.`hbl_shipper`, '') AS `Shipper Name`,
            '' AS `Customer Name`,
            COALESCE(ESHB.`delivery_agent`, '') AS `Agent Name`,
            COALESCE(ESHB.`notify_to`, '') AS `Notify Party`, 
            '' AS `MBL Consignee`, 
            COALESCE(ESHB.`lc_no`, '') AS `L/C No.`, 
            COALESCE(ESHB.`lc_date`, '') AS `L/C Date`, 
            COALESCE(ESHB.`mbl_no`, '') AS `MBL No.`, 
            COALESCE(ESHB.`hbl_no`, '') AS `HBL No.`, 
            COALESCE(ESHB.`etd`, '') AS ETD, 
            COALESCE(ESHB.`eta`, '') AS ETA, 
            COALESCE(FSI.`Freight Charge BDT`, 0) AS `Freight Charge BDT`, 
            COALESCE(FSI.`Freight Charge USD`, 0) AS `Freight Charge USD`, 
            COALESCE(FSI.`Service Commission BDT`, 0) AS `Service Commission BDT`, 
            COALESCE(FSI.`Service Commission USD`, 0) AS `Service Commission USD`, 
            COALESCE(FSI.`NOC BDT`, 0) AS `NOC BDT`, 
            COALESCE(FSI.`NOC USD`, 0) AS `NOC USD`, 
            COALESCE(FSI.`Others Income BDT`, 0) AS `Others Income BDT`, 
            COALESCE(FSI.`Others Income USD`, 0) AS `Others Income USD`, 
            COALESCE(VL.`VAT BDT`, 0) AS `VAT (BDT)`, 
            COALESCE(VL.`VAT USD`, 0) AS `VAT (USD)`, 
            COALESCE(ESHB.`inco_term`, '') AS `Inco Term` 
        FROM 
            `tabExport Sea House Bill` ESHB
            LEFT JOIN FSIAggregated FSI ON ESHB.`name` = FSI.`parent`
            LEFT JOIN VATAggregated VL ON ESHB.`name` = VL.`parent` 
        WHERE 
            ESHB.`etd` >= v_start_date 
            AND ESHB.`etd` < DATE_ADD(v_end_date, INTERVAL 1 DAY)
            AND ESHB.`docstatus` = 1
    ),
    ExportAirHouseBill AS (
        SELECT
            'Export' AS `Import/Export`,
            'Export Air House Bill' AS `HBL Type`,
            COALESCE(EAHB.`airlines`, '') AS Carrier,
            COALESCE(EAHB.`sales_person`, '') AS `Sales Person`,
            COALESCE(EAHB.`shipper`, '') AS `Shipper Name`,
            '' AS `Customer Name`,
            COALESCE(EAHB.`agent`, '') AS `Agent Name`,
            COALESCE(EAHB.`notify_party`, '') AS `Notify Party`,
            '' AS `MBL Consignee`,
            COALESCE(EAHB.`lc_number`, '') AS `L/C No.`,
            COALESCE(EAHB.`lc_date`, '') AS `L/C Date`,
            COALESCE(EAHB.`mbl_no`, '') AS `MBL No.`,
            COALESCE(EAHB.`hbl_no`, '') AS `HBL No.`,
            COALESCE(EAHB.`flight_date`, '') AS ETD,
            COALESCE(EAHB.`flight_date`, '') AS ETA,
            COALESCE(FSI.`Freight Charge BDT`, 0) AS `Freight Charge BDT`,
            COALESCE(FSI.`Freight Charge USD`, 0) AS `Freight Charge USD`,
            COALESCE(FSI.`Service Commission BDT`, 0) AS `Service Commission BDT`,
            COALESCE(FSI.`Service Commission USD`, 0) AS `Service Commission USD`,
            COALESCE(FSI.`NOC BDT`, 0) AS `NOC BDT`,
            COALESCE(FSI.`NOC USD`, 0) AS `NOC USD`,
            COALESCE(FSI.`Others Income BDT`, 0) AS `Others Income BDT`,
            COALESCE(FSI.`Others Income USD`, 0) AS `Others Income USD`,
            COALESCE(VL.`VAT BDT`, 0) AS `VAT (BDT)`,
            COALESCE(VL.`VAT USD`, 0) AS `VAT (USD)`,
            COALESCE(EAHB.`inco_term`, '') AS `Inco Term`
        FROM 
            `tabExport Air House Bill` EAHB
            LEFT JOIN FSIAggregated FSI ON EAHB.`name` = FSI.`parent`
            LEFT JOIN VATAggregated VL ON EAHB.`name` = VL.`parent`
        WHERE 
            EAHB.`flight_date` >= v_start_date 
            AND EAHB.`flight_date` < DATE_ADD(v_end_date, INTERVAL 1 DAY)
            AND EAHB.`docstatus` = 1
    ),
    ExportD2DBill AS (
        SELECT
            'Export' AS `Import/Export`,
            'Export D2D Bill' AS `HBL Type`,
            '' AS Carrier,
            COALESCE(ED2D.`sales_person`, '') AS `Sales Person`,
            COALESCE(ED2D.`shipper`, '') AS `Shipper Name`,
            COALESCE(ED2D.`customer`, '') AS `Customer Name`,
            COALESCE(ED2D.`agent`, '') AS `Agent Name`, 
            COALESCE(ED2D.`notify_party`, '') AS `Notify Party`,
            COALESCE(ED2D.`consignee`, '') AS `MBL Consignee`, 
            COALESCE(ED2D.`lc_number`, '') AS `L/C No.`,
            COALESCE(ED2D.`lc_date`, '') AS `L/C Date`, 
            COALESCE(ED2D.`mbl_no`, '') AS `MBL No.`, 
            COALESCE(ED2D.`hbl_no`, '') AS `HBL No.`, 
            COALESCE(ED2D.`etd`, '') AS ETD, 
            COALESCE(ED2D.`eta`, '') AS ETA, 
            COALESCE(FSI.`Freight Charge BDT`, 0) AS `Freight Charge BDT`, 
            COALESCE(FSI.`Freight Charge USD`, 0) AS `Freight Charge USD`, 
            COALESCE(FSI.`Service Commission BDT`, 0) AS `Service Commission BDT`, 
            COALESCE(FSI.`Service Commission USD`, 0) AS `Service Commission USD`, 
            COALESCE(FSI.`NOC BDT`, 0) AS `NOC BDT`, 
            COALESCE(FSI.`NOC USD`, 0) AS `NOC USD`, 
            COALESCE(FSI.`Others Income BDT`, 0) AS `Others Income BDT`, 
            COALESCE(FSI.`Others Income USD`, 0) AS `Others Income USD`, 
            COALESCE(VL.`VAT BDT`, 0) AS `VAT (BDT)`, 
            COALESCE(VL.`VAT USD`, 0) AS `VAT (USD)`, 
            '' AS `Inco Term` 
        FROM 
            `tabExport D2D Bill` ED2D
            LEFT JOIN `tabExport D2D Bill` IMB ON ED2D.`mbl_no` = IMB.`mbl_no`
            LEFT JOIN FSIAggregated FSI ON ED2D.`name` = FSI.`parent`
            LEFT JOIN VATAggregated VL ON ED2D.`name` = VL.`parent`
        WHERE 
            ED2D.`etd` >= v_start_date 
            AND ED2D.`etd` < DATE_ADD(v_end_date, INTERVAL 1 DAY)
            AND ED2D.`docstatus` = 1
    ),
    AllBills AS (
        SELECT * FROM ImportSeaHouseBill
        UNION ALL
        SELECT * FROM ImportAirHouseBill
        UNION ALL
        SELECT * FROM ImportD2DBill
        UNION ALL
        SELECT * FROM ExportSeaHouseBill
        UNION ALL
        SELECT * FROM ExportAirHouseBill
        UNION ALL
        SELECT * FROM ExportD2DBill
    )
    -- Final SELECT with dynamic filtering
    SELECT 
        *
    FROM
        AllBills
    WHERE
        (p_import_export IS NULL OR p_import_export = '' OR `Import/Export` = p_import_export)
        AND (p_hbl_type IS NULL OR p_hbl_type = '' OR `HBL Type` = p_hbl_type)
        AND (p_carrier IS NULL OR p_carrier = '' OR Carrier = p_carrier)
        AND (p_sales_person IS NULL OR p_sales_person = '' OR `Sales Person` = p_sales_person)
        AND (p_shipper_name IS NULL OR p_shipper_name = '' OR `Shipper Name` = p_shipper_name)
        AND (p_customer_name IS NULL OR p_customer_name = '' OR `Customer Name` = p_customer_name)
        AND (p_agent_name IS NULL OR p_agent_name = '' OR `Agent Name` = p_agent_name)
        AND (p_mbl_consignee IS NULL OR p_mbl_consignee = '' OR `MBL Consignee` = p_mbl_consignee)
        AND (p_notify_party IS NULL OR p_notify_party = '' OR `Notify Party` = p_notify_party)
        AND (p_lc_no IS NULL OR p_lc_no = '' OR `L/C No.` = p_lc_no)
        AND (p_mbl_no IS NULL OR p_mbl_no = '' OR `MBL No.` = p_mbl_no)
        AND (p_hbl_no IS NULL OR p_hbl_no = '' OR `HBL No.` = p_hbl_no)
        AND (p_inco_term IS NULL OR p_inco_term = '' OR `Inco Term` = p_inco_term)
    ORDER BY
        ETD DESC;
END$$

DELIMITER ;
