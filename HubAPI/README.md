API
==================

This API allows to access data on the IoTHub.

The table below is a summary of the API resources and operations.

|Resource|Method|Description|
|--------|------|-----------|
|users/:userid/adminKey| POST | Creates a key to access administrative functions.|
|queues/:userid/| GET | Gets all the queues of the user. |
|queues/:userid/| POST | Creates a new  queue. |
|queues/:userid/:queueid| GET | Gets all the transactions in the queue. |
|queues/:userid/:queueId| POST | Creates a transaction in the specified queue. |






