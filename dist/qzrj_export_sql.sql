truncate table qzrj_realtime_org;
-- create table qzrj_realtime_org as
insert into qzrj_realtime_org
select b.city,
       b.org_code,
       b.org_name,
       b.table_type,
       sum(b.total_records)       total_recods,
       sum(b.compliance_records) compliance_records,
       case
           when sum(b.total_records) > 0 then
               round((sum(b.compliance_records) / sum(b.total_records)) * 100, 2)
           end                   compliance_rate
from qzrj_realtime_detail b
group by b.city,
         b.org_code,
         b.org_name,
         b.table_type
order by b.city, b.org_code;

truncate table qzrj_column_level_org;
-- 字段完整性
-- create table qzrj_column_level_org as
insert into qzrj_column_level_org
select a.city,
       a.org_code,
       a.org_name,
       '1' column_level,
       sum(a.total_records)                                                        total_records,
       sum(a.notnull_records)                                                      notnull_records,
       case
           when sum(a.total_records) > 0 then
               round((sum(a.notnull_records) / sum(a.total_records)) * 100, 2) end notnull_rate
from qzrj_column_level_1_detail a
group by a.city, a.org_code, a.org_name
order by a.city, a.org_code;

insert into qzrj_column_level_org
select a.city,
       a.org_code,
       a.org_name,
       '2' column_level,
       sum(a.total_records)                                                        total_records,
       sum(a.notnull_records)                                                      notnull_records,
       case
           when sum(a.total_records) > 0 then
               round((sum(a.notnull_records) / sum(a.total_records)) * 100, 2) end notnull_rate
from qzrj_column_level_2_detail a
group by a.city, a.org_code, a.org_name
order by a.city, a.org_code;

--
insert into qzrj_column_level_org
select a.city,
       a.org_code,
       a.org_name,
       'update_3' column_level,
       sum(a.total_records)                                                        total_records,
       sum(a.notnull_records)                                                      notnull_records,
       case
           when sum(a.total_records) > 0 then
               round((sum(a.notnull_records) / sum(a.total_records)) * 100, 2) end notnull_rate
from qzrj_column_update_detail a
group by a.city, a.org_code, a.org_name
order by a.city, a.org_code;

insert into qzrj_column_level_org
select a.city,
       a.org_code,
       a.org_name,
       'update_1' column_level,
       sum(a.total_records)                                                        total_records,
       sum(a.notnull_records)                                                      notnull_records,
       case
           when sum(a.total_records) > 0 then
               round((sum(a.notnull_records) / sum(a.total_records)) * 100, 2) end notnull_rate
from qzrj_column_update_detail a
group by a.city, a.org_code, a.org_name
order by a.city, a.org_code;

-- drop table qzrj_association_org;

truncate table qzrj_association_org;
-- 关联关系
-- create table qzrj_association_org as
insert into qzrj_association_org
select a.city,a.org_code,
       a.org_name,
       'all' association_table,
       sum(a.total_records) total_records,
       sum(a.association_records) association_records,
       case when sum(a.total_records) >0 then
           round((sum(a.association_records)/sum(a.total_records))*100,2)
       end association_rate
       from qzrj_association_detail a
group by a.city, a.org_code, a.org_name
order by a.city,a.org_code;

-- 患者基本信息
insert into qzrj_association_org
select a.city,a.org_code,
       a.org_name,
       a.association_table,
       sum(a.total_records) total_records,
       sum(a.association_records) association_records,
       case when sum(a.total_records) >0 then
           round((sum(a.association_records)/sum(a.total_records))*100,2)
       end association_rate
       from qzrj_association_detail a
       where a.association_table='emr_patient_info'
group by a.city, a.org_code, a.org_name,a.association_table
order by a.city,a.org_code;

insert into qzrj_association_org
select a.city,a.org_code,
       a.org_name,
       a.association_table,
       sum(a.total_records) total_records,
       sum(a.association_records) association_records,
       case when sum(a.total_records) >0 then
           round((sum(a.association_records)/sum(a.total_records))*100,2)
       end association_rate
       from qzrj_association_detail a
       where a.association_table='emr_activity_info'
group by a.city, a.org_code, a.org_name,a.association_table
order by a.city,a.org_code;

--
truncate table qzrj_dict_org;
-- create table qzrj_dict_org as
insert into qzrj_dict_org
select a.city, a.org_code, a.org_name,
       sum(a.non_empty_violations) non_empty_violations,
       sum(a.dict_violations) dict_violations,
       case when sum(a.non_empty_violations) > 0 then
       round((sum(a.dict_violations)/sum(a.non_empty_violations))*100,2) end dict_rate
from qzrj_dict_detail a
group by a.city, a.org_code, a.org_name
order by a.city,a.org_code;


--
-- 时效性Sheet页明细
select a.city,
       a.org_code,
       a.org_name,
       b.table_name,
       b.table_comment,
       b.table_type,
       b.total_records,
       b.compliance_records,
       case
           when total_records is null then null
           when total_records = 0 then '-'
           else
               concat(b.compliance_rate, '%') end compliance_rate,
       b.table_flag
