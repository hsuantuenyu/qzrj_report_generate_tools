
-- 1.初始化表结构
drop table if exists quality_check_realtime;

create table if not exists quality_check_realtime
(
    "zone"          VARCHAR(0),
    org_code        INTEGER,
    org_name        VARCHAR(200),
    table_name      VARCHAR(50),
    table_comment   VARCHAR(100),
    timeliness_type VARCHAR(1),
    total_records HUGEINT,
    compliance_records HUGEINT,
    compliance_rate DOUBLE
)
comment on table quality_check_realtime is '前置软件时效性统计明细';
comment on column quality_check_realtime.zone is '地市(州)';
comment on column quality_check_realtime.org_code is '机构编码';
comment on column quality_check_realtime.org_name is '机构名称';
comment on column quality_check_realtime.table_name is '表名称';
comment on column quality_check_realtime.table_comment is '表注释';
comment on column quality_check_realtime.timeliness_type is '时效性类别';
comment on column quality_check_realtime.total_records is '纳入统计记录数';
comment on column quality_check_realtime.compliance_records is '合规记录数';
comment on column quality_check_realtime.compliance_rate is '合规率';

drop table if exists quality_realtime_org_sum;

create table if not exists quality_realtime_org_sum
(
    "zone"          VARCHAR(0),
    org_code        INTEGER,
    org_name        VARCHAR(0),
    timeliness_type VARCHAR(1),
    total_records HUGEINT,
    compliance_records HUGEINT,
    compliance_rate DOUBLE
);
comment on table quality_realtime_org_sum is '时效性机构汇总统计';
comment on column quality_realtime_org_sum.zone is '地市(州)';
comment on column quality_realtime_org_sum.org_code is '机构编码';
comment on column quality_realtime_org_sum.org_name is '机构名称';
comment on column quality_realtime_org_sum.timeliness_type is '时效性类别';
comment on column quality_realtime_org_sum.total_records is '纳入统计记录数';
comment on column quality_realtime_org_sum.compliance_records is '合规记录数';
comment on column quality_realtime_org_sum.compliance_rate is '合规率';

drop table if exists quality_column_level_detail;

create table if not exists quality_column_level_detail
(
    zone     VARCHAR(0),
    org_code   INTEGER,
    org_name   VARCHAR(0),
    table_name VARCHAR(0),
    table_comment VARCHAR(0),
    table_seq INTEGER,
    field_name VARCHAR(0),
    field_comment VARCHAR(0),
    field_seq INTEGER,
	column_level varchar(1),
	total_records HUGEINT,
    null_violations HUGEINT,
    notnull_records HUGEINT,
    notnull_rate DOUBLE
);

comment on table quality_column_level_detail is '字段完整性统计';
comment on column quality_column_level_detail.zone is '地市(州)';
comment on column quality_column_level_detail.org_code is '机构编码';
comment on column quality_column_level_detail.org_name is '机构名称';
comment on column quality_column_level_detail.table_name is '表名称';
comment on column quality_column_level_detail.table_comment is '表注释';
comment on column quality_column_level_detail.table_seq is '表顺序';
comment on column quality_column_level_detail.field_name is '列名称';
comment on column quality_column_level_detail.field_comment is '列注释';
comment on column quality_column_level_detail.field_seq is '列顺序';
comment on column quality_column_level_detail.column_level is '字段级别';
comment on column quality_column_level_detail.total_records is '纳入统计记录数';
comment on column quality_column_level_detail.null_violations is '空值记录数';
comment on column quality_column_level_detail.notnull_records is '非空值记录数';
comment on column quality_column_level_detail.notnull_rate is '非空率';



 
