-- 3张实时表
--
truncate table quality_check_realtime;

insert into quality_check_realtime(zone,org_code,org_name,table_name,table_comment,timeliness_type,total_records,compliance_records,compliance_rate)
select b.zone,
       a.org_id                   org_code,
       b.org_name                 org_name,
       a.table_name               table_name,
       c.table_comment            table_comment,
       '1'                        timeliness_type,
       a.total_records,
       a.check_type_eight_records compliance_records,
--        case when a.total_records = 0 then '-' else
--        concat(a.check_type_eight,'%') end compliance_rate
       check_type_eight as        compliance_rate
from quality_table_realtime a
     left join org_list_final b on a.org_id = b.org_code
     left join emr_table_list c on a.table_name = c.table_name
order by b."zone", a.org_id, a.table_name;

insert into quality_check_realtime(zone,org_code,org_name,table_name,table_comment,timeliness_type,total_records,compliance_records,compliance_rate)
select b.zone,
       a.org_id as org_code,
       b.org_name,
       a.table_name,
       c.table_comment,
       '2'                        timeliness_type,
       a.total_records,
       a.check_type_nine_records compliance_records,
       a.check_type_nine compliance_rate
from quality_table_2hour a
     left join org_list_final b on a.org_id = b.org_code
     left join emr_table_list c on a.table_name = c.table_name
order by b."zone", a.org_id, a.table_name;

insert into quality_check_realtime(zone,org_code,org_name,table_name,table_comment,timeliness_type,total_records,compliance_records,compliance_rate)
select b.zone,
       a.org_id as org_code,
       b.org_name,
       a.table_name,
       c.table_comment,
       '3'                      timeliness_type,
       a.total_records,
       a.check_type_ten_records compliance_records,
       a.check_type_ten         compliance_rate
from quality_table_other a
    left join org_list_final b on a.org_id = b.org_code
    left join emr_table_list c on a.table_name = c.table_name
order by b."zone", a.org_id, a.table_name;

-- 时效性明细
select a."zone" "地市(州)",
       a.org_code "机构编码",
       a.org_name "机构名称",
       a.table_name "表名称",
       a.table_comment "表注释",
       case
       a.timeliness_type
       when '1' then '实时表'
       when '2' then '2小时内'
       when '3' then 'T+0内' end as "时效性",
       a.total_records "纳入统计记录数",
       a.compliance_records "合规记录数",
       case
       when a.total_records = 0 then '-'
       else
        concat(a.compliance_rate,'%')
       end "合规率",
       case when a.timeliness_type = '1' then '①' end "优先级"
from quality_check_realtime a
left join emr_table_list b on a.table_name = b.table_name
order by a."zone",a.org_code,b.table_seq

-- 时效性达标计算
truncate table quality_realtime_org_sum;
--
insert into quality_realtime_org_sum("zone", org_code, org_name, timeliness_type, total_records, compliance_records, compliance_rate)
select a."zone",
       a.org_code,
       a.org_name,
       a.timeliness_type,
       sum(a.total_records) total_records,
       sum(a.compliance_records) compliance_records,
       case when sum(a.total_records)=0 then null
       else round((sum(a.compliance_records)/sum(a.total_records))*100,2)
       end compliance_rate
from quality_check_realtime a
left join emr_table_list b on a.table_name = b.table_name
group by a."zone",a.org_code,a.org_name,a.timeliness_type
order by a."zone",a.org_code,a.timeliness_type;

select * from quality_column_level where length_violations >0 and org_id='420111032';

select zone, org_code, org_name, table_name, table_comment, field_name, field_comment, column_level, total_records, null_violations, notnull_records, notnull_rate from quality_column_level_detail a;


-- 必填字段完整性

truncate table quality_column_level_detail;

insert into quality_column_level_detail(zone, org_code, org_name, table_name, table_comment,table_seq, field_name, field_comment, field_seq,column_level, total_records, null_violations, notnull_records, notnull_rate)
select a.zone,
       a.org_code,
       a.org_name,
       b.table_name,
       trim(c.table_comment) table_comment,
       c.table_seq,
       b.field_name,
       trim(d.field_comments) as field_comment,
       d.column_seq as field_seq,
       g.column_level,
       b.total_records,
       b.null_violations,
       case when total_records > 0 then total_records-null_violations end as notnull_records,
       case when total_records > 0 then round((1 - (null_violations / total_records))*100,2) end as notnull_rate
from org_list_final a
 left join quality_column_level b on a.org_code = b.org_id
