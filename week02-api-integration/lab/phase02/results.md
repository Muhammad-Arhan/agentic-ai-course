# Phase 02 - recorded API requests (Tasks 06-10)

## Task 06 - GET

- HTTP method: `GET`
- Endpoint: `/posts/1`
- Status code: `200`

Response body:
```json
{
  "userId": 1,
  "id": 1,
  "title": "sunt aut facere repellat provident occaecati excepturi optio reprehenderit",
  "body": "quia et suscipit\nsuscipit recusandae consequuntur expedita et cum\nreprehenderit molestiae ut ut quas totam\nnostrum rerum est autem sunt rem eveniet architecto"
}
```

## Task 06 - GET

- HTTP method: `GET`
- Endpoint: `/posts/2`
- Status code: `200`

Response body:
```json
{
  "userId": 1,
  "id": 2,
  "title": "qui est esse",
  "body": "est rerum tempore vitae\nsequi sint nihil reprehenderit dolor beatae ea dolores neque\nfugiat blanditiis voluptate porro vel nihil molestiae ut reiciendis\nqui aperiam non debitis possimus qui neque nisi nulla"
}
```

## Task 06 - GET

- HTTP method: `GET`
- Endpoint: `/posts/3`
- Status code: `200`

Response body:
```json
{
  "userId": 1,
  "id": 3,
  "title": "ea molestias quasi exercitationem repellat qui ipsa sit aut",
  "body": "et iusto sed quo iure\nvoluptatem occaecati omnis eligendi aut ad\nvoluptatem doloribus vel accusantium quis pariatur\nmolestiae porro eius odio et labore et velit aut"
}
```

## Task 07 - POST

- HTTP method: `POST`
- Endpoint: `/posts`
- Status code: `201`

Request body:
```json
{
  "title": "My API Lab",
  "body": "Testing POST request",
  "userId": 1
}
```

Response body:
```json
{
  "title": "My API Lab",
  "body": "Testing POST request",
  "userId": 1,
  "id": 101
}
```

## Task 08 - PUT

- HTTP method: `PUT`
- Endpoint: `/posts/1`
- Status code: `200`

Request body:
```json
{
  "id": 1,
  "title": "Updated title",
  "body": "Updated by my API lab",
  "userId": 1
}
```

Response body:
```json
{
  "id": 1,
  "title": "Updated title",
  "body": "Updated by my API lab",
  "userId": 1
}
```

## Task 09 - DELETE

- HTTP method: `DELETE`
- Endpoint: `/posts/1`
- Status code: `200`

Response body:
```json
{}
```

## Task 10 - 404 test

- HTTP method: `GET`
- Endpoint: `/posts/9999`
- Status code: `404`

Response body:
```json
{}
```
