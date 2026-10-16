# library_sdk.BooksApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**create_book**](BooksApi.md#create_book) | **POST** /books/ | Add a new book
[**get_book**](BooksApi.md#get_book) | **GET** /books/{book_id} | Retrieve book details
[**list_books**](BooksApi.md#list_books) | **GET** /books/ | Retrieve all books
[**reserve_book**](BooksApi.md#reserve_book) | **POST** /books/{book_id}/reserve | Reserve a book copy


# **create_book**
> BookResponse create_book(book_create)

Add a new book

Create a new book with specified title, author, and total copies.

### Example


```python
import library_sdk
from library_sdk.models.book_create import BookCreate
from library_sdk.models.book_response import BookResponse
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
    api_instance = library_sdk.BooksApi(api_client)
    book_create = library_sdk.BookCreate() # BookCreate | 

    try:
        # Add a new book
        api_response = api_instance.create_book(book_create)
        print("The response of BooksApi->create_book:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling BooksApi->create_book: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **book_create** | [**BookCreate**](BookCreate.md)|  | 

### Return type

[**BookResponse**](BookResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**201** | Successful Response |  -  |
**422** | Validation error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_book**
> BookResponse get_book(book_id)

Retrieve book details

Retrieve details of a specific book by ID, including current available copies.

### Example


```python
import library_sdk
from library_sdk.models.book_response import BookResponse
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
    api_instance = library_sdk.BooksApi(api_client)
    book_id = 56 # int | Unique integer ID of the book

    try:
        # Retrieve book details
        api_response = api_instance.get_book(book_id)
        print("The response of BooksApi->get_book:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling BooksApi->get_book: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **book_id** | **int**| Unique integer ID of the book | 

### Return type

[**BookResponse**](BookResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**404** | Book not found |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **list_books**
> List[BookResponse] list_books()

Retrieve all books

List all books in the catalog along with up-to-date available copies. Automatically processes expired reservations before returning counts.

### Example


```python
import library_sdk
from library_sdk.models.book_response import BookResponse
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
    api_instance = library_sdk.BooksApi(api_client)

    try:
        # Retrieve all books
        api_response = api_instance.list_books()
        print("The response of BooksApi->list_books:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling BooksApi->list_books: %s\n" % e)
```



### Parameters

This endpoint does not need any parameter.

### Return type

[**List[BookResponse]**](BookResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **reserve_book**
> ReservationResponse reserve_book(book_id, reservation_create)

Reserve a book copy

Reserve an available copy of a book for a named user. Decrements available copies by 1. Expires after 7 days.

### Example


```python
import library_sdk
from library_sdk.models.reservation_create import ReservationCreate
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
    api_instance = library_sdk.BooksApi(api_client)
    book_id = 56 # int | Unique integer ID of the book
    reservation_create = library_sdk.ReservationCreate() # ReservationCreate | 

    try:
        # Reserve a book copy
        api_response = api_instance.reserve_book(book_id, reservation_create)
        print("The response of BooksApi->reserve_book:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling BooksApi->reserve_book: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **book_id** | **int**| Unique integer ID of the book | 
 **reservation_create** | [**ReservationCreate**](ReservationCreate.md)|  | 

### Return type

[**ReservationResponse**](ReservationResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**201** | Successful Response |  -  |
**400** | No copies available or invalid request |  -  |
**404** | Book not found |  -  |
**422** | Validation error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