--  and exists (select 1 from qzrj_quality_check_config g where g.table_name = b.table_name and g.field_name =g.field_name and g.column_level = '1')
 left join emr_table_list c on c.table_name = b.table_name
 left join emr_table_info d on d.table_name = b.table_name and d.field_name = b.field_name
 join qzrj_quality_check_config g on g.table_name = b.table_name and g.field_name =g.field_name
 where a.是否516='是'
 order by a."zone",a.org_code,c.table_seq;

select a."zone",
       org_code,
       org_name,
       table_name,
       trim(table_comment) table_comment ,
       sum(total_records) total_records,
       sum(null_violations) null_violations,
       sum(notnull_records) notnull_records,
       case when sum(total_records)=0 then '-'
       else
       concat(round((sum(notnull_records)/sum(total_records))*100,2),'%') end  notnull_rate
from quality_column_level_detail a
where a.column_level ='1'
group by a."zone", org_code, org_name, table_name, table_comment,table_seq
order by a.zone, a.org_code,table_seq;

drop table quality_column_level_summary;
create table quality_column_level_summary as
select a."zone",
       org_code,
       org_name,
       table_name,
       trim(table_comment) table_comment,
       column_level,
       sum(total_records) total_records,
       sum(null_violations) null_violations,
       sum(notnull_records) notnull_records,
       case when sum(total_records)=0 then null
       else
       round((sum(notnull_records)/sum(total_records))*100,2) end  notnull_rate
from quality_column_level_detail a
--where a.column_level ='1'
group by a."zone", org_code, org_name, table_name, table_comment,column_level,table_seq
order by a.zone, a.org_code,table_seq;


-- 必填明细
select a."zone",
       org_code,
       org_name,
       table_name,
       table_comment,
       total_records,
--        null_violations,
       notnull_records,
       case
           when total_records = 0 then '-'
           else
               concat(notnull_rate, '%') end notnull_rate
from quality_column_level_summary a
where a.column_level = '1'
order by a."zone", a.org_code;

-- 关键字段建议填 明细
select a."zone",
       org_code,
       org_name,
       table_name,
       table_comment,
       total_records,
--        null_violations,
       notnull_records,
       case
           when total_records = 0 then '-'
           else
               concat(notnull_rate, '%') end notnull_rate
from quality_column_level_summary a
where a.column_level = '2'
order by a."zone", a.org_code;

-- 主诉明细

 create table quality_column_level_org_summary as
 select a."zone",
       org_code,
       org_name,
       column_level,
       sum(total_records) total_records,
       sum(notnull_records) notnull_records,
       case
           when sum(total_records) > 0 then
            round((sum(notnull_records)/sum(total_records))*100,2) end notnull_rate
from quality_column_level_summary a
group by a."zone", org_code, org_name, column_level
order by a."zone", a.org_code;


-- 修订字段必填明细
drop table quality_update_column;
create table quality_update_column as
select org_code,org_name,
sum(total_records) total_records,
sum(notnull_records) notnull_records,
case when sum(total_records)>0 then
round((sum(notnull_records)/sum(total_records))*100,2) end not_null_rate

