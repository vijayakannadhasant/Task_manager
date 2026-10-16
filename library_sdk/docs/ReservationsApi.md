# library_sdk.ReservationsApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**cancel_reservation**](ReservationsApi.md#cancel_reservation) | **DELETE** /reservations/{reservation_id} | Cancel a reservation
[**list_reservations**](ReservationsApi.md#list_reservations) | **GET** /reservations/ | List all reservations


# **cancel_reservation**
> ReservationResponse cancel_reservation(reservation_id)

Cancel a reservation

Cancel an active reservation. Restores exactly 1 copy to the book's inventory. Fails if already cancelled or expired.

### Example


```python
import library_sdk
from library_sdk.models.reservation_response import ReservationResponse
from library_sdk.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = library_sdk.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
with library_sdk.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = library_sdk.ReservationsApi(api_client)
    reservation_id = 56 # int | Unique integer ID of the reservation

    try:
        # Cancel a reservation
        api_response = api_instance.cancel_reservation(reservation_id)
        print("The response of ReservationsApi->cancel_reservation:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ReservationsApi->cancel_reservation: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **reservation_id** | **int**| Unique integer ID of the reservation | 

### Return type

[**ReservationResponse**](ReservationResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**400** | Reservation is already cancelled or expired |  -  |
**404** | Reservation not found |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **list_reservations**
> List[ReservationResponse] list_reservations(book_id=book_id, status=status)

List all reservations

Retrieve all reservations with optional filtering by status (active, cancelled, expired) or book_id. Automatically updates expired statuses.

### Example


```python
import library_sdk
from library_sdk.models.reservation_response import ReservationResponse
from library_sdk.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = library_sdk.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
with library_sdk.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = library_sdk.ReservationsApi(api_client)
    book_id = 56 # int | Optional book ID filter (optional)
    status = 'status_example' # str | Optional status filter: active, cancelled, expired (optional)

    try:
        # List all reservations
        api_response = api_instance.list_reservations(book_id=book_id, status=status)
        print("The response of ReservationsApi->list_reservations:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ReservationsApi->list_reservations: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **book_id** | **int**| Optional book ID filter | [optional] 
 **status** | **str**| Optional status filter: active, cancelled, expired | [optional] 

### Return type

[**List[ReservationResponse]**](ReservationResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

