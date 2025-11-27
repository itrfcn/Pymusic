from apps.tool.Mysql import Mysql
import datetime
import logging
from flask import Flask, g

# 配置日志（兼容 Flask 全局日志）
logger = logging.getLogger(__name__)
if not logger.handlers:
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    ))
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)

# 定时任务配置（可直接修改）
SCHEDULER_CONFIG = {
    "CRON_HOUR": 2,    # 每天凌晨2点执行
    "CRON_MINUTE": 0,  # 分钟数（0-59）
    "BATCH_SIZE": 1000 # 批量删除大小，避免锁表
}

def clean_play_history_data(days_to_keep=90, max_records_per_user=1000):
    """
    清理播放历史数据（Flask 适配版）
    - 修复 SQL 注入
    - 批量删除避免锁表
    - 日志替换 print
    """
    try:
        with Mysql() as db:
            deleted_count = 0
            
            # 1. 删除超过指定天数的记录（参数化查询 + 批量删除）
            logger.info(f"开始清理{days_to_keep}天前的播放历史记录...")
            cutoff_date = datetime.datetime.now() - datetime.timedelta(days=days_to_keep)
            cutoff_date_str = cutoff_date.strftime('%Y-%m-%d %H:%M:%S')
            
            # 修复：参数化查询（%s 占位符，避免注入）
            old_records_sql = """
            DELETE FROM play_history 
            WHERE play_time < %s
            LIMIT %s  # 批量删除，避免锁表
            """
            # 循环分批删除
            while True:
                # 修复：传递参数元组，而非字符串拼接
                old_records_result = db.sql(old_records_sql, (cutoff_date_str, SCHEDULER_CONFIG["BATCH_SIZE"]))
                old_deleted = old_records_result[0] if isinstance(old_records_result, tuple) else 0
                if old_deleted <= 0:
                    break
                deleted_count += old_deleted
            logger.info(f"已删除{deleted_count}条超过{days_to_keep}天的记录")
            
            # 2. 为每个用户保留最新记录（参数化查询 + 批量删除）
            logger.info(f"开始清理每个用户超过{max_records_per_user}条的记录...")
            
            users_sql = "SELECT DISTINCT user_id FROM play_history"
            users = db.sql(users_sql)
            
            if isinstance(users, list) and users:
                for user in users:
                    user_id = user.get('user_id')
                    if user_id:
                        # 修复：参数化查询（user_id 和 limit 用占位符）
                        keep_ids_sql = """
                        SELECT id FROM play_history 
                        WHERE user_id = %s 
                        ORDER BY play_time DESC 
                        LIMIT %s
                        """
                        keep_ids_result = db.sql(keep_ids_sql, (user_id, max_records_per_user))
                        
                        if isinstance(keep_ids_result, list) and keep_ids_result:
                            keep_ids = [str(record.get('id')) for record in keep_ids_result if record.get('id')]
                            
                            if keep_ids:
                                # 修复：参数化查询（IN 从句用占位符）
                                delete_user_sql = f"""
                                DELETE FROM play_history 
                                WHERE user_id = %s 
                                AND id NOT IN ({','.join(['%s'] * len(keep_ids))})
                                LIMIT %s
                                """
                                # 拼接参数：user_id + keep_ids + 批量大小
                                params = [user_id] + keep_ids + [SCHEDULER_CONFIG["BATCH_SIZE"]]
                                user_total_deleted = 0
                                while True:
                                    user_delete_result = db.sql(delete_user_sql, params)
                                    user_deleted = user_delete_result[0] if isinstance(user_delete_result, tuple) else 0
                                    if user_deleted <= 0:
                                        break
                                    user_total_deleted += user_deleted
                                    deleted_count += user_deleted
                                if user_total_deleted > 0:
                                    logger.info(f"用户{user_id}：已删除{user_total_deleted}条旧记录")
            
            # 3. 优化表空间（仅在有删除时执行）
            if deleted_count > 0:
                logger.info("\n优化表空间...")
                try:
                    db.sql("OPTIMIZE TABLE play_history")
                    logger.info("表空间优化完成")
                except Exception as e:
                    logger.error(f"表空间优化失败：{str(e)}", exc_info=True)
            else:
                logger.info("\n无数据删除，跳过表空间优化")
            
            # 4. 数据统计
            logger.info("\n当前数据统计:")
            total_count_sql = "SELECT COUNT(*) as count FROM play_history"
            total_result = db.sql(total_count_sql)
            total_count = total_result[0].get('count', 0) if isinstance(total_result, list) and total_result else 0
            
            user_count_sql = "SELECT COUNT(DISTINCT user_id) as count FROM play_history"
            user_result = db.sql(user_count_sql)
            user_count = user_result[0].get('count', 0) if isinstance(user_result, list) and user_result else 0
            
            logger.info(f"总记录数: {total_count}")
            logger.info(f"用户数: {user_count}")
            logger.info(f"本次清理共删除: {deleted_count}条记录")
            logger.info("播放历史数据清理完成！\n")
            
            return {
                'total_count': total_count,
                'user_count': user_count,
                'deleted_count': deleted_count
            }
            
    except Exception as e:
        logger.error(f"清理过程中出错: {str(e)}", exc_info=True)
        return {'error': str(e)}

# -------------------------- Flask 定时任务核心 --------------------------
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.executors.pool import ThreadPoolExecutor

# 全局调度器实例
scheduler = None

def start_scheduler():
    """启动定时任务调度器"""
    global scheduler
    if scheduler and scheduler.running:
        logger.warning("定时调度器已在运行")
        return
    
    # 配置单线程执行，避免数据库并发冲突
    executors = {"default": ThreadPoolExecutor(1)}
    scheduler = BackgroundScheduler(
        executors=executors,
        timezone="Asia/Shanghai"  # 指定时区，避免错乱
    )
    
    # 添加定时任务（每天凌晨2点执行）
    scheduler.add_job(
        id="play_history_cleanup",
        func=clean_play_history_data,
        trigger="cron",
        hour=SCHEDULER_CONFIG["CRON_HOUR"],
        minute=SCHEDULER_CONFIG["CRON_MINUTE"]
    )
    
    scheduler.start()
    logger.info(f"定时调度器启动成功！每天 {SCHEDULER_CONFIG['CRON_HOUR']}:{SCHEDULER_CONFIG['CRON_MINUTE']:02d} 执行清理")

def stop_scheduler():
    """停止定时任务调度器"""
    global scheduler
    if scheduler and scheduler.running:
        scheduler.shutdown()
        logger.info("定时调度器已停止")

def register_cleanup_hook(app: Flask):
    """
    注册 Flask 定时任务（适配 Flask 生命周期）
    - 应用启动时启动调度器
    - 应用退出时停止调度器
    - 兼容 Flask 1.x/2.x
    """
    # 替代 before_first_request（兼容 Flask 2.0+）
    scheduler_initialized = False
    
    @app.before_request
    def init_scheduler():
        nonlocal scheduler_initialized
        if not scheduler_initialized:
            scheduler_initialized = True
            start_scheduler()
    
    # 应用退出时停止调度器
    @app.teardown_appcontext
    def shutdown_scheduler(exception=None):
        stop_scheduler()

if __name__ == "__main__":
    # 直接运行时执行一次清理（测试用）
    clean_play_history_data()