from (
select "zone",
       org_code,
       org_name,
       table_name,
       trim(table_comment) table_comment,
       column_level,
       sum(total_records) total_records,
       sum(null_violations) null_violations,
       sum(notnull_records) notnull_records,
       case when sum(total_records)=0 then null
       else
       round((sum(notnull_records)/sum(total_records))*100,2) end  notnull_rate
from quality_column_level_detail a
where (a.table_name,a.field_name) in (
('emr_patient_info','gender_code'),
('emr_patient_info','gender_name'),
('emr_patient_info','birth_date'),
('emr_patient_info','nation_code'),
('emr_patient_info','nation_name'),
('emr_patient_info','nationality_code'),
('emr_patient_info','nationality_name'),
('emr_patient_info','current_addr_code'),
('emr_patient_info','current_addr_name'),
('emr_patient_info','current_addr_detail'),
('emr_patient_info','tel'),
('emr_patient_info','workunit'),
('emr_activity_info','chief_complaint'),
('emr_activity_info','present_illness_his'),
('emr_activity_info','physical_examination'),
('emr_activity_info','studies_summary_result'),
('emr_inf_report','gender_code'),
('emr_inf_report','gender_name'),
('emr_inf_report','nultitude_type_name'),
('emr_inf_report','afp_doctor_date'),
('emr_outpatient_record','outpatient_date'),
('emr_outpatient_record','chief_complaint'),
('emr_outpatient_record','present_illness_his'),
('emr_outpatient_record','physical_examination'),
('emr_outpatient_record','studies_summary_result'),
('emr_outpatient_record','inital_diagnosis_code'),
('emr_outpatient_obs','chief_complaint'),
('emr_outpatient_obs','present_illness_his'),
('emr_outpatient_obs','physical_examination'),
('emr_outpatient_obs','studies_summary_result'),
('emr_admission_info','chief_complaint'),
('emr_admission_info','present_illness_his'),
('emr_admission_info','physical_examination'),
('emr_admission_info','studies_summary_result'),
('emr_admission_info','wm_inital_diagnosis_code'),
('emr_admission_info','wm_inital_diagnosis_name'),
('emr_admission_info','ward_name'),
('emr_admission_info','admission_date'),
('emr_admission_record','admission_date'),
('emr_discharge_info','admission_date'),
('emr_discharge_info','admission_diagnosis_code'),
('emr_discharge_info','admission_diagnosis_name'),
('emr_discharge_info','disease_progression_code'),
('emr_discharge_info','admission_desc'),
('emr_ex_clinical','examination_objective_desc'),
('emr_ex_clinical','examination_subjective_desc'),
('emr_ex_clinical','examination_report_no'),
('emr_ex_clinical','apply_dept_code'),
('emr_ex_clinical','apply_dept_name'),
('emr_ex_clinical_item','item_code'),
('emr_ex_clinical_item','item_name'),
('emr_ex_lab','specimen_sampling_date'),
('emr_ex_lab','specimen_category_code'),
('emr_ex_lab','specimen_category_name'),
('emr_ex_lab','specimen_receiving_date'),
('emr_ex_lab','apply_org_code'),
('emr_ex_lab','apply_org_name'),
('emr_ex_lab','apply_dept_code'),
('emr_ex_lab','apply_dept_name'),
('emr_ex_lab_item','source_examination_result_code'),
('emr_ex_lab_item','source_examination_result_name'),
('emr_ex_lab_item','examination_result_code'),
('emr_ex_lab_item','examination_result_name'),
('emr_ex_lab_item','examination_quantification'),
('emr_order','prescription_issuance_date'),
('emr_order_item','drug_specifications'),
('emr_order_item','drug_dosage_code'),
('emr_order_item','drug_dosage_unit_code'),
('emr_order_item','drug_dosage_unit_name')
)
group by a."zone", org_code, org_name, table_name, table_comment,column_level,table_seq)
group by "zone", org_code, org_name
order by zone, org_code;

create table quality_update_column_level2 as
select org_code,org_name,
sum(total_records) total_records,
sum(notnull_records) notnull_records,
case when sum(total_records)>0 then
round((sum(notnull_records)/sum(total_records))*100,2) end not_null_rate
from (
select "zone",
       org_code,
       org_name,
       table_name,
       trim(table_comment) table_comment,
       column_level,
       sum(total_records) total_records,
       sum(null_violations) null_violations,
       sum(notnull_records) notnull_records,
       case when sum(total_records)=0 then null
       else
       round((sum(notnull_records)/sum(total_records))*100,2) end  notnull_rate
from quality_column_level_detail a
where (a.table_name,a.field_name) in (
('emr_activity_info','disease_code'),
('emr_activity_info','disease_name'),
('emr_inf_report','nationality_code'),
('emr_inf_report','nationality_name'),
('emr_inf_report','nation_code'),
('emr_inf_report','nation_name'),
('emr_inf_report','nultitude_type_other'),
('emr_inf_report','dead_date'),
('emr_inf_report','foreign_type_code'),
('emr_inf_report','foreign_type_name'),
('emr_inf_report','place_code'),
('emr_inf_report','place_name')
)
group by a."zone", org_code, org_name, table_name, table_comment,column_level,table_seq
)
group by "zone", org_code, org_name
order by zone, org_code;


-- 主诉
select a.zone,
       a.org_code,
       a.org_name,
       b.是否哨点,
       table_name,
       table_comment,
       field_name,
       field_comment,
       total_records,
       notnull_records ,
       case
       when total_records is null then null
       when total_records =0 then '-'
       else
        concat(round((notnull_records / total_records) * 100, 2),'%')
           end              not_null_rate
