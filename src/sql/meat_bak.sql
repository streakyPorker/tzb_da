use tzbv1;
drop table if exists meat_bak;
create table meat_bak
(
    id                                INT primary key,
    manufacturer_name                 varchar(255),
    manufacturer_address              varchar(150),
    manufacturer_final_county         INT,
    manufacturer_final_prefecture     INT,
    manufacturer_final_province       INT,
    sampled_location_name             varchar(255),
    sampled_location_address          varchar(255),
    sampled_location_final_county     INT,
    sampled_location_final_prefecture INT,
    sampled_location_final_province   INT,
    food_name                         varchar(200),
    specifications_model              varchar(150),
    production_date                   varchar(10),
    production_year                   INT,
    product_classification            varchar(120),
    notice_number                     varchar(40),
    announcement_date                 varchar(10),
    announcement_year                 INT,
    task_source_or_project_name       varchar(100),
    testing_agency                    varchar(60),
    inspection_results                varchar(50),
    failing_results                   varchar(255),
    adulterant                        varchar(512),
    test_outcome                      varchar(50),
    legal_limit                       varchar(50),
    adulterant_english                varchar(100),
    adulterant_category               varchar(60),
    adulterant_sub_category           varchar(60),
    adulterant_intention              varchar(30),
    adulterant_possible_source        varchar(70),
    filename                          varchar(255),
    sheetname                         varchar(100),
    data_source_detailed              varchar(20),
    data_source_province              varchar(20),
    data_source_general               varchar(15),
    inspection_id                     INT,
    prod_category_english             varchar(100),
    prod_category_english_detailed    varchar(100),
    prod_category_english_nn          varchar(100),
    sampled_location_type             varchar(50),
    manufacturer_type                 varchar(70),
    mandate_level                     varchar(25),
    Failing                           boolean,
    fresh_aqua                        varchar(5),
    sampled_date                      varchar(10),
    web_source                        varchar(10)
);

# the transfer takes about 2GB of space, comment the line below if your buffer size is enough

insert into meat_bak
select * from meat;

# select count(id)
# from meat
# where sampled_location_type is not null
#   and manufacturer_type is not null;