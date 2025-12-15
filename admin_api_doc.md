# 网易云音乐项目管理员接口文档

## 接口概述
本文档描述了网易云音乐项目中管理员模块的所有接口，包括接口URL、请求方法、请求参数、响应格式等详细信息。

## 接口基础信息
- 接口前缀：`/admin`
- 认证方式：Session认证
- 响应格式：JSON，统一包含`code`、`msg`和`data`字段

## 1. 管理员登录接口

### 接口信息
- URL: `/admin/login`
- 方法: `POST`
- 功能: 管理员登录系统

### 请求参数
| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| username | String | 是 | 用户名 |
| password | String | 是 | 密码 |

### 响应格式

#### 成功响应 (200 OK)
```json
{
  "code": 200,
  "msg": "登录成功",
  "data": {
    "user_id": 1,
    "username": "admin",
    "is_admin": 1
  }
}
```

#### 失败响应
- **401 Unauthorized**: 用户名或密码错误
```json
{
  "code": 401,
  "msg": "用户名或密码错误",
  "data": null
}
```

- **403 Forbidden**: 没有管理员权限
```json
{
  "code": 403,
  "msg": "没有管理员权限",
  "data": null
}
```

- **500 Internal Server Error**: 系统错误
```json
{
  "code": 500,
  "msg": "系统错误，请稍后重试",
  "data": null
}
```

## 2. 管理员退出登录接口

### 接口信息
- URL: `/admin/logout`
- 方法: `POST`
- 功能: 管理员退出登录，清除会话

### 请求参数
无

### 响应格式

#### 成功响应 (200 OK)
```json
{
  "code": 200,
  "msg": "退出登录成功",
  "data": null
}
```

#### 失败响应
- **500 Internal Server Error**: 系统错误
```json
{
  "code": 500,
  "msg": "系统错误，请稍后重试",
  "data": null
}
```

## 3. 获取当前登录管理员信息接口

### 接口信息
- URL: `/admin/me`
- 方法: `GET`
- 功能: 获取当前登录管理员的详细信息
- 权限: 管理员

### 请求参数
无

### 响应格式

#### 成功响应 (200 OK)
```json
{
  "code": 200,
  "msg": "获取管理员信息成功",
  "data": {
    "id": 1,
    "username": "admin",
    "netease_user_id": "123456",
    "status": 1,
    "is_admin": 1,
    "create_time": "2023-01-01 00:00:00",
    "update_time": "2023-01-01 00:00:00"
  }
}
```

#### 失败响应
- **401 Unauthorized**: 请先登录
```json
{
  "code": 401,
  "msg": "请先登录",
  "data": null
}
```

- **404 Not Found**: 管理员不存在
```json
{
  "code": 404,
  "msg": "管理员不存在",
  "data": null
}
```

- **500 Internal Server Error**: 系统错误
```json
{
  "code": 500,
  "msg": "系统错误，请稍后重试",
  "data": null
}
```

## 4. 修改管理员信息接口

### 接口信息
- URL: `/admin/profile`
- 方法: `PUT`
- 功能: 修改当前登录管理员的名称和密码
- 权限: 管理员

### 请求参数
| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| username | String | 否 | 新的管理员名称 |
| password | String | 否 | 新的管理员密码 |

### 响应格式

#### 成功响应 (200 OK)
```json
{
  "code": 200,
  "msg": "修改管理员信息成功",
  "data": null
}
```

#### 失败响应
- **400 Bad Request**: 请求参数错误
```json
{
  "code": 400,
  "msg": "用户名已存在",
  "data": null
}
```

```json
{
  "code": 400,
  "msg": "密码不能为空",
  "data": null
}
```

- **401 Unauthorized**: 请先登录
```json
{
  "code": 401,
  "msg": "请先登录",
  "data": null
}
```

- **404 Not Found**: 管理员不存在
```json
{
  "code": 404,
  "msg": "管理员不存在",
  "data": null
}
```

- **500 Internal Server Error**: 系统错误
```json
{
  "code": 500,
  "msg": "系统错误，请稍后重试",
  "data": null
}
```

## 5. 获取所有用户列表接口

### 接口信息
- URL: `/admin/users`
- 方法: `GET`
- 功能: 获取所有用户列表（分页查询）
- 权限: 管理员