from (select "zone",
             org_code,
             org_name,
             table_name,
             trim(table_comment)                                                     table_comment,
             field_name,
             '主诉'                                                                  field_comment,
             column_level,
             sum(total_records)                                                      total_records,
             sum(null_violations)                                                    null_violations,
             sum(notnull_records)                                                    notnull_records,
             case
                 when sum(total_records) = 0 then null
                 else
                     round((sum(notnull_records) / sum(total_records)) * 100, 2) end notnull_rate
      from quality_column_level_detail a

      where (a.table_name, a.field_name) in (
                                             ('emr_activity_info', 'chief_complaint'),
                                             ('emr_outpatient_record', 'chief_complaint'),
                                             ('emr_outpatient_obs', 'chief_complaint'),
                                             ('emr_admission_info', 'chief_complaint'),
                                             ('emr_first_course', 'chief_complaint')
          )
      group by a."zone", org_code, org_name, table_name, table_comment, field_name, column_level, table_seq) a
         left join org_list_final b on a.org_code = b.org_code
order by a.zone, a.org_code;

-- 现病史明细
select a.zone,
       a.org_code,
       a.org_name,
       b.是否哨点,
       table_name,
       table_comment,
       field_name,
       field_comment,
       sum(total_records)   total_records,
       sum(notnull_records) notnull_records,
       case
           when sum(total_records) > 0 then
               round((sum(notnull_records) / sum(total_records)) * 100, 2)
           end              not_null_rate
from (select "zone",
             org_code,
             org_name,
             table_name,
             trim(table_comment)                                                     table_comment,
             field_name,
             '现病史'                                                                  field_comment,
             column_level,
             sum(total_records)                                                      total_records,
             sum(null_violations)                                                    null_violations,
             sum(notnull_records)                                                    notnull_records,
             case
                 when sum(total_records) = 0 then null
                 else
                     round((sum(notnull_records) / sum(total_records)) * 100, 2) end notnull_rate
      from quality_column_level_detail a

      where (a.table_name, a.field_name) in (
 ('emr_outpatient_record','present_illness_his'),
('emr_outpatient_obs','present_illness_his'),
('emr_admission_info','present_illness_his')

          )
      group by a."zone", org_code, org_name, table_name, table_comment, field_name, column_level, table_seq) a
         left join org_list_final b on a.org_code = b.org_code
group by a."zone", a.org_code, a.org_name, table_name, table_comment, field_name, field_comment, b.是否哨点
order by a.zone, a.org_code;

select table_name,field_name from emr_table_info a where field_comments ='现病史'
-- 现病史
select b.* from quality_association b where org_id='420111032' and table_name='emr_outpatient_record';

-- 关联关系明细
-- drop table quality_association_detail;
-- create table quality_association_detail as

truncate table quality_association_detail;

insert into quality_association_detail(zone,org_code,org_name,table_name,table_comment,association_table,association_table_comment,total_records,association_records,association_rate)
-- create table quality_association_detail as
select a.zone,
       a.org_code,
       a.org_name,
       b.table_name,
       c.table_comment,
       case when b.table_name is not null then
       'emr_patient_info' end association_table,
       case when b.table_name is not null then '患者基本信息表' end association_table_comment,
       b.total_records,
       b.patient_association_violations association_records,
       case when b.total_records is null then null
       when b.total_records >0 then  round((b.patient_association_violations/b.total_records)*100,2) end association_rate
from org_list_final a
left join quality_association b on a.org_code = b.org_id and b.field_name in('1','1,2')
left join emr_table_list c on b.table_name = c.table_name
order by a."zone",a.org_code,c.table_seq;

insert into quality_association_detail(zone,org_code,org_name,table_name,table_comment,association_table,association_table_comment,total_records,association_records,association_rate)
select a.zone,
       a.org_code,
       a.org_name,
       b.table_name,
       c.table_comment,
       case when b.table_name is not null then 'emr_activity_info' end association_table,
       case when b.table_name is not null then '诊疗活动信息表' end association_table_comment,
       b.total_records,
       b.activity_association_violations association_records,
       case when b.total_records is null then null
       when b.total_records >0 then  round((b.activity_association_violations/b.total_records)*100,2) end association_rate
from org_list_final a
left join quality_association b on a.org_code = b.org_id and b.field_name in('1','1,2') and table_name <>'emr_activity_info'
left join emr_table_list c on b.table_name = c.table_name
order by a."zone",a.org_code,c.table_seq;

