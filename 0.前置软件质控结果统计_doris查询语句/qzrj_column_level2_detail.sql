/********************************************************************************
*描述： 重要字段建议填查询结果统计，导出Excel模板：qzrj_column_level_2_detail.xlsx
*修改日期范围：
*********************************************************************************/
select 
 c.city,
    a.org_id,
    c.org_name,
   a.table_name,
    b.table_comment,
     SUM(a.total_records) AS total_records,
    SUM(a.null_violations) AS null_violations,
    case when SUM(a.total_records) > 0 then 
    (SUM(a.total_records)-SUM(a.null_violations)) 
    end AS notnull_records,
    CASE 
        WHEN SUM(a.total_records) > 0 THEN 
            ROUND(((SUM(a.total_records) - SUM(a.null_violations)) / SUM(a.total_records)) * 100, 2)
    END AS notnull_rate
from cdc_emr_quality_check a,
ods_tem_emr_table_field_list b,
ods_tem_cdc_v211_org_code_new c 
where a.table_name = b.table_name 
and a.field_name = b.field_name 
and a.org_id = c.org_code
and c.is_516 = '是'
and a.check_type IN ('1', '2', '3')
AND FROM_UNIXTIME(a.check_time/1000) >='2026-05-24 00:00:00' 
AND FROM_UNIXTIME(a.check_time/1000) <'2026-05-25 00:00:00'
and b.column_level = '2'
GROUP BY c.city, a.org_id, c.org_name, a.table_name, b.table_comment, b.table_seq
ORDER BY c.city, a.org_id, b.table_seq
LIMIT 10000;