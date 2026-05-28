/****************************************************************
*描述：主诉、现病史明细查询结果统计，导出Excel模板：qzrj_chief_detail.xlsx
*修改日期范围：
*****************************************************************/
with tmp_level_chief as (
select 'emr_outpatient_record' table_name,'门（急）诊病历' table_comment,'present_illness_his' field_name,'现病史' field_comment,'1' column_level from cdc_emr_quality_check limit 1 union all
select 'emr_outpatient_record' table_name,'门（急）诊病历' table_comment,'present_illness_his' field_name,'现病史' field_comment,'1' column_level from cdc_emr_quality_check limit 1 union all
select 'emr_admission_info' table_name,'入院记录' table_comment,'present_illness_his' field_name,'现病史' field_comment,'1' column_level from cdc_emr_quality_check limit 1 union all
select 'emr_outpatient_obs' table_name,'门（急）诊留观记录' table_comment,'present_illness_his' field_name,'现病史' field_comment,'1' column_level from cdc_emr_quality_check limit 1 union all
select 'emr_admission_info' table_name,'入院记录' table_comment,'present_illness_his' field_name,'现病史' field_comment,'1' column_level from cdc_emr_quality_check limit 1 union all
select 'emr_admission_info' table_name,'入院记录' table_comment,'chief_complaint' field_name,'主诉' field_comment,'1' column_level from cdc_emr_quality_check limit 1 union all
select 'emr_outpatient_record' table_name,'门（急）诊病历' table_comment,'chief_complaint' field_name,'主诉' field_comment,'1' column_level from cdc_emr_quality_check limit 1 union all
select 'emr_outpatient_obs' table_name,'门（急）诊留观记录' table_comment,'chief_complaint' field_name,'主诉' field_comment,'1' column_level from cdc_emr_quality_check limit 1 union all
select 'emr_outpatient_record' table_name,'门（急）诊病历' table_comment,'chief_complaint' field_name,'主诉' field_comment,'1' column_level from cdc_emr_quality_check limit 1 union all
select 'emr_activity_info' table_name,'诊疗活动信息' table_comment,'chief_complaint' field_name,'主诉' field_comment,'1' column_level from cdc_emr_quality_check limit 1 union all
select 'emr_admission_info' table_name,'入院记录' table_comment,'chief_complaint' field_name,'主诉' field_comment,'1' column_level from cdc_emr_quality_check limit 1 union all
select 'emr_activity_info' table_name,'诊疗活动信息' table_comment,'chief_complaint' field_name,'主诉' field_comment,'1' column_level from cdc_emr_quality_check limit 1 
),tmp_records as (
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
  and FROM_UNIXTIME(b.check_time / 1000) >='2026-05-25 00:00:00'
  and FROM_UNIXTIME(b.check_time / 1000) <'2026-05-26 00:00:00'
)
select a.city,
a.org_code,
a.org_name,
f.table_name,
c.table_comment,
f.field_name,
c.field_comment,
sum(total_records) total_records,
    sum(null_violations) null_violations,
    sum(notnull_records) notnull_records,
    case when sum(total_records)>0 then 
       round((sum(notnull_records)/sum(total_records))*100,2)
    end  notnull_rate
 from  ods_tem_cdc_v211_org_code_new a ,tmp_records f
  join tmp_level_chief c on c.table_name = f.table_name and c.field_name = f.field_name
  join ods_tem_emr_table_list d on f.table_name = d.table_name
 where a.org_code = f.org_id
 group by a.city, a.org_code, a.org_name, f.table_name, c.table_comment,f.field_name,c.field_comment,d.table_seq
 order by a.city, a.org_code,d.table_seq
 limit 50000;