insert into quality_association_detail(zone,org_code,org_name,table_name,table_comment,association_table,association_table_comment,total_records,association_records,association_rate)
select a.zone,
       a.org_code,
       a.org_name,
       b.table_name,
       c.table_comment,
       case b.table_name
       when 'emr_order_item' then 'emr_order'
       when 'emr_ex_lab_item' then 'emr_ex_lab'
       when 'emr_ex_clinical_item' then 'emr_ex_clinical'
       end association_table,
       case b.table_name
       when 'emr_order_item' then '检查报告'
       when 'emr_ex_lab_item' then '检验报告'
       when 'emr_ex_clinical_item' then '医嘱处方'
       end association_table_comment,
       b.total_records,
       b.master_association_violations association_records,
       case when b.total_records is null then null
       when b.total_records >0 then  round((b.master_association_violations/b.total_records)*100,2) end association_rate
from org_list_final a
left join quality_association b on a.org_code = b.org_id and b.field_name ='3'
left join emr_table_list c on b.table_name = c.table_name
order by a."zone",a.org_code,c.table_seq;



select distinct a."zone",
       a.org_code,
       a.org_name,
       a.table_name,
       a.table_comment,
       a.association_table,
       a.association_table_comment,
       a.total_records,
       a.association_records,
       case when a.total_records is null then null
       when a.total_records =0 then '-'
       when a.total_records >0 then
       concat(a.association_rate,'%') end
       association_rate
from quality_association_detail a
left join emr_table_list b on a.table_name = b.table_name
order by a."zone",a.org_code,b.table_seq;

--
create table quality_association_org_summary as
select a."zone",
       a.org_code,
       a.org_name,
--        a.table_name,
--        a.table_comment,
       a.association_table,
--        a.association_table_comment,
       sum(a.total_records) total_records,
       sum(a.association_records) association_records,
       case when sum(a.total_records) >0 then
       round((sum(a.association_records)/sum(a.total_records))*100,2) end  association_rate
from quality_association_detail a
where a.association_table in('emr_patient_info','emr_activity_info')
group by a."zone", a.org_code, a.org_name, a.association_table
order by "zone",org_code;


-- -- 机构汇总
-- create table quality_timeliness_org_summary as
-- select a."zone",
--        a.org_code,
--        a.org_name,
--        b.total_records realtime_total_records,
--        b.compliance_records realtime_compliance_records,
--        case when b.total_records is null then null
--        when b.total_records = 0 then null else
--        b.compliance_rate end as realtime_compliance_rate,
--        c.total_records hour_total_records,
--        c.compliance_records hour_compliance_records,
--        case when c.total_records is null then null
--        when c.total_records = 0 then null else
--        c.compliance_rate end as hour_compliance_rate,
--        d.total_records other_total_records,
--        d.compliance_records other_compliance_records,
--        case when d.total_records is null then null
--        when d.total_records = 0 then null else
--        d.compliance_rate end as other_compliance_rate
-- from org_list_final a
--   left join quality_realtime_org_sum b on a.org_code = b.org_code and b.timeliness_type = '1'
--   left join quality_realtime_org_sum c on a.org_code = c.org_code and c.timeliness_type = '2'
--   left join quality_realtime_org_sum d on a.org_code = d.org_code and d.timeliness_type = '3'
--
--   where a.是否516 = '是'
-- order by a."zone",a.org_code;



-- 机构汇总查询SQL
select a."zone",
       a.org_code,
       a.org_name,
        b.realtime_total_records realtime_total_records,
       b.realtime_compliance_records,
       case
           when b.realtime_total_records is null then null
           when b.realtime_total_records = 0 then '-'
           else concat(b.realtime_compliance_rate, '%') end "实时表达标率",
       b.hour_total_records,
       b.hour_compliance_records,
       case
           when b.hour_total_records is null then null
           when b.hour_total_records = 0 then '-'
           else concat(b.hour_compliance_rate, '%') end     "2小时表达标率",
       b.other_total_records,
       b.other_compliance_records,
       case
           when b.other_total_records is null then null
           when b.other_total_records = 0 then '-'
           else concat(b.other_compliance_rate, '%') end    "T+0表达标率",
           c.total_records,
           c.notnull_records,
           c.notnull_rate,
           d.total_records,
           d.notnull_records,
           d.notnull_rate,
           e.total_records,
           e.notnull_records,
           case when e.total_records is null then null
           when e.total_records >0 then concat(e.not_null_rate,'%') end update_level1_not_null_rate,
           f.total_records,
           f.notnull_records,
           case when f.total_records is null then null
           when f.total_records >0 then concat(f.not_null_rate,'%') end update_level2_not_null_rate,
           g.total_records,
           g.association_records,
           case when g.total_records >0 then
           concat(g.association_rate,'%') end g_association_rate,
           h.total_records,
           h.association_records,
          case when h.total_records >0 then
          concat(h.association_rate,'%') end h_association_rate,
          case when (g.total_records+h.total_records) is null then null
          when (g.total_records+h.total_records) = 0 then '-' else
          -- 平均关联率不对
          concat(round(((g.association_records+h.association_records)/(g.total_records+h.total_records))*100,2),'%') end avg_rate
