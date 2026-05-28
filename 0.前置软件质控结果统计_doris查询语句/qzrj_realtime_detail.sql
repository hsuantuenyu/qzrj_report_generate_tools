/**********************************************************************
*描述：表实时性查询结果统计：导出Excel文件模板 qzrj_realtime_detail.xlsx
*修改查询日期范围：
**********************************************************************/
WITH tmp_records as 
(
    select
      b.city,
      b.org_code,
      b.org_name,
      a.table_name,
      a.field_name,
      a.check_type,
      sum(a.total_records) total_records,
      sum(
        CAST(
          CEILING(a.total_records * (a.check_type_seven / 100)) as INTEGER
        )
      ) compliance_records
    from
      cdc_emr_quality_check a,ods_tem_cdc_v211_org_code_new b
    where
      a.org_id = b.org_code
      and  b.is_516='是' 
      and a.check_type = '4'
      and FROM_UNIXTIME(a.check_time / 1000) >= '2026-05-25 00:00:00'
      and FROM_UNIXTIME(a.check_time / 1000) < '2026-05-26 00:00:00'
      and field_name = 'date_check'
      and table_name in('emr_patient_info','emr_activity_info','emr_inf_report')
    group by
      b.city,
      b.org_code,
      b.org_name,
      a.table_name,
      a.field_name,
      a.check_type
    union all
    select
      b.city,
      b.org_code,
      b.org_name,
      a.table_name,
      a.field_name,
      a.check_type,
      sum(a.total_records) total_records,
      sum(
        CAST(
          CEILING(a.total_records * (a.check_type_nine / 100)) AS INTEGER
        )
      ) AS compliance_records
    from
      cdc_emr_quality_check a,ods_tem_cdc_v211_org_code_new b
    where
      a.org_id = b.org_code
      and b.is_516='是'
      and a.check_type = '4'
      and FROM_UNIXTIME(a.check_time / 1000) >= '2026-05-25 00:00:00'
      and FROM_UNIXTIME(a.check_time / 1000) < '2026-05-26 00:00:00'
      and field_name = 'date_check'
      and table_name in('emr_ex_lab','emr_ex_lab_item')
    group by
      b.city,
      b.org_code,
      b.org_name,
      a.table_name,
      a.field_name,
      a.check_type
    union all
    select
      b.city,
      b.org_code,
      b.org_name,
      a.table_name,
      a.field_name,
      a.check_type,
      sum(a.total_records) total_records,
      sum(
        CAST(
          CEILING(a.total_records * (a.check_type_ten / 100)) AS INTEGER
        )
      ) AS compliance_records
    from
      cdc_emr_quality_check a,
       ods_tem_cdc_v211_org_code_new b
    where
      a.org_id = b.org_code
      and b.is_516='是'
      and a.check_type = '4'
      and FROM_UNIXTIME(a.check_time / 1000) >= '2026-05-25 00:00:00'
      and FROM_UNIXTIME(a.check_time / 1000) < '2026-05-26 00:00:00'
      and field_name = 'date_check'
      and table_name in('emr_outpatient_record','emr_outpatient_obs','emr_admission_info','emr_first_course','emr_daily_course','emr_admission_record','emr_discharge_info','emr_ex_clinical','emr_ex_clinical_item','emr_order','emr_order_item','emr_death_info','emr_vital_signs_record')
    group by
      b.city,
      b.org_code,
      b.org_name,
      a.table_name,
      a.field_name,
      a.check_type
  )
SELECT a.city,
a.org_code,
a.org_name,
a.table_name,
b.table_comment,
case b.table_level 
when '1' then '实时表' 
when '2' then '2小时内'
when '3' then 'T+0内'
end table_type,
sum(a.total_records) total_records,
sum(a.compliance_records) compliance_records,
case when sum(a.total_records) > 0 then 
round((sum(a.compliance_records)/sum(a.total_records))*100,2) end compliance_rate,
case b.table_level 
when '1' then '1'  
end table_flag
 FROM tmp_records a,ods_tem_emr_table_list b 
 where a.table_name = b.table_name
--  and a.org_code='420111032'
 group by a.city,a.org_code,a.org_name,a.table_name,b.table_comment,b.table_level,b.table_seq
order by a.city,a.org_code,b.table_seq
limit 10000;