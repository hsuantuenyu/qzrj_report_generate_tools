/**************************************
*@描述：关键字段建议填
***************************************/
with tmp_level as (
  select 'emr_inf_report' table_name,'传染病报告卡' table_comment,'bs_transmission_name' field_name,'感染途径名称' field_comment,'2' column_level from cdc_emr_quality_check limit 1 union all
select 'emr_inf_report' table_name,'传染病报告卡' table_comment,'serverity_code' field_name,'是否重症代码' field_comment,'2' column_level from cdc_emr_quality_check limit 1 union all
select 'emr_inf_report' table_name,'传染病报告卡' table_comment,'serverity_name' field_name,'是否重症名称' field_comment,'2' column_level from cdc_emr_quality_check limit 1 union all
select 'emr_inf_report' table_name,'传染病报告卡' table_comment,'ncv_severity_name' field_name,'新冠临床严重程度名称' field_comment,'2' column_level from cdc_emr_quality_check limit 1 union all
select 'emr_inf_report' table_name,'传染病报告卡' table_comment,'permanent_addr_name' field_name,'户籍地址名称' field_comment,'2' column_level from cdc_emr_quality_check limit 1 union all
select 'emr_inf_report' table_name,'传染病报告卡' table_comment,'ncv_severity_code' field_name,'新冠临床严重程度代码' field_comment,'2' column_level from cdc_emr_quality_check limit 1 union all
select 'emr_patient_info' table_name,'患者基本信息' table_comment,'nultitude_type_code' field_name,'人群分类代码' field_comment,'2' column_level from cdc_emr_quality_check limit 1 union all
select 'emr_patient_info' table_name,'患者基本信息' table_comment,'nultitude_type_name' field_name,'人群分类名称' field_comment,'2' column_level from cdc_emr_quality_check limit 1 union all
select 'emr_inf_report' table_name,'传染病报告卡' table_comment,'discovery_mode_name' field_name,'发现方式名称' field_comment,'2' column_level from cdc_emr_quality_check limit 1 union all
select 'emr_patient_info' table_name,'患者基本信息' table_comment,'education_code' field_name,'学历代码' field_comment,'2' column_level from cdc_emr_quality_check limit 1 union all
select 'emr_order' table_name,'医嘱处方信息' table_comment,'prescription_validity_days' field_name,'处方有效天数' field_comment,'2' column_level from cdc_emr_quality_check limit 1 union all
select 'emr_inf_report' table_name,'传染病报告卡' table_comment,'afp_doctor_date' field_name,'就诊日期' field_comment,'2' column_level from cdc_emr_quality_check limit 1 union all
select 'emr_inf_report' table_name,'传染病报告卡' table_comment,'education_code' field_name,'学历代码' field_comment,'2' column_level from cdc_emr_quality_check limit 1 union all
select 'emr_order' table_name,'医嘱处方信息' table_comment,'excute_date' field_name,'医嘱处方执行日期' field_comment,'2' column_level from cdc_emr_quality_check limit 1 union all
select 'emr_order_item' table_name,'医嘱处方条目' table_comment,'drug_dosage_total' field_name,'药物使用总剂量' field_comment,'2' column_level from cdc_emr_quality_check limit 1
),
tmp_table_list as (
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
tmp_org_list as 
(select distinct city,org_code,org_name from cdc_mdm_org_code where is_516='是')
,tmp_records as (
    select 
  b.org_id,
  b.table_name,
  b.field_name,
  b.check_type,
  b.total_records,
  b.null_violations,
 case when total_records > 0 then total_records - null_violations end as notnull_records
 from cdc_emr_quality_check b
where  b.check_type in('1', '2', '3')
  and FROM_UNIXTIME(b.check_time / 1000) >='2026-04-13 00:00:00'
  and FROM_UNIXTIME(b.check_time / 1000) <='2026-04-13 00:00:00'
)
select a.city,
a.org_code,
a.org_name,
f.table_name,
c.table_comment,
sum(total_records) total_records,
    sum(null_violations) null_violations,
    sum(notnull_records) notnull_records,
    case when sum(total_records)>0 then 
       round((sum(notnull_records)/sum(total_records))*100,2)
    end  notnull_rate
 from  tmp_org_list a ,tmp_records f
  join tmp_level c on c.table_name = f.table_name and c.field_name = f.field_name
  left join tmp_table_list d on f.table_name = d.table_name
 where a.org_code = f.org_id
 group by a.city, a.org_code, a.org_name, f.table_name, c.table_comment,d.table_seq
 order by a.city, a.org_code,d.table_seq
 limit 30000