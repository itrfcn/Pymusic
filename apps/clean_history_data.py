from apps.tool.Mysql import Mysql
import datetime

def clean_play_history_data(days_to_keep=90, max_records_per_user=1000):
    """
    清理播放历史数据
    
    Args:
        days_to_keep: 保留多少天内的记录，默认90天
        max_records_per_user: 每个用户最多保留的记录数，默认1000条
    """
    try:
        with Mysql() as db:
            deleted_count = 0
            
            # 1. 删除超过指定天数的记录
            print(f"开始清理{days_to_keep}天前的播放历史记录...")
            cutoff_date = datetime.datetime.now() - datetime.timedelta(days=days_to_keep)
            cutoff_date_str = cutoff_date.strftime('%Y-%m-%d %H:%M:%S')
            
            old_records_sql = f"""
            DELETE FROM play_history 
            WHERE play_time < '{cutoff_date_str}'
            """
            old_records_result = db.sql(old_records_sql)
            old_deleted = old_records_result[0] if isinstance(old_records_result, tuple) else 0
            deleted_count += old_deleted
            print(f"已删除{old_deleted}条超过{days_to_keep}天的记录")
            
            # 2. 为每个用户保留最新的记录，删除多余的旧记录
            print(f"开始清理每个用户超过{max_records_per_user}条的记录...")
            
            # 获取所有用户ID
            users_sql = "SELECT DISTINCT user_id FROM play_history"
            users = db.sql(users_sql)
            
            if isinstance(users, list) and users:
                for user in users:
                    user_id = user.get('user_id')
                    if user_id:
                        # 获取该用户需要保留的记录ID列表（最新的max_records_per_user条）
                        keep_ids_sql = f"""
                        SELECT id FROM play_history 
                        WHERE user_id = {user_id} 
                        ORDER BY play_time DESC 
                        LIMIT {max_records_per_user}
                        """
                        keep_ids_result = db.sql(keep_ids_sql)
                        
                        if isinstance(keep_ids_result, list) and keep_ids_result:
                            # 提取需要保留的ID
                            keep_ids = [str(record.get('id')) for record in keep_ids_result if record.get('id')]
                            
                            if keep_ids:
                                # 删除不在保留列表中的记录
                                delete_user_sql = f"""
                                DELETE FROM play_history 
                                WHERE user_id = {user_id} 
                                AND id NOT IN ({','.join(keep_ids)})
                                """
                                user_delete_result = db.sql(delete_user_sql)
                                user_deleted = user_delete_result[0] if isinstance(user_delete_result, tuple) else 0
                                deleted_count += user_deleted
                                if user_deleted > 0:
                                    print(f"用户{user_id}：已删除{user_deleted}条旧记录")
            
            # 3. 优化表空间
            print("\n优化表空间...")
            db.sql("OPTIMIZE TABLE play_history")
            
            # 4. 显示当前数据统计
            print("\n当前数据统计:")
            total_count_sql = "SELECT COUNT(*) as count FROM play_history"
            total_result = db.sql(total_count_sql)
            total_count = total_result[0].get('count', 0) if isinstance(total_result, list) and total_result else 0
            
            user_count_sql = "SELECT COUNT(DISTINCT user_id) as count FROM play_history"
            user_result = db.sql(user_count_sql)
            user_count = user_result[0].get('count', 0) if isinstance(user_result, list) and user_result else 0
            
            print(f"总记录数: {total_count}")
            print(f"用户数: {user_count}")
            print(f"本次清理共删除: {deleted_count}条记录")
            print("\n播放历史数据清理完成！")
            
            return {
                'total_count': total_count,
                'user_count': user_count,
                'deleted_count': deleted_count
            }
            
    except Exception as e:
        print(f"清理过程中出错: {str(e)}")
        return {'error': str(e)}

# 添加到应用的启动时自动清理

def register_cleanup_hook(app):
    """
    注册应用启动时的清理钩子
    """
    # 使用app.before_request来模拟before_first_request功能
    first_request = True
    
    @app.before_request
    def cleanup_on_startup():
        # 记录日志但不阻止应用启动
        nonlocal first_request
        if first_request:
            first_request = False
            try:
                print("[定时任务] 执行播放历史数据清理...")
                clean_play_history_data()
            except Exception as e:
                print(f"[定时任务] 清理失败: {str(e)}")

if __name__ == "__main__":
    # 直接运行时执行清理
    clean_play_history_data()