{{
    config(
        materialized="external",
        location="staging/asana__users.parquet",
    )
}}

{# 
    We can write this out to S3/GCS if we want. The key is that
    this happens AFTER the python model pulls the data and the
    subsequent data tests defined in our YAML file pass. You can
    think of the YAML file as a test suite against your extract
    but BEFORE your load. Hence, EtLT where t is for test without
    fudging with great expectations. Decent idea? I think so.

    Furthermore we can actually transform the data here if we want,
    split a single load into multiple nodes which materialize in
    different locations, etc. If we extrapolate, we can think of
    implementing a Data Vault style architecture AS THE DATA IS
    IN FLIGHT. Interesting. If only as a thought experiment.
 #}
select *
from {{ ref("asana__users__extract") }}