from org_list a
         left join qzrj_realtime_detail b on a.org_code = b.org_code
where a.is_516_flag = '是'
order by a.city, a.org_code;

-- 2必填字段完整性Sheet页明细
select a.city,
       a.org_code,
       a.org_name,
       b.table_name,
       b.table_comment,
       b.total_records,
       b.notnull_records,
       case
           when total_records is null then null
           when total_records = 0 then '-'
           else
               concat(b.notnull_rate, '%') end notnull_rate
from org_list a
    left join qzrj_column_level_1_detail b on a.org_code = b.org_code
where a.is_516_flag = '是'
order by a.city, a.org_code;

-- 3.重要建议填字段 sheet
select a.city,
       a.org_code,
       a.org_name,
       b.table_name,
       b.table_comment,
       b.total_records,
       b.notnull_records,
       case
           when total_records is null then null
           when total_records = 0 then '-'
           else
               concat(b.notnull_rate, '%') end notnull_rate
from org_list a
         left join qzrj_column_level_2_detail b on a.org_code = b.org_code
where a.is_516_flag = '是'
order by a.city, a.org_code;

-- 4.关联关系Sheet页明细
select a.city,a.org_code,a.org_name,
       b.table_name,
       b.table_comment,
       b.association_table,
       b.association_table_comment,
       b.total_records,
       b.association_records,
       case when total_records = 0 then '-'
           else
               concat( b.association_rate,'%')
           end association_rate
       from org_list a
    left join  qzrj_association_detail b on b.org_code = a.org_code
where a.is_516_flag ='是'
order by a.city,a.org_code;


-- 值域一致性Sheet页明细
select a.city,
       a.org_code,
       a.org_name,
       b.table_name,
       b.table_comment,
       b.field_name,
       b.field_comment,
       b.non_empty_violations,
       b.dict_violations,
       case
           when b.non_empty_violations is null then null
           when b.non_empty_violations = 0 then '-'
           else concat(b.dict_rate, '%') end dict_rate
from org_list a
         left join qzrj_dict_detail b on b.org_code = a.org_code
where a.is_516_flag = '是'
order by a.city, a.org_code;

-- 主诉Sheet页明细明细
select a.city,
       a.org_code,
       a.org_name,
       a.是否哨点,
       b.table_name,
       b.table_comment,
       b.field_name,
       b.field_comment,
       b.total_records,
       b.notnull_records,
       case
           when b.total_records = 0 then '-'
           else
               concat(b.notnull_rate, '%')
           end notnull_rate
from org_list a
         left join qzrj_chief_detail b on b.org_code = a.org_code and b.field_name = 'chief_complaint'
where a.is_516_flag = '是'
order by a.city, a.org_code;

--现病史Sheet页明细明细
select a.city,
       a.org_code,
       a.org_name,
       a.是否哨点,
       b.table_name,
       b.table_comment,
       b.field_name,
       b.field_comment,
       b.total_records,
       b.notnull_records,
       case
           when b.total_records = 0 then '-'
           else
               concat(b.notnull_rate, '%')
           end notnull_rate
from org_list a
         left join qzrj_chief_detail b on b.org_code = a.org_code and b.field_name = 'present_illness_his'
where a.is_516_flag = '是'
order by a.city, a.org_code;


-- 机构汇总Sheet页明细
--qzrj_realtime_org
select a.city,
       a.org_code,
       a.org_name,
       b.total_recods,
       b.compliance_records,
       case
           when b.total_recods is null then null
           when b.total_recods = 0 then '-'
           else concat(b.compliance_rate, '%') end  compliance_rate,
       c.total_recods,
       c.compliance_records,
       case
           when c.total_recods is null then null
           when c.total_recods = 0 then '-'
           else concat(c.compliance_rate, '%') end  compliance_rate,
       d.total_recods,
       d.compliance_records,
       case
           when d.total_recods is null then null
           when d.total_recods = 0 then '-'
           else concat(d.compliance_rate, '%') end  compliance_rate,
       e.total_records,
       e.notnull_records,
       case
           when e.total_records is null then null
           when e.total_records = 0 then '-'
           else concat(e.notnull_rate, '%') end     notnull_rate,
       f.total_records,
       f.notnull_records,
       case
           when f.total_records is null then null
           when f.total_records = 0 then '-'
           else concat(f.notnull_rate, '%') end     notnull_rate,
       g.total_records,
       g.notnull_records,
       case
           when g.total_records is null then null
           when g.total_records = 0 then '-'
           else concat(f.notnull_rate, '%') end     notnull_rate,
       h.total_records,
       h.notnull_records,
       case
           when h.total_records is null then null
           when h.total_records = 0 then '-'
           else concat(h.notnull_rate, '%') end     notnull_rate,
       i.total_records,
       i.association_records,
       case
           when i.total_records is null then null
           when i.total_records = 0 then '-'
           else concat(i.association_rate, '%') end association_rate,
       j.total_records,
       j.association_records,
       case
           when j.total_records is null then null
           when j.total_records = 0 then '-'
           else concat(j.association_rate, '%') end association_rate,
       k.total_records,
       k.association_records,
       case
           when k.total_records is null then null
           when k.total_records = 0 then '-'
           else concat(k.association_rate, '%') end association_rate,
       l.non_empty_violations,
       l.dict_violations,
       case when l.non_empty_violations is null then null
            when l.non_empty_violations = 0 then '-'
            else concat(l.dict_rate,'%') end dict_rate
