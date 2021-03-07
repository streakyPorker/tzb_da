select sampled_location_type, count(id)
from fruit_veg
where sampled_location_type is not null
group by sampled_location_type;


select *
from fruit_veg
limit 500;


select count(id)
from fruit_veg
where sampled_location_type is not null;


select adulterant_category, adulterant_sub_category, count(adulterant_sub_category) as cnt
from fruit_veg f
where adulterant_category is not null
  and Failing is true
  and adulterant_sub_category is not null
group by adulterant_category, adulterant_sub_category
having count(adulterant_sub_category) >= 100
order by adulterant_category, count(adulterant_sub_category) desc;


select Failing, count(id)
from origin_data
where prod_category_english_nn like 'meat and meat product'
group by Failing;


#
select adulterant_category, adulterant_sub_category, count(adulterant_sub_category) as cnt
from origin_data
where adulterant_category is not null
  and Failing is true
  and adulterant_sub_category is not null
  and prod_category_english_nn like 'meat and meat product'
group by adulterant_category, adulterant_sub_category
# having count(adulterant_sub_category) >= 100
order by adulterant_category, count(adulterant_sub_category) desc;



select count(id)
from fruit_veg
where sampled_location_type is not null
  and manufacturer_type is not null;

select count(id)
from fruit_veg
where sampled_location_type is not null
   or manufacturer_type is not null;



# 以下2个查询，查询果蔬检测数量在sampled_location_type和 manufacturer_type上的分布
# 查询果蔬检测数量在sampled_location_type上的分布
select sampled_location_type, count(id)
from fruit_veg
where sampled_location_type is not null
group by sampled_location_type
order by count(id) DESC;

select manufacturer_type, count(id)
from fruit_veg
where manufacturer_type is not null
group by manufacturer_type
order by count(id) DESC;

select sampled_location_type, count(id)
from fruit_veg
where sampled_location_type is not null
  and Failing is true
group by sampled_location_type;

select sampled_location_name,food_name,specifications_model,sampled_location_type
from fruit_veg
where sampled_location_type is not null
and specifications_model like '%_/_%';

# 散 非定量



