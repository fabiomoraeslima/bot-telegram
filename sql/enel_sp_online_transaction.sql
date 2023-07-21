set session my.vars.enelsp = 23; -- ENELSP
set session my.vars.gap_enelsp = '00:35:00';
set session my.vars.gap_default = '00:30:00';
set session my.vars.gap_warn_madr = '00:40:00';
set session my.vars.gap_madrugada = '00:59:00';
set session my.vars.channel = 'WEB';

select r.name
          ,case when (cast(to_char(now(), 'yyyy-mm-dd hh24:mi:ss') as time) between '07:00:00' and '23:59:59.999')
                                                 and cast (r.gap_time as time) > current_setting('my.vars.gap_default')::time
                                                     and cast (r.gap_time as time) < current_setting('my.vars.gap_enelsp')::time
                        then 1 --Warning
                        when (cast(to_char(now(), 'yyyy-mm-dd hh24:mi:ss') as time) between '07:00:00' and '23:59:59.999')
                                                         and cast(r.gap_time as time) > current_setting('my.vars.gap_enelsp')::time
                        then 0 -- Alarme
                        when (cast(to_char(now(), 'yyyy-mm-dd hh24:mi:ss') as time) between '00:00:00' and '06:59:59.999')
                                                        and cast (r.gap_time as time) > current_setting('my.vars.gap_warn_madr')::time
                                                     and cast (r.gap_time as time) < current_setting('my.vars.gap_madrugada')::time
                        then 2 --Warning ** celpe nao monitora de madrugda
                        when (cast(to_char(now(), 'yyyy-mm-dd hh24:mi:ss') as time) between '00:00:00' and '06:59:59.999')
                                                             and cast (r.gap_time as time) > current_setting('my.vars.gap_madrugada')::time
                        then 0 -- Alarme ** celpe nao monitora de madrugda
                        else 2 -- okay
           end valida_gap_time
        ,case when (cast(to_char(now(), 'yyyy-mm-dd hh24:mi:ss') as time) between '07:00:00' and '18:59:59.999')
                                 then 'diurno'
                                 when (cast(to_char(now(), 'yyyy-mm-dd hh24:mi:ss') as time) between '19:00:00' and '23:59:59.999')
                                 then 'noite'
                                 when (cast(to_char(now(), 'yyyy-mm-dd hh24:mi:ss') as time) between '00:00:00' and '06:59:59.999')
                                 then  'madrugada'
                 end turno
        ,substring(cast(cast(r.created_at as time) as varchar(20)),1,8) created_at
                ,substring(cast(cast(r.gap_time as time) as varchar(20)),1,8) gap_time
                ,to_char(now(), 'yyyy-mm-dd hh24:mi:ss') as date_time
from (
select      max(p.created_at)::timestamp created_at
                   ,cast ((now()::timestamp - max(p.created_at)::timestamp) as time) as gap_time
                   ,c.name
                   ,p.company_id id
        from purchase p
           join company c on p.company_id = c.id
           where p.purchase_channel = current_setting('my.vars.channel')
           and p.created_at > now()::date -interval '2 day'
           and p.status = 2
           and c.id in (current_setting('my.vars.enelsp')::int
                                        )
group by c.name
            ,p.company_id
        ) r
;