### 请求参数
| 参数名 | 类型 | 必填 | 默认值 | 描述 |
|--------|------|------|--------|------|
| current | Integer | 否 | 1 | 当前页码 |
| size | Integer | 否 | 10 | 每页记录数 |
| is_admin | Integer | 否 | - | 是否管理员，0表示普通用户，1表示管理员 |

### 响应格式

#### 成功响应 (200 OK)
```json
{
  "code": 200,
  "msg": "获取用户列表成功",
  "data": {
    "records": [
      {
        "id": 1,
        "username": "admin",
        "netease_user_id": "123456",
        "status": 1,
        "is_admin": 1,
        "create_time": "2023-01-01 00:00:00"
      },
      // ... 更多用户
    ],
    "current": 1,
    "size": 10,
    "total": 100,
    "pages": 10
  }
}
```

#### 失败响应
- **401 Unauthorized**: 请先登录
```json
{
  "code": 401,
  "msg": "请先登录",
  "data": null
}
```

- **500 Internal Server Error**: 系统错误
```json
{
  "code": 500,
  "msg": "系统错误，请稍后重试",
  "data": null
}
```

## 6. 根据多条件搜索用户接口

### 接口信息
- URL: `/admin/users/search`
- 方法: `GET`
- 功能: 根据多条件搜索用户（分页查询）
- 权限: 管理员

### 请求参数
| 参数名 | 类型 | 必填 | 默认值 | 描述 |
|--------|------|------|--------|------|
| username | String | 否 | - | 搜索的用户名关键字（支持模糊搜索） |
| netease_user_id | String | 否 | - | 搜索的网易云用户ID |
| status | Integer | 否 | - | 搜索的用户状态（0-禁用，1-启用） |
| is_admin | Integer | 否 | - | 是否管理员，0表示普通用户，1表示管理员 |
| current | Integer | 否 | 1 | 当前页码 |
| size | Integer | 否 | 10 | 每页记录数 |

> 说明：至少需要提供一个搜索条件（用户名、网易云ID、状态或是否管理员）

### 响应格式

#### 成功响应 (200 OK)
```json
{
  "code": 200,
  "msg": "搜索用户成功",
  "data": {
    "records": [
      {
        "id": 1,
        "username": "admin_new",
        "netease_user_id": "123456789",
        "status": 1,
        "is_admin": 1,
        "create_time": "2023-01-01 12:00:00"
      }
    ],
    "current": 1,
    "size": 10,
    "total": 1,
    "pages": 1
  }
}
```

#### 失败响应
- **401 Unauthorized**: 请先登录
```json
{
  "code": 401,
  "msg": "请先登录",
  "data": null
}
```

- **500 Internal Server Error**: 系统错误
```json
{
  "code": 500,
  "msg": "系统错误，请稍后重试",
  "data": null
}
```

## 7. 获取单个用户信息接口

### 接口信息
- URL: `/admin/users/<int:user_id>`
- 方法: `GET`
- 功能: 获取指定用户的详细信息
- 权限: 管理员

### 请求参数
| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| user_id | Integer | 是 | 用户ID |

### 响应格式

#### 成功响应 (200 OK)
```json
{
  "code": 200,
  "msg": "获取用户信息成功",
  "data": {
    "id": 1,
    "username": "admin",
    "netease_user_id": "123456",
    "status": 1,
    "is_admin": 1,
    "create_time": "2023-01-01 00:00:00",
    "update_time": "2023-01-01 00:00:00"
  }
}
```

#### 失败响应
- **401 Unauthorized**: 请先登录
```json
{
  "code": 401,
  "msg": "请先登录",
  "data": null
}
```

- **404 Not Found**: 用户不存在
```json
{
  "code": 404,
  "msg": "用户不存在",
  "data": null
}
```

- **500 Internal Server Error**: 系统错误
```json
{
  "code": 500,
  "msg": "系统错误，请稍后重试",
  "data": null
}
```

## 8. 添加用户接口

### 接口信息
- URL: `/admin/users`
- 方法: `POST`
- 功能: 管理员添加新用户
- 权限: 管理员

### 请求参数
| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| username | String | 是 | 用户名 |
| password | String | 是 | 密码 |
| netease_user_id | String | 是 | 网易云用户ID |

### 响应格式

#### 成功响应 (200 OK)
```json
{
  "code": 200,
  "msg": "添加用户成功",
  "data": {
    "id": 3,
    "username": "newuser",
    "netease_user_id": "789012",
    "status": 1,
    "is_admin": 0,
    "create_time": "2023-01-02 00:00:00"
  }
}
```

