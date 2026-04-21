-- 1. 常量表改用标准 SELECT 字面量 + UNION ALL（零基表扫描）
WITH tmp_table_list AS (
    select table_name,'患者基本信息表'table_comment,'1' table_level, 1 table_seq  from cdc_emr_quality_check where table_name='emr_patient_info' limit 1 union all
    select table_name,'诊疗活动信息表' table_comment,'1'  table_level,2 table_seq  from cdc_emr_quality_check where table_name='emr_activity_info' limit 1 union all
    select table_name,'传染病报告卡' table_comment,'1'  table_level ,3 table_seq  from cdc_emr_quality_check where table_name='emr_inf_report' limit 1 union all
    select table_name,'检验报告' table_comment,'2'  table_level ,13 table_seq from cdc_emr_quality_check where table_name='emr_ex_lab' limit 1 union all
    select table_name,'检验报告项目' table_comment,'2'  table_level ,14 table_seq  from cdc_emr_quality_check where table_name='emr_ex_lab_item' limit 1 union all
    select table_name,'门（急）诊病历' table_comment,'3'  table_level , 4 table_seq from cdc_emr_quality_check where table_name='emr_outpatient_record' limit 1 union all
    select table_name,'门（急）诊留观记录' table_comment,'3'  table_level, 5 table_seq  from cdc_emr_quality_check where table_name='emr_outpatient_obs' limit 1 union all
    select table_name,'入院记录' table_comment,'3'  table_level,6 table_seq  from cdc_emr_quality_check where table_name='emr_admission_info' limit 1 union all
    select table_name,'住院首次病程记录' table_comment,'3'  table_level,7 table_seq  from cdc_emr_quality_check where table_name='emr_first_course' limit 1 union all
    select table_name,'住院日常病程记录' table_comment,'3'  table_level, 8 table_seq  from cdc_emr_quality_check where table_name='emr_daily_course' limit 1 union all
    select table_name,'住院病案首页' table_comment,'3'  table_level,9 table_seq  from cdc_emr_quality_check where table_name='emr_admission_record' limit 1 union all
    select table_name,'出院记录' table_comment,'3'  table_level,10 table_seq  from cdc_emr_quality_check where table_name='emr_discharge_info' limit 1 union all
    select table_name,'检查报告' table_comment,'3'  table_level,11 table_seq  from cdc_emr_quality_check where table_name='emr_ex_clinical' limit 1 union all
    select table_name,'检查报告项目' table_comment,'3'  table_level,12 table_seq  from cdc_emr_quality_check where table_name='emr_ex_clinical_item' limit 1 union all
    select table_name,'医嘱处方信息' table_comment,'3'  table_level,15 table_seq  from cdc_emr_quality_check where table_name='emr_order' limit 1 union all
    select table_name,'医嘱处方条目' table_comment,'3'  table_level,16 table_seq  from cdc_emr_quality_check where table_name='emr_order_item' limit 1 union all
    select table_name,'死亡信息' table_comment,'3'  table_level,17 table_seq  from cdc_emr_quality_check where table_name='emr_death_info' limit 1 union all
    select table_name,'生命体征护理记录单' table_comment,'3'  table_level,18 table_seq  from cdc_emr_quality_check where table_name='emr_vital_signs_record' limit 1
),

-- 2. 聚合中间层：优化时间过滤写法（常量计算 + 支持索引下推）
tmp_list AS (
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
    JOIN (select distinct city,org_code,org_name from cdc_mdm_org_code where is_516='是') b ON a.org_id = b.org_code
    WHERE 
        -- 函数移到常量侧，让 check_time 参与索引/ZoneMap 过滤
        a.check_time >= UNIX_TIMESTAMP('2026-04-13 00:00:00') * 1000
        AND a.check_time <  UNIX_TIMESTAMP('2026-04-14 00:00:00') * 1000
    GROUP BY b.city, b.org_code, b.org_name, a.table_name, a.field_name
)

-- 3. 主查询：一次扫描 tmp_list 产出所有分支，避免重复扫描
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
    -- 分支 1：患者关联（field_name IN '1','1,2'）
    SELECT
        city, org_code,
         org_name, 
        table_name,
        'emr_patient_info' AS association_table,
        '患者基本信息表' AS association_table_comment,
        total_records,
        patient_association_violations AS association_records,
        ROUND(patient_association_violations / NULLIF(total_records, 0) * 100, 2) AS association_rate
    FROM tmp_list
    WHERE field_name IN ('1', '1,2')
    
    UNION ALL
    
    -- 分支 2：诊疗活动关联（field_name IN '1','1,2'）
    SELECT
        city, org_code, org_name, table_name,
        'emr_activity_info' AS association_table,
        '诊疗活动信息表' AS association_table_comment,
        total_records,
        activity_association_violations AS association_records,
        ROUND(activity_association_violations / NULLIF(total_records, 0) * 100, 2) AS association_rate
    FROM tmp_list
    WHERE field_name IN ('1', '1,2')
    
    UNION ALL
    
    -- 分支 3：主表关联（field_name = '3'）
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
        ROUND(master_association_violations / NULLIF(total_records, 0) * 100, 2) AS association_rate
    FROM tmp_list
    WHERE field_name = '3'
) a
LEFT JOIN tmp_table_list c ON c.table_name = a.table_name
ORDER BY a.city, a.org_code, c.table_seq
LIMIT 50000;