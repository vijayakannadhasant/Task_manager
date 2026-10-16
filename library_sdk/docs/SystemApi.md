# library_sdk.SystemApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**health_check**](SystemApi.md#health_check) | **GET** /health | Health check
[**root_info**](SystemApi.md#root_info) | **GET** / | Root service info


# **health_check**
> object health_check()

Health check

Health check endpoint to verify backend service liveness.

### Example


```python
import library_sdk
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
    api_instance = library_sdk.SystemApi(api_client)

    try:
        # Health check
        api_response = api_instance.health_check()
        print("The response of SystemApi->health_check:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling SystemApi->health_check: %s\n" % e)
```



### Parameters

This endpoint does not need any parameter.

### Return type

**object**

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

# **root_info**
> object root_info()

Root service info

Root info redirecting users to docs.

### Example


```python
import library_sdk
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
    api_instance = library_sdk.SystemApi(api_client)

    try:
        # Root service info
        api_response = api_instance.root_info()
        print("The response of SystemApi->root_info:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling SystemApi->root_info: %s\n" % e)
```



### Parameters

This endpoint does not need any parameter.

### Return type

**object**

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

