# ReservationCreate


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**user_name** | **str** | Username of the person reserving the book | 

## Example

```python
from library_sdk.models.reservation_create import ReservationCreate

# TODO update the JSON string below
json = "{}"
# create an instance of ReservationCreate from a JSON string
reservation_create_instance = ReservationCreate.from_json(json)
# print the JSON string representation of the object
print(ReservationCreate.to_json())

# convert the object into a dict
reservation_create_dict = reservation_create_instance.to_dict()
# create an instance of ReservationCreate from a dict
reservation_create_from_dict = ReservationCreate.from_dict(reservation_create_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