#### 失败响应
- **400 Bad Request**: 请求参数错误
```json
{
  "code": 400,
  "msg": "用户名已存在",
  "data": null
}
```

- **401 Unauthorized**: 请先登录
```json
{
  "code": 401,
  "msg": "请先登录",
  "data": null
}
```

- **500 Internal Server Error**: 系统错误
```json
{
  "code": 500,
  "msg": "系统错误，请稍后重试",
  "data": null
}
```

## 9. 聚合修改用户信息接口

### 接口信息
- URL: `/admin/users/<int:user_id>`
- 方法: `PUT`
- 功能: 管理员聚合修改指定用户的信息，支持同时修改多个字段或单独修改某个字段
- 权限: 管理员

### 请求参数
| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| user_id | Integer | 是 | 用户ID |
| username | String | 否 | 用户名 |
| password | String | 否 | 密码 |
| netease_user_id | String | 否 | 网易云用户ID，支持设置为空字符串以清空该字段 |
| is_admin | Integer | 否 | 是否管理员，0表示普通用户，1表示管理员 |
| status | Integer | 否 | 用户状态，0表示封禁，1表示正常 |

### 响应格式

#### 成功响应 (200 OK)
```json
{
  "code": 200,
  "msg": "修改用户信息成功",
  "data": {
    "id": 1,
    "username": "updateduser",
    "netease_user_id": "123456",
    "status": 1,
    "is_admin": 1,
    "create_time": "2023-01-01 00:00:00",
    "update_time": "2023-01-02 00:00:00"
  }
}```

#### 失败响应
- **400 Bad Request**: 请求参数错误
```json
{
  "code": 400,
  "msg": "用户名已存在",
  "data": null
}
```

- **401 Unauthorized**: 请先登录
```json
{
  "code": 401,
  "msg": "请先登录",
  "data": null
}
```

- **404 Not Found**: 用户不存在
```json
{
  "code": 404,
  "msg": "用户不存在",
  "data": null
}
```

- **500 Internal Server Error**: 系统错误
```json
{
  "code": 500,
  "msg": "系统错误，请稍后重试",
  "data": null
}
```

## 10. 删除用户接口

### 接口信息
- URL: `/admin/users/<int:user_id>`
- 方法: `DELETE`
- 功能: 管理员删除指定用户
- 权限: 管理员

### 请求参数
| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| user_id | Integer | 是 | 用户ID |

### 响应格式

#### 成功响应 (200 OK)
```json
{
  "code": 200,
  "msg": "删除用户成功",
  "data": null
}
```

#### 失败响应
- **400 Bad Request**: 请求参数错误
```json
{
  "code": 400,
  "msg": "不能删除自己",
  "data": null
}
```

- **401 Unauthorized**: 请先登录
```json
{
  "code": 401,
  "msg": "请先登录",
  "data": null
}
```

- **404 Not Found**: 用户不存在
```json
{
  "code": 404,
  "msg": "用户不存在",
  "data": null
}
```

- **500 Internal Server Error**: 系统错误
```json
{
  "code": 500,
  "msg": "系统错误，请稍后重试",
  "data": null
}
```

## 11. 封禁用户接口

### 接口信息
- URL: `/admin/users/<int:user_id>/ban`
- 方法: `PUT`
- 功能: 管理员封禁指定用户
- 权限: 管理员

### 请求参数
| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| user_id | Integer | 是 | 用户ID |

### 响应格式

#### 成功响应 (200 OK)
```json
{
  "code": 200,
  "msg": "封禁用户成功",
  "data": null
}
```

#### 失败响应
- **400 Bad Request**: 不能封禁自己
```json
{
  "code": 400,
  "msg": "不能封禁自己",
  "data": null
}
```

- **401 Unauthorized**: 请先登录
```json
{
  "code": 401,
  "msg": "请先登录",
  "data": null
}
```

- **404 Not Found**: 用户不存在
```json
{
  "code": 404,
  "msg": "用户不存在",
  "data": null
}
```

- **500 Internal Server Error**: 系统错误
```json
{
  "code": 500,
  "msg": "系统错误，请稍后重试",
  "data": null
}
```

## 12. 解封用户接口

