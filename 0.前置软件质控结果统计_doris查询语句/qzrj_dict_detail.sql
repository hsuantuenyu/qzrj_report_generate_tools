/**********************************
*描述：值域映射
**********************************/
WITH tmp_table_field_info AS (
select 'emr_patient_info' table_name,'患者基本信息表' table_comment,'id_card_type_code' field_name,'身份证件类别代码' field_comment,1 field_seq from cdc_emr_quality_check_dict limit 1 union all
select 'emr_patient_info' table_name,'患者基本信息表' table_comment,'gender_code' field_name,'性别代码' field_comment,2 field_seq from cdc_emr_quality_check_dict limit 1 union all
select 'emr_patient_info' table_name,'患者基本信息表' table_comment,'nationality_code' field_name,'国籍/地区代码' field_comment,3 field_seq from cdc_emr_quality_check_dict limit 1 union all
select 'emr_patient_info' table_name,'患者基本信息表' table_comment,'nation_code' field_name,'民族代码' field_comment,4 field_seq from cdc_emr_quality_check_dict limit 1 union all
select 'emr_patient_info' table_name,'患者基本信息表' table_comment,'permanent_addr_code' field_name,'户籍地址代码' field_comment,5 field_seq from cdc_emr_quality_check_dict limit 1 union all
select 'emr_patient_info' table_name,'患者基本信息表' table_comment,'current_addr_code' field_name,'现住地区代码' field_comment,6 field_seq from cdc_emr_quality_check_dict limit 1 union all
select 'emr_patient_info' table_name,'患者基本信息表' table_comment,'marital_status_code' field_name,'婚姻状况代码' field_comment,7 field_seq from cdc_emr_quality_check_dict limit 1 union all
select 'emr_patient_info' table_name,'患者基本信息表' table_comment,'education_code' field_name,'学历代码' field_comment,8 field_seq from cdc_emr_quality_check_dict limit 1 union all
select 'emr_patient_info' table_name,'患者基本信息表' table_comment,'nultitude_type_code' field_name,'人群分类代码' field_comment,9 field_seq from cdc_emr_quality_check_dict limit 1 union all
select 'emr_patient_info' table_name,'患者基本信息表' table_comment,'org_code' field_name,'医疗机构代码' field_comment,10 field_seq from cdc_emr_quality_check_dict limit 1 union all
select 'emr_activity_info' table_name,'诊疗活动信息表' table_comment,'activity_type_code' field_name,'诊疗活动类型代码' field_comment,12 field_seq from cdc_emr_quality_check_dict limit 1 union all
select 'emr_activity_info' table_name,'诊疗活动信息表' table_comment,'id_card_type_code' field_name,'身份证件类别代码' field_comment,13 field_seq from cdc_emr_quality_check_dict limit 1 union all
select 'emr_activity_info' table_name,'诊疗活动信息表' table_comment,'disease_code' field_name,'传染病诊断' field_comment,14 field_seq from cdc_emr_quality_check_dict limit 1 union all
select 'emr_activity_info' table_name,'诊疗活动信息表' table_comment,'org_code' field_name,'医疗机构代码' field_comment,16 field_seq from cdc_emr_quality_check_dict limit 1 union all
select 'emr_inf_report' table_name,'传染病报告卡' table_comment,'activity_type_code' field_name,'诊疗活动类型代码' field_comment,18 field_seq from cdc_emr_quality_check_dict limit 1 union all
select 'emr_outpatient_record' table_name,'门急诊病历表' table_comment,'id_card_type_code' field_name,'身份证件类别代码' field_comment,21 field_seq from cdc_emr_quality_check_dict limit 1 union all
select 'emr_outpatient_record' table_name,'门急诊病历表' table_comment,'allergy_his_flag' field_name,'过敏史标志' field_comment,22 field_seq from cdc_emr_quality_check_dict limit 1 union all
select 'emr_outpatient_record' table_name,'门急诊病历表' table_comment,'inital_diagnosis_code' field_name,'初诊标志代码' field_comment,23 field_seq from cdc_emr_quality_check_dict limit 1 union all
select 'emr_outpatient_record' table_name,'门急诊病历表' table_comment,'org_code' field_name,'医疗机构代码' field_comment,25 field_seq from cdc_emr_quality_check_dict limit 1 union all
select 'emr_outpatient_obs' table_name,'门急诊留观记录' table_comment,'id_card_type_code' field_name,'身份证件类别代码' field_comment,27 field_seq from cdc_emr_quality_check_dict limit 1 union all
select 'emr_outpatient_obs' table_name,'门急诊留观记录' table_comment,'allergy_his_flag' field_name,'过敏史标志' field_comment,28 field_seq from cdc_emr_quality_check_dict limit 1 union all
select 'emr_outpatient_obs' table_name,'门急诊留观记录' table_comment,'inital_diagnosis_code' field_name,'初诊标志代码' field_comment,29 field_seq from cdc_emr_quality_check_dict limit 1 union all
select 'emr_outpatient_obs' table_name,'门急诊留观记录' table_comment,'org_code' field_name,'医疗机构代码' field_comment,31 field_seq from cdc_emr_quality_check_dict limit 1 union all
select 'emr_admission_info' table_name,'入院记录表' table_comment,'id_card_type_code' field_name,'身份证件类别代码' field_comment,33 field_seq from cdc_emr_quality_check_dict limit 1 union all
select 'emr_admission_info' table_name,'入院记录表' table_comment,'org_code' field_name,'医疗机构代码' field_comment,35 field_seq from cdc_emr_quality_check_dict limit 1 union all
select 'emr_first_course' table_name,'住院首次病程记录' table_comment,'id_card_type_code' field_name,'身份证件类别代码' field_comment,37 field_seq from cdc_emr_quality_check_dict limit 1 union all
select 'emr_first_course' table_name,'住院首次病程记录' table_comment,'disease_progression_code' field_name,'病情转归代码' field_comment,38 field_seq from cdc_emr_quality_check_dict limit 1 union all
select 'emr_first_course' table_name,'住院首次病程记录' table_comment,'org_code' field_name,'医疗机构代码' field_comment,40 field_seq from cdc_emr_quality_check_dict limit 1 union all
select 'emr_daily_course' table_name,'住院日常病程记录' table_comment,'id_card_type_code' field_name,'身份证件类别代码' field_comment,42 field_seq from cdc_emr_quality_check_dict limit 1 union all
select 'emr_daily_course' table_name,'住院日常病程记录' table_comment,'disease_progression_code' field_name,'病情转归代码' field_comment,43 field_seq from cdc_emr_quality_check_dict limit 1 union all
select 'emr_daily_course' table_name,'住院日常病程记录' table_comment,'org_code' field_name,'医疗机构代码' field_comment,45 field_seq from cdc_emr_quality_check_dict limit 1 union all
select 'emr_admission_record' table_name,'住院病案首页' table_comment,'id_card_type_code' field_name,'身份证件类别代码' field_comment,47 field_seq from cdc_emr_quality_check_dict limit 1 union all
select 'emr_admission_record' table_name,'住院病案首页' table_comment,'allergy_code' field_name,'药物过敏标志' field_comment,50 field_seq from cdc_emr_quality_check_dict limit 1 union all
select 'emr_admission_record' table_name,'住院病案首页' table_comment,'accept_org_code' field_name,'拟接收医疗机构代码' field_comment,51 field_seq from cdc_emr_quality_check_dict limit 1 union all
select 'emr_admission_record' table_name,'住院病案首页' table_comment,'org_code' field_name,'医疗机构代码' field_comment,53 field_seq from cdc_emr_quality_check_dict limit 1 union all
select 'emr_discharge_info' table_name,'出院记录' table_comment,'id_card_type_code' field_name,'身份证件类别代码' field_comment,55 field_seq from cdc_emr_quality_check_dict limit 1 union all
select 'emr_discharge_info' table_name,'出院记录' table_comment,'disease_progression_code' field_name,'病情转归代码' field_comment,56 field_seq from cdc_emr_quality_check_dict limit 1 union all
select 'emr_discharge_info' table_name,'出院记录' table_comment,'org_code' field_name,'医疗机构代码' field_comment,58 field_seq from cdc_emr_quality_check_dict limit 1 union all
select 'emr_ex_clinical' table_name,'检查报告表' table_comment,'activity_type_code' field_name,'诊疗活动类型代码' field_comment,60 field_seq from cdc_emr_quality_check_dict limit 1 union all
select 'emr_ex_clinical' table_name,'检查报告表' table_comment,'id_card_type_code' field_name,'身份证件类别代码' field_comment,61 field_seq from cdc_emr_quality_check_dict limit 1 union all
select 'emr_ex_clinical' table_name,'检查报告表' table_comment,'apply_org_code' field_name,'检查申请机构代码' field_comment,62 field_seq from cdc_emr_quality_check_dict limit 1 union all
select 'emr_ex_clinical' table_name,'检查报告表' table_comment,'examination_type_code' field_name,'检查类别代码' field_comment,64 field_seq from cdc_emr_quality_check_dict limit 1 union all
select 'emr_ex_clinical' table_name,'检查报告表' table_comment,'org_code' field_name,'医疗机构代码' field_comment,66 field_seq from cdc_emr_quality_check_dict limit 1 union all
select 'emr_ex_clinical_item' table_name,'检查报告项目' table_comment,'item_code' field_name,'检查项目代码' field_comment,68 field_seq from cdc_emr_quality_check_dict limit 1 union all
select 'emr_ex_clinical_item' table_name,'检查报告项目' table_comment,'examination_result_code' field_name,'检查结果代码' field_comment,69 field_seq from cdc_emr_quality_check_dict limit 1 union all
select 'emr_ex_lab' table_name,'检验报告表' table_comment,'activity_type_code' field_name,'诊疗活动类型代码' field_comment,71 field_seq from cdc_emr_quality_check_dict limit 1 union all
select 'emr_ex_lab' table_name,'检验报告表' table_comment,'id_card_type_code' field_name,'身份证件类别代码' field_comment,72 field_seq from cdc_emr_quality_check_dict limit 1 union all
select 'emr_ex_lab' table_name,'检验报告表' table_comment,'apply_org_code' field_name,'检查申请机构代码' field_comment,73 field_seq from cdc_emr_quality_check_dict limit 1 union all
select 'emr_ex_lab' table_name,'检验报告表' table_comment,'specimen_category_code' field_name,'标本类别代码' field_comment,75 field_seq from cdc_emr_quality_check_dict limit 1 union all
select 'emr_ex_lab' table_name,'检验报告表' table_comment,'org_code' field_name,'医疗机构代码' field_comment,77 field_seq from cdc_emr_quality_check_dict limit 1 union all
select 'emr_ex_lab_item' table_name,'检查报告项目' table_comment,'examination_result_code' field_name,'标化检验定性结果代码' field_comment,79 field_seq from cdc_emr_quality_check_dict limit 1 union all
select 'emr_ex_lab_item' table_name,'检查报告项目' table_comment,'examination_quantification_ri' field_name,'检验定量结果超出或低于参考值' field_comment,80 field_seq from cdc_emr_quality_check_dict limit 1 union all
select 'emr_order' table_name,'医嘱处方信息' table_comment,'activity_type_code' field_name,'诊疗活动类型代码' field_comment,82 field_seq from cdc_emr_quality_check_dict limit 1 union all
select 'emr_order' table_name,'医嘱处方信息' table_comment,'id_card_type_code' field_name,'身份证件类别代码' field_comment,83 field_seq from cdc_emr_quality_check_dict limit 1 union all
select 'emr_order' table_name,'医嘱处方信息' table_comment,'prescription_type_code' field_name,'处方类别代码' field_comment,84 field_seq from cdc_emr_quality_check_dict limit 1 union all
select 'emr_order' table_name,'医嘱处方信息' table_comment,'org_code' field_name,'医疗机构代码' field_comment,86 field_seq from cdc_emr_quality_check_dict limit 1 union all
select 'emr_order_item' table_name,'医嘱处方条目' table_comment,'drug_dosage_unit_code' field_name,'药物使用剂量单位代码' field_comment,89 field_seq from cdc_emr_quality_check_dict limit 1 union all
select 'emr_death_info' table_name,'死亡信息' table_comment,'activity_type_code' field_name,'诊疗活动类型代码' field_comment,91 field_seq from cdc_emr_quality_check_dict limit 1 union all
select 'emr_death_info' table_name,'死亡信息' table_comment,'id_card_type_code' field_name,'身份证件类别代码' field_comment,92 field_seq from cdc_emr_quality_check_dict limit 1 union all
select 'emr_death_info' table_name,'死亡信息' table_comment,'death_diagnosis_code' field_name,'死亡诊断代码' field_comment,93 field_seq from cdc_emr_quality_check_dict limit 1 union all
select 'emr_death_info' table_name,'死亡信息' table_comment,'org_code' field_name,'医疗机构代码' field_comment,95 field_seq from cdc_emr_quality_check_dict limit 1 union all
select 'emr_vital_signs_record' table_name,'生命体征护理记录单' table_comment,'activity_type_code' field_name,'诊疗活动类型代码' field_comment,97 field_seq from cdc_emr_quality_check_dict limit 1 union all
select 'emr_vital_signs_record' table_name,'生命体征护理记录单' table_comment,'id_card_type_code' field_name,'身份证件类别代码' field_comment,98 field_seq from cdc_emr_quality_check_dict limit 1 union all
select 'emr_vital_signs_record' table_name,'生命体征护理记录单' table_comment,'ventilatorused_code' field_name,'是否使用呼吸机代码' field_comment,99 field_seq from cdc_emr_quality_check_dict limit 1 union all
select 'emr_vital_signs_record' table_name,'生命体征护理记录单' table_comment,'critical_care_code' field_name,'是否重症监护代码' field_comment,100 field_seq from cdc_emr_quality_check_dict limit 1 union all
select 'emr_vital_signs_record' table_name,'生命体征护理记录单' table_comment,'org_code' field_name,'医疗机构代码' field_comment,102 field_seq from cdc_emr_quality_check_dict limit 1 union all
select 'base_user' table_name,'医院信息系统用户信息' table_comment,'id_card_type_code' field_name,'身份证件类别' field_comment,104 field_seq from cdc_emr_quality_check_dict limit 1 union all
select 'base_user' table_name,'医院信息系统用户信息' table_comment,'user_type_code' field_name,'用户类型' field_comment,105 field_seq from cdc_emr_quality_check_dict limit 1
),
tmp_org_list as 
(select distinct city,org_code,org_name from cdc_mdm_org_code where is_516='是')

SELECT
  a.city,
  a.org_code,
  a.org_name,
  b.table_name,
  c.table_comment,
  b.field_name,
  c.field_comment,
  sum(total_records) total_records,
  sum(non_empty_violations) non_empty_violations,
  sum(dict_violations) dict_violations,
  case  when sum(non_empty_violations) > 0 then
  round((sum(dict_violations) / sum(non_empty_violations))*100,2) end dict_rate
from
 tmp_org_list a,
 cdc_emr_quality_check_dict b,
 tmp_table_field_info c 
where
 c.table_name = b.table_name
 and c.field_name = b.field_name
 and a.org_code = b.org_id
  and FROM_UNIXTIME(b.check_time / 1000) >= '2026-04-13 00:00:00'
  and FROM_UNIXTIME(b.check_time / 1000) <= '2026-04-13 00:00:00'
  group by a.city, a.org_code, a.org_name, b.table_name, c.table_comment, b.field_name, c.field_comment ,c.field_seq
  order by  a.city, a.org_code,b.table_name,c.field_seq
limit
  50000
