# ReservationResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **int** | Unique ID of the reservation | 
**book_id** | **int** | ID of the reserved book | 
**book_title** | **str** | Title of the reserved book | [optional] 
**user_name** | **str** | Username of the reserver | 
**reservation_date** | **datetime** | UTC timestamp when reservation was created | 
**expires_at** | **datetime** | UTC timestamp when reservation expires | 
**status** | **str** | Status of reservation: &#39;active&#39;, &#39;cancelled&#39;, or &#39;expired&#39; | 

## Example

```python
from library_sdk.models.reservation_response import ReservationResponse

# TODO update the JSON string below
json = "{}"
# create an instance of ReservationResponse from a JSON string
reservation_response_instance = ReservationResponse.from_json(json)
# print the JSON string representation of the object
print(ReservationResponse.to_json())

# convert the object into a dict
reservation_response_dict = reservation_response_instance.to_dict()
# create an instance of ReservationResponse from a dict
reservation_response_from_dict = ReservationResponse.from_dict(reservation_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