from org_list a
         left join qzrj_realtime_org b on b.org_code = a.org_code and b.table_type = '实时表'
         left join qzrj_realtime_org c on c.org_code = a.org_code and c.table_type = '2小时内'
         left join qzrj_realtime_org d on d.org_code = a.org_code and d.table_type = 'T+0内'
         left join qzrj_column_level_org e on e.org_code = a.org_code and e.column_level = '1'
         left join qzrj_column_level_org f on f.org_code = a.org_code and f.column_level = '2'
         left join qzrj_column_level_org g on g.org_code = a.org_code and g.column_level = 'update_1'
         left join qzrj_column_level_org h on h.org_code = a.org_code and h.column_level = 'update_3'
         left join qzrj_association_org i on i.org_code = a.org_code and i.association_table = 'emr_patient_info'
         left join qzrj_association_org j on j.org_code = a.org_code and j.association_table = 'emr_activity_info'
         left join qzrj_association_org k on k.org_code = a.org_code and k.association_table = 'all'
         left join qzrj_dict_org l on l.org_code = a.org_code
where a.is_516_flag = '是'
order by a.city, a.org_code;

-- 地市州汇总Sheet页明细
select city,
       org_cnt,
       real_cnt,
       concat(round((real_cnt / org_cnt) * 100, 2), '%')                  as real_rate,
       hour_cnt,
       concat(round((hour_cnt / org_cnt) * 100, 2), '%')                  as hour_rate,
       other_cnt,
       concat(round((other_cnt / org_cnt) * 100, 2), '%')                 as other_rate,
       e_total_records,
       e_notnull_records,
       concat(round((e_notnull_records / e_total_records) * 100, 2), '%') as e_notnull_rate,
       f_total_records,
       f_notnull_records,
       concat(round((f_notnull_records / f_total_records) * 100, 2), '%') as f_notnull_rate,
       g_total_records,
       g_notnull_records,
       concat(round((g_notnull_records / g_total_records) * 100, 2), '%') as g_notnull_rate,
       h_total_records,
       h_notnull_records,
       concat(round((h_notnull_records / h_total_records) * 100, 2), '%') as h_notnull_rate,
       association_org_cnt,
       concat(round((association_org_cnt / org_cnt) * 100, 2), '%')       as association__rate,
       dict_org_cnt,
       concat(round((dict_org_cnt / org_cnt) * 100, 2), '%')              as dict_rate
from qzrj_city_summary a
union
select ':合计:'                                                                          city,
       sum(org_cnt),
       sum(real_cnt),
       concat(round((sum(real_cnt) / sum(org_cnt)) * 100, 2), '%')                  as real_rate,
       sum(hour_cnt)                                                                   hour_cnt,
       concat(round((sum(hour_cnt) / sum(org_cnt)) * 100, 2), '%')                  as hour_rate,
       sum(other_cnt)                                                                  other_cnt,
       concat(round((sum(other_cnt) / sum(org_cnt)) * 100, 2), '%')                 as other_rate,
       sum(e_total_records)                                                            e_total_records,
       sum(e_notnull_records)                                                          e_notnull_records,
       concat(round((sum(e_notnull_records) / sum(e_total_records)) * 100, 2), '%') as e_notnull_rate,
       sum(f_total_records)                                                            f_total_records,
       sum(f_notnull_records)                                                          f_notnull_records,
       concat(round((sum(f_notnull_records) / sum(f_total_records)) * 100, 2), '%') as f_notnull_rate,
       sum(g_total_records)                                                            g_total_records,
       sum(g_notnull_records)                                                          g_notnull_records,
       concat(round((sum(g_notnull_records) / sum(g_total_records)) * 100, 2), '%') as g_notnull_rate,
       sum(h_total_records)                                                            h_total_records,
       sum(h_notnull_records)                                                          h_notnull_records,
       concat(round((sum(h_notnull_records) / sum(h_total_records)) * 100, 2), '%') as h_notnull_rate,
       sum(association_org_cnt)                                                        association_org_cnt,
       concat(round((sum(association_org_cnt) / sum(org_cnt)) * 100, 2), '%')       as association__rate,
       sum(dict_org_cnt)                                                               dict_org_cnt,
       concat(round((sum(dict_org_cnt) / sum(org_cnt)) * 100, 2), '%')              as dict_rate
from qzrj_city_summary
order by city