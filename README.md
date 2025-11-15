# 个人博客后端开发手册

## 预期功能

前端分为管理端和用户端(两个vue app), 后端同时处理来自管理端和用户端的请求

### 接口设计

仅超级管理员(我本人)和授权用户(role为admin)可登录后台管理端, 管理端的接口请求需要鉴权,部分接口内部需要进一步确定是否是超级管理员, 比如普通管理员登录管理端后不能删除其他管理员用户, 更不能删除超级管理员

超级管理员的id可设置为环境变量在.env中

#### 用户部分

1. 用户注册(用户端)
路径: POST /api/v1/users
功能: 新用户注册, 默认role为user

2. 用户登录(用户端)
路径: POST /api/v1/users/login
功能: 用户登录，返回 JWT Token

3. 用户登出(用户端)
路径: POST /api/v1/users/logout
功能: 用户登出
请求头: Authorization: Bearer `<token>`

4. 获取当前用户信息(用户端)
路径: GET /api/v1/users
功能: 获取当前登录用户信息
请求头: Authorization: Bearer `<token>`

5. 更新用户信息(用户端)
路径: PUT /api/v1/users
功能: 更新当前用户信息
请求头: Authorization: Bearer `<token>`

6. 修改密码(用户端)
路径: PUT /api/v1/users/password
功能: 修改当前用户密码
请求头: Authorization: Bearer `<token>`

7. 获取用户列表（管理端）
路径: GET /api/v1/admin/users
功能: 分页获取用户列表（仅管理员）
请求头: Authorization: Bearer `<token>`
查询参数:
page: 页码 (默认1)
size: 每页数量 (默认10)

8. 获取单个用户信息（管理端）
路径: GET /api/v1/admin/users/{id}
功能: 获取指定用户信息（仅管理员）
请求头: Authorization: Bearer `<token>`

9. 更新用户状态（管理端）
路径: PUT /api/v1/admin/users/{id}/status
功能: 启用/禁用用户（仅管理员）
请求头: Authorization: Bearer `<token>`

10. 删除用户（管理端）
路径: DELETE /api/v1/admin/users/{id}
功能: 删除用户（仅管理员）
请求头: Authorization: Bearer `<token>`

11. 创建用户（管理端）
路径: POST /api/v1/admin/users
功能: 创建新用户（仅管理员）
请求头: Authorization: Bearer `<token>`

#### 文章部分

文章作者信息默认使用固定常量, 保留 `author_id` 以便后续拓展。

1. 获取文章列表(用户端)
路径: GET /api/v1/articles
功能: 分页获取文章卡片列表, 不包含正文; 每条包含 `tag_names`（逗号分隔）与 `categories` 列表
查询参数: page, size, category_id?, tag_id?

2. 获取单个文章详情(用户端)
路径: GET /api/v1/articles/{id}
功能: 获取指定文章详情, 包含卡片信息、`tag_names` 与正文文件路径

3. 创建文章(管理端)
路径: POST /api/v1/admin/articles
功能: 创建新文章并维护分类/标签关联
请求头: Authorization: Bearer `<token>`

4. 更新文章(管理端)
路径: PUT /api/v1/admin/articles/{id}
功能: 更新指定文章及分类/标签关联
请求头: Authorization: Bearer `<token>`

5. 删除文章(管理端)
路径: DELETE /api/v1/admin/articles/{id}
功能: 删除指定文章
请求头: Authorization: Bearer `<token>`

#### 分类部分

1. 获取分类列表(管理端和用户端都可用)
路径: GET /api/v1/categories
功能: 获取所有分类列表

2. 创建分类(管理端)
路径: POST /api/v1/categories
功能: 创建新分类
请求头: Authorization: Bearer `<token>`

3. 删除分类(管理端)
路径: DELETE /api/v1/categories/{id}
功能: 删除指定分类
请求头: Authorization: Bearer `<token>`

4. 更新分类(管理端)
路径: PUT /api/v1/categories/{id}
功能: 更新指定分类
请求头: Authorization: Bearer `<token>`

#### 标签部分

1. 获取标签列表(管理端和用户端都可用)
路径: GET /api/v1/tags
功能: 获取所有标签列表

2. 标签管理(管理端)
路径: POST/PUT/DELETE /api/v1/admin/tags
功能: 创建/更新/删除标签
请求头: Authorization: Bearer `<token>`

#### 评论部分

1. 获取文章评论(用户端)
路径: GET /api/v1/articles/{id}/comments
功能: 分页获取文章评论
查询参数: page, size

2. 发表评论(用户端)
路径: POST /api/v1/articles/{id}/comments
功能: 登录用户发表评论（需鉴权），匿名评论已移除

3. 评论审核(管理端)
路径: PUT /api/v1/admin/comments/{id}/status
功能: 审核评论状态
请求头: Authorization: Bearer `<token>`

#### 点赞部分

1. 获取点赞数(用户端)
路径: GET /api/v1/articles/{id}/likes/count
功能: 直接读取 `like_count`

2. 点赞(用户端)
路径: POST /api/v1/articles/{id}/likes
功能: 为文章 `like_count` +1
