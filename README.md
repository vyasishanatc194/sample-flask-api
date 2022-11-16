NPI Query API
=============

- This is a Micro Service that handles the Patients and Physician directories.
- It internally communicates with other Micro Services as well.

### Search by `NPI`

- `country` type `str` default `US` ; possible values `US, CA`
- `npi` type `int` required

#### Response pattern

```json
{"is_success": true, "data": [{}], "counts": 1, "country": "US"}
```


### Search by name


- `country` type `str` default `US` ; possible values `US, CA`
- `first_name` type `str` optional
- `last_name` type `str` optional
-  `name` type `str` optional
- `limit` type `int` default `10` optional ; max `100`
- `skip` type `int` default `0` optional


Note request must contain at least one of the following three parameters 
`name`, `first_name`, `last_name` .


#### Response type


```json
{"is_success": true, "counts": 5, "data": [{}, {}, {}, {}, {}],
 "country": "US", "limit": 10, "skip": 0}
``` 