### 接口信息
- URL: `/admin/users/<int:user_id>/unban`
- 方法: `PUT`
- 功能: 管理员解封指定用户
- 权限: 管理员

### 请求参数
| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| user_id | Integer | 是 | 用户ID |

### 响应格式

#### 成功响应 (200 OK)
```json
{
  "code": 200,
  "msg": "解放用户成功",
  "data": null
}
```

#### 失败响应
- **401 Unauthorized**: 请先登录
```json
{
  "code": 401,
  "msg": "请先登录",
  "data": null
}
```

- **404 Not Found**: 用户不存在
```json
{
  "code": 404,
  "msg": "用户不存在",
  "data": null
}
```

- **500 Internal Server Error**: 系统错误
```json
{
  "code": 500,
  "msg": "系统错误，请稍后重试",
  "data": null
}
```

## 13. 设置用户为管理员接口

### 接口信息
- URL: `/admin/users/<int:user_id>/set_admin`
- 方法: `PUT`
- 功能: 管理员将指定用户设置为管理员
- 权限: 管理员

### 请求参数
| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| user_id | Integer | 是 | 用户ID |

### 响应格式

#### 成功响应 (200 OK)
```json
{
  "code": 200,
  "msg": "设置用户为管理员成功",
  "data": null
}
```

#### 失败响应
- **401 Unauthorized**: 请先登录
```json
{
  "code": 401,
  "msg": "请先登录",
  "data": null
}
```

- **404 Not Found**: 用户不存在
```json
{
  "code": 404,
  "msg": "用户不存在",
  "data": null
}
```

- **500 Internal Server Error**: 系统错误
```json
{
  "code": 500,
  "msg": "系统错误，请稍后重试",
  "data": null
}
```

## 14. 解除管理员权限接口

### 接口信息
- URL: `/admin/users/<int:user_id>/remove-admin`
- 方法: `PUT`
- 功能: 管理员解除指定用户的管理员权限
- 权限: 管理员

### 请求参数
| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| user_id | Integer | 是 | 用户ID |

### 响应格式

#### 成功响应 (200 OK)
```json
{
  "code": 200,
  "msg": "解除用户管理员权限成功",
  "data": null
}
```

#### 失败响应
- **400 Bad Request**: 请求参数错误
```json
{
  "code": 400,
  "msg": "不能解除自己的管理员权限",
  "data": null
}
```

- **401 Unauthorized**: 请先登录
```json
{
  "code": 401,
  "msg": "请先登录",
  "data": null
}
```

- **404 Not Found**: 用户不存在
```json
{
  "code": 404,
  "msg": "用户不存在",
  "data": null
}
```

- **500 Internal Server Error**: 系统错误
```json
{
  "code": 500,
  "msg": "系统错误，请稍后重试",
  "data": null
}
```

## 15. 获取所有歌单接口

### 接口信息
- URL: `/admin/playlists`
- 方法: `GET`
- 功能: 获取所有歌单列表（分页查询）
- 权限: 管理员

### 请求参数
| 参数名 | 类型 | 必填 | 默认值 | 描述 |
|--------|------|------|--------|------|
| current | Integer | 否 | 1 | 当前页码 |
| size | Integer | 否 | 10 | 每页记录数 |

### 响应格式

#### 成功响应 (200 OK)
```json
{
  "code": 200,
  "msg": "获取所有歌单成功",
  "data": {
    "records": [
      {
        "id": 1,
        "user_id": 1,
        "username": "admin",
        "name": "我的歌单",
        "cover_url": "http://example.com/cover.jpg",
        "description": "这是我的歌单",
        "create_time": "2023-01-01 00:00:00",
        "update_time": "2023-01-01 00:00:00",
        "song_count": 10
      },
      // ... 更多歌单
    ],
    "current": 1,
    "size": 10,
    "total": 50,
    "pages": 5
  }
}
```

#### 失败响应
- **401 Unauthorized**: 请先登录
```json
{
  "code": 401,
  "msg": "请先登录",
  "data": null
}
```

- **500 Internal Server Error**: 系统错误
```json
{
  "code": 500,
  "msg": "系统错误，请稍后重试",
  "data": null
}
```

## 16. 根据用户ID获取歌单接口

### 接口信息
- URL: `/admin/users/<int:user_id>/playlists`
- 方法: `GET`
- 功能: 根据用户ID获取歌单列表
- 权限: 管理员

