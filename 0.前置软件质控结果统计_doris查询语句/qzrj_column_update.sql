with tmp_level_update as (
    select 'emr_patient_info' table_name,'患者基本信息' table_comment,'gender_name' field_name,'性别名称' field_comment,'1' column_level from cdc_emr_quality_check limit 1 union all
select 'emr_patient_info' table_name,'患者基本信息' table_comment,'current_addr_detail' field_name,'现住详细地址' field_comment,'1' column_level from cdc_emr_quality_check limit 1 union all
select 'emr_patient_info' table_name,'患者基本信息' table_comment,'gender_code' field_name,'性别代码' field_comment,'1' column_level from cdc_emr_quality_check limit 1 union all
select 'emr_ex_clinical' table_name,'检查报告' table_comment,'apply_dept_name' field_name,'检查申请科室名称' field_comment,'1' column_level from cdc_emr_quality_check limit 1 union all
select 'emr_patient_info' table_name,'患者基本信息' table_comment,'nation_name' field_name,'民族名称' field_comment,'1' column_level from cdc_emr_quality_check limit 1 union all
select 'emr_ex_lab' table_name,'检验报告' table_comment,'apply_org_code' field_name,'检验申请机构代码' field_comment,'1' column_level from cdc_emr_quality_check limit 1 union all
select 'emr_patient_info' table_name,'患者基本信息' table_comment,'nation_code' field_name,'民族代码' field_comment,'1' column_level from cdc_emr_quality_check limit 1 union all
select 'emr_outpatient_obs' table_name,'门（急）诊留观记录' table_comment,'studies_summary_result' field_name,'辅助检查' field_comment,'1' column_level from cdc_emr_quality_check limit 1 union all
select 'emr_order_item' table_name,'医嘱处方条目' table_comment,'drug_dosage_unit_code' field_name,'药物使用剂量单位代码' field_comment,'1' column_level from cdc_emr_quality_check limit 1 union all
select 'emr_outpatient_record' table_name,'门（急）诊病历' table_comment,'inital_diagnosis_code' field_name,'初诊标志代码' field_comment,'1' column_level from cdc_emr_quality_check limit 1 union all
select 'emr_admission_info' table_name,'入院记录' table_comment,'physical_examination' field_name,'体格检查' field_comment,'1' column_level from cdc_emr_quality_check limit 1 union all
select 'emr_outpatient_record' table_name,'门（急）诊病历' table_comment,'studies_summary_result' field_name,'辅助检查' field_comment,'1' column_level from cdc_emr_quality_check limit 1 union all
select 'emr_outpatient_record' table_name,'门（急）诊病历' table_comment,'present_illness_his' field_name,'现病史' field_comment,'1' column_level from cdc_emr_quality_check limit 1 union all
select 'emr_outpatient_obs' table_name,'门（急）诊留观记录' table_comment,'studies_summary_result' field_name,'辅助检查' field_comment,'1' column_level from cdc_emr_quality_check limit 1 union all
select 'emr_inf_report' table_name,'传染病报告卡' table_comment,'gender_name' field_name,'性别名称' field_comment,'1' column_level from cdc_emr_quality_check limit 1 union all
select 'emr_patient_info' table_name,'患者基本信息' table_comment,'nationality_code' field_name,'国籍/地区代码' field_comment,'1' column_level from cdc_emr_quality_check limit 1 union all
select 'emr_ex_clinical' table_name,'检查报告' table_comment,'examination_subjective_desc' field_name,'检查报告结果-主观提示' field_comment,'1' column_level from cdc_emr_quality_check limit 1 union all
select 'emr_inf_report' table_name,'传染病报告卡' table_comment,'gender_code' field_name,'性别代码' field_comment,'1' column_level from cdc_emr_quality_check limit 1 union all
select 'emr_patient_info' table_name,'患者基本信息' table_comment,'birth_date' field_name,'出生日期' field_comment,'1' column_level from cdc_emr_quality_check limit 1 union all
select 'emr_patient_info' table_name,'患者基本信息' table_comment,'workunit' field_name,'工作单位/学校名称' field_comment,'1' column_level from cdc_emr_quality_check limit 1 union all
select 'emr_outpatient_record' table_name,'门（急）诊病历' table_comment,'present_illness_his' field_name,'现病史' field_comment,'1' column_level from cdc_emr_quality_check limit 1 union all
select 'emr_admission_info' table_name,'入院记录' table_comment,'chief_complaint' field_name,'主诉' field_comment,'1' column_level from cdc_emr_quality_check limit 1 union all
select 'emr_admission_info' table_name,'入院记录' table_comment,'present_illness_his' field_name,'现病史' field_comment,'1' column_level from cdc_emr_quality_check limit 1 union all
select 'emr_discharge_info' table_name,'出院记录' table_comment,'admission_desc' field_name,'入院情况' field_comment,'1' column_level from cdc_emr_quality_check limit 1 union all
select 'emr_outpatient_record' table_name,'门（急）诊病历' table_comment,'chief_complaint' field_name,'主诉' field_comment,'1' column_level from cdc_emr_quality_check limit 1 union all
select 'emr_activity_info' table_name,'诊疗活动信息' table_comment,'physical_examination' field_name,'体格检查' field_comment,'1' column_level from cdc_emr_quality_check limit 1 union all
select 'emr_ex_lab_item' table_name,'检验报告项目' table_comment,'source_examination_result_name' field_name,'院内检验定性结果名称' field_comment,'1' column_level from cdc_emr_quality_check limit 1 union all
select 'emr_patient_info' table_name,'患者基本信息' table_comment,'nationality_name' field_name,'国籍/地区名称' field_comment,'1' column_level from cdc_emr_quality_check limit 1 union all
select 'emr_ex_lab' table_name,'检验报告' table_comment,'apply_dept_code' field_name,'检验申请科室代码' field_comment,'1' column_level from cdc_emr_quality_check limit 1 union all
select 'emr_outpatient_obs' table_name,'门（急）诊留观记录' table_comment,'chief_complaint' field_name,'主诉' field_comment,'1' column_level from cdc_emr_quality_check limit 1 union all
select 'emr_outpatient_obs' table_name,'门（急）诊留观记录' table_comment,'present_illness_his' field_name,'现病史' field_comment,'1' column_level from cdc_emr_quality_check limit 1 union all
select 'emr_outpatient_obs' table_name,'门（急）诊留观记录' table_comment,'physical_examination' field_name,'体格检查' field_comment,'1' column_level from cdc_emr_quality_check limit 1 union all
select 'emr_discharge_info' table_name,'出院记录' table_comment,'admission_diagnosis_code' field_name,'入院诊断编码' field_comment,'1' column_level from cdc_emr_quality_check limit 1 union all
select 'emr_discharge_info' table_name,'出院记录' table_comment,'admission_diagnosis_name' field_name,'入院诊断名称' field_comment,'1' column_level from cdc_emr_quality_check limit 1 union all
select 'emr_ex_clinical_item' table_name,'检查报告项目' table_comment,'item_code' field_name,'检查项目代码' field_comment,'1' column_level from cdc_emr_quality_check limit 1 union all
select 'emr_discharge_info' table_name,'出院记录' table_comment,'disease_progression_code' field_name,'病情转归代码' field_comment,'1' column_level from cdc_emr_quality_check limit 1 union all
select 'emr_ex_clinical' table_name,'检查报告' table_comment,'examination_objective_desc' field_name,'检查报告结果-客观所见' field_comment,'1' column_level from cdc_emr_quality_check limit 1 union all
select 'emr_outpatient_record' table_name,'门（急）诊病历' table_comment,'outpatient_date' field_name,'就诊日期时间' field_comment,'1' column_level from cdc_emr_quality_check limit 1 union all
select 'emr_outpatient_record' table_name,'门（急）诊病历' table_comment,'chief_complaint' field_name,'主诉' field_comment,'1' column_level from cdc_emr_quality_check limit 1 union all
select 'emr_outpatient_record' table_name,'门（急）诊病历' table_comment,'physical_examination' field_name,'体格检查' field_comment,'1' column_level from cdc_emr_quality_check limit 1 union all
select 'emr_activity_info' table_name,'诊疗活动信息' table_comment,'present_illness_his' field_name,'现病史/入院情况' field_comment,'1' column_level from cdc_emr_quality_check limit 1 union all
select 'emr_activity_info' table_name,'诊疗活动信息' table_comment,'studies_summary_result' field_name,'辅助检查' field_comment,'1' column_level from cdc_emr_quality_check limit 1 union all
select 'emr_admission_info' table_name,'入院记录' table_comment,'wm_inital_diagnosis_name' field_name,'初步诊断-西医诊断名称' field_comment,'1' column_level from cdc_emr_quality_check limit 1 union all
select 'emr_patient_info' table_name,'患者基本信息' table_comment,'current_addr_code' field_name,'现住地区代码' field_comment,'1' column_level from cdc_emr_quality_check limit 1 union all
select 'emr_admission_info' table_name,'入院记录' table_comment,'wm_inital_diagnosis_code' field_name,'初步诊断-西医诊断编码' field_comment,'1' column_level from cdc_emr_quality_check limit 1 union all
select 'emr_admission_info' table_name,'入院记录' table_comment,'ward_name' field_name,'病区名称' field_comment,'1' column_level from cdc_emr_quality_check limit 1 union all
select 'emr_admission_record' table_name,'住院病案首页' table_comment,'admission_date' field_name,'入院日期时间' field_comment,'1' column_level from cdc_emr_quality_check limit 1 union all
select 'emr_activity_info' table_name,'诊疗活动信息' table_comment,'physical_examination' field_name,'体格检查' field_comment,'1' column_level from cdc_emr_quality_check limit 1 union all
select 'emr_activity_info' table_name,'诊疗活动信息' table_comment,'chief_complaint' field_name,'主诉' field_comment,'1' column_level from cdc_emr_quality_check limit 1 union all
select 'emr_outpatient_record' table_name,'门（急）诊病历' table_comment,'physical_examination' field_name,'体格检查' field_comment,'1' column_level from cdc_emr_quality_check limit 1 union all
select 'emr_outpatient_record' table_name,'门（急）诊病历' table_comment,'studies_summary_result' field_name,'辅助检查' field_comment,'1' column_level from cdc_emr_quality_check limit 1 union all
select 'emr_admission_info' table_name,'入院记录' table_comment,'physical_examination' field_name,'体格检查' field_comment,'1' column_level from cdc_emr_quality_check limit 1 union all
select 'emr_admission_info' table_name,'入院记录' table_comment,'studies_summary_result' field_name,'辅助检查' field_comment,'1' column_level from cdc_emr_quality_check limit 1 union all
select 'emr_order_item' table_name,'医嘱处方条目' table_comment,'drug_dosage_unit_name' field_name,'药物使用剂量单位名称' field_comment,'1' column_level from cdc_emr_quality_check limit 1 union all
select 'emr_activity_info' table_name,'诊疗活动信息' table_comment,'present_illness_his' field_name,'现病史/入院情况' field_comment,'1' column_level from cdc_emr_quality_check limit 1 union all
select 'emr_activity_info' table_name,'诊疗活动信息' table_comment,'studies_summary_result' field_name,'辅助检查' field_comment,'1' column_level from cdc_emr_quality_check limit 1 union all
select 'emr_ex_clinical' table_name,'检查报告' table_comment,'examination_report_no' field_name,'检查报告单编号' field_comment,'1' column_level from cdc_emr_quality_check limit 1 union all
select 'emr_admission_info' table_name,'入院记录' table_comment,'present_illness_his' field_name,'现病史' field_comment,'1' column_level from cdc_emr_quality_check limit 1 union all
select 'emr_admission_info' table_name,'入院记录' table_comment,'chief_complaint' field_name,'主诉' field_comment,'1' column_level from cdc_emr_quality_check limit 1 union all
select 'emr_ex_clinical_item' table_name,'检查报告项目' table_comment,'item_name' field_name,'检查项目名称' field_comment,'1' column_level from cdc_emr_quality_check limit 1 union all
select 'emr_admission_info' table_name,'入院记录' table_comment,'studies_summary_result' field_name,'辅助检查' field_comment,'1' column_level from cdc_emr_quality_check limit 1 union all
select 'emr_inf_report' table_name,'传染病报告卡' table_comment,'afp_doctor_date' field_name,'就诊日期' field_comment,'2' column_level from cdc_emr_quality_check limit 1 union all
select 'emr_order' table_name,'医嘱处方信息' table_comment,'prescription_issuance_date' field_name,'处方开立日期' field_comment,'1' column_level from cdc_emr_quality_check limit 1 union all
select 'emr_inf_report' table_name,'传染病报告卡' table_comment,'nultitude_type_name' field_name,'人群分类名称' field_comment,'1' column_level from cdc_emr_quality_check limit 1 union all
select 'emr_patient_info' table_name,'患者基本信息' table_comment,'current_addr_name' field_name,'现住地区名称' field_comment,'1' column_level from cdc_emr_quality_check limit 1 union all
select 'emr_ex_lab_item' table_name,'检验报告项目' table_comment,'examination_result_code' field_name,'标化检验定性结果代码' field_comment,'1' column_level from cdc_emr_quality_check limit 1 union all
select 'emr_ex_lab_item' table_name,'检验报告项目' table_comment,'examination_quantification' field_name,'检验定量结果' field_comment,'1' column_level from cdc_emr_quality_check limit 1 union all
select 'emr_ex_clinical' table_name,'检查报告' table_comment,'apply_dept_code' field_name,'检查申请科室代码' field_comment,'1' column_level from cdc_emr_quality_check limit 1 union all
select 'emr_order_item' table_name,'医嘱处方条目' table_comment,'drug_specifications' field_name,'药物规格' field_comment,'1' column_level from cdc_emr_quality_check limit 1 union all
select 'emr_ex_lab' table_name,'检验报告' table_comment,'specimen_sampling_date' field_name,'标本采样日期时间' field_comment,'1' column_level from cdc_emr_quality_check limit 1 union all
select 'emr_admission_info' table_name,'入院记录' table_comment,'admission_date' field_name,'入院日期时间' field_comment,'1' column_level from cdc_emr_quality_check limit 1 union all
select 'emr_activity_info' table_name,'诊疗活动信息' table_comment,'chief_complaint' field_name,'主诉' field_comment,'1' column_level from cdc_emr_quality_check limit 1 union all
select 'emr_ex_lab_item' table_name,'检验报告项目' table_comment,'source_examination_result_code' field_name,'院内检验定性结果代码' field_comment,'1' column_level from cdc_emr_quality_check limit 1 union all
select 'emr_ex_lab_item' table_name,'检验报告项目' table_comment,'examination_result_name' field_name,'标化检验定性结果名称' field_comment,'1' column_level from cdc_emr_quality_check limit 1 union all
select 'emr_discharge_info' table_name,'出院记录' table_comment,'admission_date' field_name,'入院日期时间' field_comment,'1' column_level from cdc_emr_quality_check limit 1 union all
select 'emr_ex_lab' table_name,'检验报告' table_comment,'specimen_category_code' field_name,'标本类别代码' field_comment,'1' column_level from cdc_emr_quality_check limit 1 union all
select 'emr_ex_lab' table_name,'检验报告' table_comment,'specimen_category_name' field_name,'标本类别名称' field_comment,'1' column_level from cdc_emr_quality_check limit 1 union all
select 'emr_ex_lab' table_name,'检验报告' table_comment,'apply_org_name' field_name,'检验申请机构名称' field_comment,'1' column_level from cdc_emr_quality_check limit 1 union all
select 'emr_ex_lab' table_name,'检验报告' table_comment,'apply_dept_name' field_name,'检验申请科室名称' field_comment,'1' column_level from cdc_emr_quality_check limit 1 union all
select 'emr_ex_lab' table_name,'检验报告' table_comment,'specimen_receiving_date' field_name,'接收标本日期时间' field_comment,'1' column_level from cdc_emr_quality_check limit 1 union all
select 'emr_order_item' table_name,'医嘱处方条目' table_comment,'drug_dosage_code' field_name,'单次用药剂量' field_comment,'1' column_level from cdc_emr_quality_check limit 1 union all
select 'emr_inf_report' table_name,'传染病报告卡' table_comment,'place_code' field_name,'输入来源地代码' field_comment,'3' column_level from cdc_emr_quality_check limit 1 union all
select 'emr_inf_report' table_name,'传染病报告卡' table_comment,'foreign_type_code' field_name,'输入病例类型代码' field_comment,'3' column_level from cdc_emr_quality_check limit 1 union all
select 'emr_activity_info' table_name,'诊疗活动信息' table_comment,'disease_name' field_name,'传染病诊断名称' field_comment,'3' column_level from cdc_emr_quality_check limit 1 union all
select 'emr_inf_report' table_name,'传染病报告卡' table_comment,'foreign_type_name' field_name,'输入病例类型名称' field_comment,'3' column_level from cdc_emr_quality_check limit 1 union all
select 'emr_inf_report' table_name,'传染病报告卡' table_comment,'nationality_name' field_name,'国籍/地区名称' field_comment,'3' column_level from cdc_emr_quality_check limit 1 union all
select 'emr_activity_info' table_name,'诊疗活动信息' table_comment,'disease_code' field_name,'传染病诊断代码' field_comment,'3' column_level from cdc_emr_quality_check limit 1 union all
select 'emr_inf_report' table_name,'传染病报告卡' table_comment,'nation_code' field_name,'民族代码' field_comment,'3' column_level from cdc_emr_quality_check limit 1 union all
select 'emr_inf_report' table_name,'传染病报告卡' table_comment,'nation_name' field_name,'民族名称' field_comment,'3' column_level from cdc_emr_quality_check limit 1 union all
select 'emr_inf_report' table_name,'传染病报告卡' table_comment,'place_name' field_name,'输入来源地名称' field_comment,'3' column_level from cdc_emr_quality_check limit 1 union all
select 'emr_inf_report' table_name,'传染病报告卡' table_comment,'nationality_code' field_name,'国籍/地区代码' field_comment,'3' column_level from cdc_emr_quality_check limit 1 union all
select 'emr_inf_report' table_name,'传染病报告卡' table_comment,'dead_date' field_name,'死亡日期' field_comment,'3' column_level from cdc_emr_quality_check limit 1 union all
select 'emr_inf_report' table_name,'传染病报告卡' table_comment,'nultitude_type_other' field_name,'人群分类其他' field_comment,'3' column_level from cdc_emr_quality_check limit 1 
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
-- f.field_name,
-- c.field_comment,
sum(total_records) total_records,
    sum(null_violations) null_violations,
    sum(notnull_records) notnull_records,
    case when sum(total_records)>0 then 
       round((sum(notnull_records)/sum(total_records))*100,2)
    end  notnull_rate,
c.column_level
 from  tmp_org_list a ,tmp_records f
  join tmp_level_update c on c.table_name = f.table_name and c.field_name = f.field_name
  left join tmp_table_list d on f.table_name = d.table_name
 where a.org_code = f.org_id
 group by a.city, a.org_code, a.org_name, f.table_name, c.table_comment,c.column_level,d.table_seq
 order by a.city, a.org_code,d.table_seq
 limit 30000