from org_list_final a
         left join quality_timeliness_org_summary b on a.org_code = b.org_code
         left join quality_column_level_org_summary c on c.org_code = a.org_code and c.column_level='1'
         left join quality_column_level_org_summary d on d.org_code = a.org_code and d.column_level='2'
         left join quality_update_column e on e.org_code = a.org_code
         left join quality_update_column_level2 f on f.org_code = a.org_code
         left join quality_association_org_summary g on g.org_code = a.org_code and g.association_table='emr_patient_info'
         left join quality_association_org_summary h on h.org_code = a.org_code and h.association_table='emr_activity_info'
where a.是否516 = '是'
order by a."zone", a.org_code;


-- 地市汇总
select zone,
org_count,
realtime_orgcount,
concat(round((realtime_orgcount/org_count)*100,2),'%') as realtime_zone_rate,
hour_orgcount,
concat(round((hour_orgcount/org_count)*100,2),'%') as hour_zone_rate,
other_orgcount,
concat(round((other_orgcount/org_count)*100,2),'%') as other_zone_rate,
level_1_total_records,
level_1_notnull_records,
concat(round(level_1_notnull_rate*100,2),'%') level_1_notnull_rate,
level_2_total_records,
level_2_notnull_records,
concat(round(level_2_notnull_rate*100,2),'%') level_2_notnull_rate,
update_level1_total_records,
update_level1_notnull_records,
concat(round(update_level1_rate*100,2),'%') update_level1_rate,
update_level3_total_records,
update_level3_notnull_records,
concat(round(update_level3_rate*100,2),'%') update_level3_rate,
g_association_cnt,
concat(round((g_association_cnt/org_count)*100,2),'%') g_association_rate
from (select a."zone", count (a.org_code) as org_count,
sum (case when b.realtime_compliance_rate >= 90 then 1 else 0 end) realtime_orgcount,
sum (case when b.hour_compliance_rate >= 100 then 1 else 0 end) hour_orgcount,
sum (case when b.other_compliance_rate >= 100 then 1 else 0 end) other_orgcount,
    sum(c.total_records) as level_1_total_records,
    sum(c.notnull_records) level_1_notnull_records,
    case when sum(c.total_records) >0 then sum(c.notnull_records)/sum(c.total_records) end level_1_notnull_rate ,
    sum(d.total_records) level_2_total_records,
    sum(d.notnull_records) level_2_notnull_records,
    case when sum(d.total_records) >0 then sum(d.notnull_records)/sum(d.total_records) end level_2_notnull_rate,
    sum(e.total_records) as update_level1_total_records,
    sum(e.notnull_records) as update_level1_notnull_records,
    case when sum(e.total_records)>0 then sum(e.notnull_records)/sum(e.total_records) end update_level1_rate,
    sum(f.total_records) as update_level3_total_records,
    sum(f.notnull_records) as update_level3_notnull_records,
    case when sum(f.total_records)>0 then sum(f.notnull_records)/sum(f.total_records) end update_level3_rate,
    sum(g.total_records) g_total_records,
    sum(g.association_records) g_association_records,
    sum(case when g_association_rate >= 0.90 then 1 else 0 end) g_association_cnt
    from org_list_final a
    left join quality_timeliness_org_summary b on a.org_code = b.org_code
    left join quality_column_level_org_summary c on c.org_code = a.org_code and c.column_level='1'
    left join quality_column_level_org_summary d on d.org_code = a.org_code and d.column_level='2'
    left join quality_update_column e on e.org_code =a.org_code
    left join quality_update_column_level2 f on f.org_code = a.org_code
     left join (select zone,org_code,org_name,sum(total_records) total_records,sum(association_records) association_records,case when sum(total_records) =0 then 0 else  sum(association_records)/sum(total_records) end as g_association_rate from quality_association_org_summary group by zone,org_code,org_name) g on g.org_code = a.org_code
    where a.是否516 = '是'
    group by a.zone)
order by zone;

