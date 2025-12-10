#!/usr/bin/env python3
"""
用于测试管理员功能的脚本
"""

import requests
import json

BASE_URL = 'http://localhost:5000'

def test_login():
    """测试登录功能"""
    print("\n=== 测试登录功能 ===")
    data = {
        'username': 'admin',
        'password': '123456'
    }
    response = requests.post(f'{BASE_URL}/user/login', data=data)
    print(f"登录响应: {response.status_code}, {response.text}")
    return response.cookies


def test_get_all_users(cookies):
    """测试获取所有用户列表"""
    print("\n=== 测试获取所有用户列表 ===")
    response = requests.get(f'{BASE_URL}/user/admin/users', cookies=cookies)
    print(f"获取用户列表响应: {response.status_code}, {response.text}")
    return response.json()


def test_ban_user(cookies, user_id):
    """测试封禁用户"""
    print(f"\n=== 测试封禁用户 {user_id} ===")
    response = requests.put(f'{BASE_URL}/user/admin/users/{user_id}/ban', cookies=cookies)
    print(f"封禁用户响应: {response.status_code}, {response.text}")
    return response.json()


def test_unban_user(cookies, user_id):
    """测试解放用户"""
    print(f"\n=== 测试解放用户 {user_id} ===")
    response = requests.put(f'{BASE_URL}/user/admin/users/{user_id}/unban', cookies=cookies)
    print(f"解放用户响应: {response.status_code}, {response.text}")
    return response.json()


def test_delete_user(cookies, user_id):
    """测试删除用户"""
    print(f"\n=== 测试删除用户 {user_id} ===")
    response = requests.delete(f'{BASE_URL}/user/admin/users/{user_id}', cookies=cookies)
    print(f"删除用户响应: {response.status_code}, {response.text}")
    return response.json()


def test_set_admin(cookies, user_id):
    """测试设置用户为管理员"""
    print(f"\n=== 测试设置用户 {user_id} 为管理员 ===")
    response = requests.put(f'{BASE_URL}/user/admin/users/{user_id}/set_admin', cookies=cookies)
    print(f"设置管理员响应: {response.status_code}, {response.text}")
    return response.json()


def main():
    print("管理员功能测试脚本")
    print(f"测试基础URL: {BASE_URL}")
    
    # 登录
    cookies = test_login()
    if not cookies:
        print("登录失败，无法进行后续测试")
        return
    
    # 获取所有用户列表
    users_data = test_get_all_users(cookies)
    if not users_data.get('data'):
        print("没有用户数据，无法进行后续测试")
        return
    
    # 获取第一个用户的ID（用于测试）
    user_id = users_data['data'][0]['id']
    print(f"测试用户ID: {user_id}")
    
    # 测试封禁用户
    # test_ban_user(cookies, user_id)
    
    # 测试解放用户
    # test_unban_user(cookies, user_id)
    
    # 测试设置用户为管理员
    # test_set_admin(cookies, user_id)
    
    # 测试删除用户（谨慎使用）
    # test_delete_user(cookies, user_id)
    
    print("\n=== 测试完成 ===")


if __name__ == "__main__":
    main()