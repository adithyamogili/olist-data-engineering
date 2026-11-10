select
    p.product_id,
    coalesce(t.product_category_name_english, p.product_category_name, 'unknown') as product_category,
    cast(p.product_name_lenght as integer) as product_name_length,
    cast(p.product_description_lenght as integer) as product_description_length,
    cast(p.product_photos_qty as integer) as product_photos_qty,
    cast(p.product_weight_g as integer) as product_weight_g,
    cast(p.product_length_cm as integer) as product_length_cm,
    cast(p.product_height_cm as integer) as product_height_cm,
    cast(p.product_width_cm as integer) as product_width_cm
from {{ source('bronze', 'products') }} p
left join {{ source('bronze', 'category_translation') }} t
    on p.product_category_name = t.product_category_name
