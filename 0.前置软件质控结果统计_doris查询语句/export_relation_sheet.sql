
/*
*描述： 数据关联一致性查询结果统计，导出Excel模板：qzrj_association_detail.xlsx
*修改日期范围：
* 更新日期：2026-05-25
*/
SELECT
    a.city,
    a.org_code,
    a.org_name,
    a.table_name,
    c.table_comment,
    a.association_table,
    a.association_table_comment,
    a.total_records,
    a.association_records,
    a.association_rate
FROM (
    SELECT
        city, org_code, org_name, table_name,
        'emr_patient_info' AS association_table,
        '患者基本信息表' AS association_table_comment,
        total_records,
        patient_association_violations AS association_records,
        CASE 
            WHEN total_records = 0 THEN 0
            ELSE ROUND(patient_association_violations * 100.0 / total_records, 2)
        END AS association_rate
    FROM (
        SELECT
            b.city,
            b.org_code,
            b.org_name,
            a.table_name,
            a.field_name,
            SUM(a.total_records) AS total_records,
            SUM(a.patient_association_violations) AS patient_association_violations,
            SUM(a.activity_association_violations) AS activity_association_violations,
            SUM(a.master_association_violations) AS master_association_violations
        FROM cdc_emr_quality_check_association a
        JOIN ods_tem_cdc_v211_org_code_new b ON a.org_id = b.org_code 
        WHERE b.is_516 = '是'
            AND a.check_time >= UNIX_TIMESTAMP('2026-05-25 00:00:00') * 1000
            AND a.check_time < UNIX_TIMESTAMP('2026-05-26 00:00:00') * 1000
        GROUP BY b.city, b.org_code, b.org_name, a.table_name, a.field_name
    ) tmp_list
    WHERE table_name <> 'emr_patient_info' AND field_name IN ('1', '1,2')
    
    UNION ALL
    
    SELECT
        city, org_code, org_name, table_name,
        'emr_activity_info' AS association_table,
        '诊疗活动信息表' AS association_table_comment,
        total_records,
        activity_association_violations AS association_records,
        CASE 
            WHEN total_records = 0 THEN 0
            ELSE ROUND(activity_association_violations * 100.0 / total_records, 2)
        END AS association_rate
    FROM (
        SELECT
            b.city,
            b.org_code,
            b.org_name,
            a.table_name,
            a.field_name,
            SUM(a.total_records) AS total_records,
            SUM(a.patient_association_violations) AS patient_association_violations,
            SUM(a.activity_association_violations) AS activity_association_violations,
            SUM(a.master_association_violations) AS master_association_violations
        FROM cdc_emr_quality_check_association a
        JOIN ods_tem_cdc_v211_org_code_new b ON a.org_id = b.org_code 
        WHERE b.is_516 = '是'
            AND a.check_time >= UNIX_TIMESTAMP('2026-05-25 00:00:00') * 1000
            AND a.check_time < UNIX_TIMESTAMP('2026-05-26 00:00:00') * 1000
        GROUP BY b.city, b.org_code, b.org_name, a.table_name, a.field_name
    ) tmp_list
    WHERE table_name <> 'emr_activity_info' AND field_name IN ('1', '1,2')
    
    UNION ALL
    
    SELECT
        city, org_code, org_name, table_name,
        CASE table_name
            WHEN 'emr_order_item' THEN 'emr_order'
            WHEN 'emr_ex_lab_item' THEN 'emr_ex_lab'
            WHEN 'emr_ex_clinical_item' THEN 'emr_ex_clinical'
        END AS association_table,
        CASE table_name
            WHEN 'emr_order_item' THEN '医嘱处方'
            WHEN 'emr_ex_lab_item' THEN '检验报告'
            WHEN 'emr_ex_clinical_item' THEN '检查报告'
        END AS association_table_comment,
        total_records,
        master_association_violations AS association_records,
        CASE 
            WHEN total_records = 0 THEN 0
            ELSE ROUND(master_association_violations * 100.0 / total_records, 2)
        END AS association_rate
    FROM (
        SELECT
            b.city,
            b.org_code,
            b.org_name,
            a.table_name,
            a.field_name,
            SUM(a.total_records) AS total_records,
            SUM(a.patient_association_violations) AS patient_association_violations,
            SUM(a.activity_association_violations) AS activity_association_violations,
            SUM(a.master_association_violations) AS master_association_violations
        FROM cdc_emr_quality_check_association a
        JOIN ods_tem_cdc_v211_org_code_new b ON a.org_id = b.org_code 
        WHERE b.is_516 = '是'
            AND FROM_UNIXTIME(a.check_time) >='2026-05-25 00:00:00'
            AND FROM_UNIXTIME(a.check_time) < '2026-05-26 00:00:00'
        GROUP BY b.city, b.org_code, b.org_name, a.table_name, a.field_name
    ) tmp_list
    WHERE field_name = '3'
) a
LEFT JOIN ods_tem_emr_table_list c ON c.table_name = a.table_name
ORDER BY a.city, a.org_code, c.table_seq
LIMIT 50000;