### 请求参数
| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| user_id | Integer | 是 | 用户ID |

### 响应格式

#### 成功响应 (200 OK)
```json
{
  "code": 200,
  "msg": "获取用户歌单成功",
  "data": {
    "user": {
      "id": 1,
      "username": "admin"
    },
    "playlists": [
      {
        "id": 1,
        "user_id": 1,
        "username": "admin",
        "name": "我的歌单",
        "cover_url": "http://example.com/cover.jpg",
        "description": "这是我的歌单",
        "create_time": "2023-01-01 00:00:00",
        "update_time": "2023-01-01 00:00:00",
        "song_count": 10
      },
      // ... 更多歌单
    ],
    "total": 10
  }
}
```

#### 失败响应
- **401 Unauthorized**: 请先登录
```json
{
  "code": 401,
  "msg": "请先登录",
  "data": null
}
```

- **404 Not Found**: 用户不存在
```json
{
  "code": 404,
  "msg": "用户不存在",
  "data": null
}
```

- **500 Internal Server Error**: 系统错误
```json
{
  "code": 500,
  "msg": "系统错误，请稍后重试",
  "data": null
}
```

## 17. 修改歌单信息接口

### 接口信息
- URL: `/admin/playlists/<int:playlist_id>`
- 方法: `PUT`
- 功能: 管理员修改指定歌单的信息
- 权限: 管理员

### 请求参数
| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| playlist_id | Integer | 是 | 歌单ID |
| name | String | 否 | 歌单名称，不能为空 |
| cover_url | String | 否 | 歌单封面URL |
| description | String | 否 | 歌单描述 |

### 响应格式

#### 成功响应 (200 OK)
```json
{
  "code": 200,
  "msg": "更新歌单信息成功",
  "data": {
    "id": 1,
    "user_id": 1,
    "name": "更新后的歌单名称",
    "cover_url": "http://example.com/new_cover.jpg",
    "description": "更新后的歌单描述",
    "create_time": "2023-01-01 00:00:00",
    "update_time": "2023-01-02 00:00:00"
  }
}
```

#### 失败响应
- **400 Bad Request**: 请求参数错误
```json
{
  "code": 400,
  "msg": "没有提供要修改的字段",
  "data": null
}
```

```json
{
  "code": 400,
  "msg": "歌单名称不能为空",
  "data": null
}
```

```json
{
  "code": 400,
  "msg": "没有提供有效的字段进行修改",
  "data": null
}
```

- **401 Unauthorized**: 请先登录
```json
{
  "code": 401,
  "msg": "请先登录",
  "data": null
}
```

- **404 Not Found**: 歌单不存在
```json
{
  "code": 404,
  "msg": "歌单不存在",
  "data": null
}
```

- **500 Internal Server Error**: 系统错误
```json
{
  "code": 500,
  "msg": "系统错误，请稍后重试",
  "data": null
}
```

## 18. 删除歌单接口

### 接口信息
- URL: `/admin/playlists/<int:playlist_id>`
- 方法: `DELETE`
- 功能: 管理员删除指定歌单
- 权限: 管理员

### 请求参数
| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| playlist_id | Integer | 是 | 歌单ID |

### 响应格式

#### 成功响应 (200 OK)
```json
{
  "code": 200,
  "msg": "删除歌单成功",
  "data": null
}
```

#### 失败响应
- **401 Unauthorized**: 请先登录
```json
{
  "code": 401,
  "msg": "请先登录",
  "data": null
}
```

- **404 Not Found**: 歌单不存在
```json
{
  "code": 404,
  "msg": "歌单不存在",
  "data": null
}
```

- **500 Internal Server Error**: 系统错误
```json
{
  "code": 500,
  "msg": "系统错误，请稍后重试",
  "data": null
}
```

## 19. 响应状态码说明

| 状态码 | 描述 |
|--------|------|
| 200 | 请求成功 |
| 201 | 资源创建成功 |
| 400 | 请求参数错误 |
| 401 | 未登录或登录状态失效 |
| 404 | 请求的资源不存在 |
| 500 | 系统内部错误 |

## 20. 错误码说明

| 错误码 | 描述 |
|--------|------|
| 200 | 操作成功 |
| 201 | 资源创建成功 |
| 400 | 请求参数错误 |
| 401 | 未授权或认证失败 |
| 404 | 资源不存在 |
| 500 | 系统错误 |