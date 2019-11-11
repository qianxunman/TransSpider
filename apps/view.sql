create or replace view view_newst_info as (

with view_trans_last_info as (

    select row_number() over (partition by order_no order by create_time_trans desc ) as orderid,
       *
from trans_order_lines
)
 select * from view_trans_last_info where orderid = 1
);

--
-- select * from view_newst_info;


