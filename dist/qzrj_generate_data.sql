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

insert into qzrj_column_level_org
select a.city,
       a.org_code,
       a.org_name,
       '3' column_level,
       sum(a.total_records)                                                        total_records,
       sum(a.notnull_records)                                                      notnull_records,
       case
           when sum(a.total_records) > 0 then
               round((sum(a.notnull_records) / sum(a.total_records)) * 100, 2) end notnull_rate
from qzrj_column_level_3_detail a
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
where a.column_level = '3'
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
where a.column_level = '1'
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

truncate table qzrj_city_summary;
insert into qzrj_city_summary
select a.city,count(a.org_code) org_cnt,
       sum(case when b.compliance_rate >=90 then 1 else 0 end) real_cnt,
       sum(case when c.compliance_rate >=100 then 1 else 0 end ) hour_cnt,
       sum(case when d.compliance_rate >=100 then 1 else 0 end) other_cnt,
       sum(e.total_records) e_total_records,
       sum(e.notnull_records) e_notnull_records,
       sum(f.total_records) f_total_records,
       sum(f.notnull_records) f_notnull_records,
       sum(g.total_records) g_total_records,
       sum(g.notnull_records) g_notnull_records,
       sum(h.total_records) h_total_records,
       sum(h.notnull_records) h_notnull_records,
       sum(i.total_records) i_total_records,
       sum(i.notnull_records) i_notnull_records,
       sum(case when j.association_rate >=90 then 1 else 0 end) association_org_cnt,
       sum(case when k.dict_rate >=100 then 1 else 0 end) dict_org_cnt
from org_list a
 left join qzrj_realtime_org b on b.org_code = a.org_code and b.table_type = '实时表'
         left join qzrj_realtime_org c on c.org_code = a.org_code and c.table_type = '2小时内'
         left join qzrj_realtime_org d on d.org_code = a.org_code and d.table_type = 'T+0内'
         left join qzrj_column_level_org e on e.org_code = a.org_code and e.column_level = '1'
         left join qzrj_column_level_org f on f.org_code = a.org_code and f.column_level = '2'
         left join qzrj_column_level_org g on g.org_code = a.org_code and g.column_level = '3'
         left join qzrj_column_level_org h on h.org_code = a.org_code and h.column_level = 'update_1'
         left join qzrj_column_level_org i on i.org_code = a.org_code and i.column_level = 'update_3'
         left join qzrj_association_org j on j.org_code = a.org_code and j.association_table = 'all'
         left join qzrj_dict_org k on k.org_code = a.org_code
   where a.is_516_flag = '是'
group by a.city;