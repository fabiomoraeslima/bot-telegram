set session my.vars.light = 21; -- LIGHT
set session my.vars.enelsp = 23; -- ENELSP
set session my.vars.channel = 'WEB';
set session my.vars.status = '2';

select f.purchase_channel
          ,f.name
          ,cast(f.created_at as date) date
          ,substring(cast(cast(f.created_at as time) as varchar(20)),1,8) hora          ,case when (cast(f.created_at as time) between '07:00:00' and '18:59:59.999')
                                 then 'diurno'
                                 when (cast(f.created_at as time) between '19:00:00' and '23:59:59.999')
                                 then 'noite'
                                 when (cast(f.created_at as time) between '00:00:00' and '06:59:59.999')
                                 then  'madrugada'
                 end turno
           ,f.gap_time
           ,(extract(epoch from f.gap_time::time) * (1.0/3600.0)) gap_time_decimal
from (

 select r.id
          ,r.purchase_channel
          ,r.name
      ,r.created_at
          ,max(t.id)
          ,max(t.created_at)
          ,to_char ((r.created_at::timestamp - max(t.created_at)::timestamp),'hh24:mm:ss')::time as gap_time
 from (
 select p.id
           ,p.purchase_channel
           ,c.name
           ,p.created_at
           from purchase p
           join company c on p.company_id = c.id
           where p.purchase_channel = current_setting('my.vars.channel')
           and p.created_at > now() - interval '72 hours'
           and p.status = current_setting('my.vars.status')::int
           and c.id in (current_setting('my.vars.enelsp')::int)
order by p.created_at desc
--limit 10
) r join (select p.id
           ,p.purchase_channel
           ,c.name
           ,p.created_at
           from purchase p
           join company c on p.company_id = c.id
           where p.purchase_channel = current_setting('my.vars.channel')
           and p.created_at > now() - interval '72 hours'
           and p.status = current_setting('my.vars.status')::int
           and c.id = current_setting('my.vars.enelsp')::int
order by p.created_at desc
 ) as t on t.id < r.id
group by 1,2,3,4
 ) f
