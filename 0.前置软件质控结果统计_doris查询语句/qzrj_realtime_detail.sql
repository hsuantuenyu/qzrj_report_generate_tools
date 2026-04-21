WITH tmp_table_list as (
select table_name,'患者基本信息表' table_comment,'1' table_level, 1 table_seq  from cdc_emr_quality_check where table_name='emr_patient_info' limit 1 union all
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

),tmp_records as 
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
      cdc_emr_quality_check a,
      (select distinct city,org_code,org_name from cdc_mdm_org_code where is_516='是') b
    where
      a.org_id = b.org_code
      and a.check_type = '4'
      and FROM_UNIXTIME(a.check_time / 1000) >= '2026-04-13 00:00:00'
      and FROM_UNIXTIME(a.check_time / 1000) <= '2026-04-13 00:00:00'
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
      cdc_emr_quality_check a,
     (select distinct city,org_code,org_name from cdc_mdm_org_code where is_516='是') b
    where
      a.org_id = b.org_code
      and a.check_type = '4'
      and FROM_UNIXTIME(a.check_time / 1000) >= '2026-04-13 00:00:00'
      and FROM_UNIXTIME(a.check_time / 1000) <= '2026-04-13 00:00:00'
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
      (select distinct city,org_code,org_name from cdc_mdm_org_code where is_516='是') b
    where
      a.org_id = b.org_code
      and a.check_type = '4'
      and FROM_UNIXTIME(a.check_time / 1000) >= '2026-04-13 00:00:00'
      and FROM_UNIXTIME(a.check_time / 1000) <= '2026-04-13 00:00:00'
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
 FROM tmp_records a,
 tmp_table_list b 
 where a.table_name = b.table_name
--  and a.org_code='420111032'
 group by a.city,a.org_code,a.org_name,a.table_name,b.table_comment,b.table_level,b.table_seq
order by a.city,a.org_code,b.table_seq
limit 10000