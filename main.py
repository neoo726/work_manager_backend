"""
Work Manager Backend - FastAPI 主应用
"""
from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import json
import logging
from datetime import datetime
from typing import List

from config import settings, get_allowed_origins
from database import get_db_manager, DatabaseManager
from models import (
    SmartRecordWorkItemRequest,
    QueryWorkItemsRequest,
    UpdateWorkItemRequest,
    ApiResponse,
    HealthResponse,
    WorkItemResponse
)
from utils import get_date_range, get_user_id_from_request, validate_priority
from text_parser import parse_user_query

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 创建 FastAPI 应用实例
app = FastAPI(
    title="Work Manager Backend",
    description="为 Dify AI 助手提供工作事项管理功能的后端服务",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# 添加 CORS 中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=get_allowed_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """全局异常处理器"""
    logger.error(f"未处理的异常: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"message": f"服务器内部错误: {str(exc)}", "error": True}
    )


@app.get("/", response_model=dict)
async def root():
    """根路径"""
    return {
        "message": "Work Manager Backend API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }


@app.get("/health", response_model=HealthResponse)
async def health_check(db_manager: DatabaseManager = Depends(get_db_manager)):
    """健康检查接口"""
    try:
        # 测试数据库连接
        is_db_healthy = db_manager.test_connection()
        
        if is_db_healthy:
            return HealthResponse(
                status="healthy",
                message="服务运行正常，数据库连接成功",
                timestamp=datetime.now()
            )
        else:
            raise HTTPException(
                status_code=503,
                detail="数据库连接失败"
            )
    except Exception as e:
        logger.error(f"健康检查失败: {e}")
        raise HTTPException(
            status_code=503,
            detail=f"健康检查失败: {str(e)}"
        )


@app.post("/smart_record_work_item", response_model=ApiResponse)
async def smart_record_work_item(
    request: SmartRecordWorkItemRequest,
    http_request: Request,
    db_manager: DatabaseManager = Depends(get_db_manager)
):
    """智能记录工作事项"""
    try:
        # 获取用户ID
        user_id = get_user_id_from_request(dict(http_request.headers))

        # 调试日志
        logger.info(f"记录请求 - 用户ID: {user_id}")
        logger.info(f"记录请求 - 请求头: {dict(http_request.headers)}")
        logger.info(f"记录请求 - 请求内容: {request}")

        # 验证优先级
        if not validate_priority(request.priority):
            raise HTTPException(
                status_code=400,
                detail="优先级必须在1-5之间"
            )
        
        # 插入数据库
        with db_manager.get_db_cursor() as cursor:
            sql = """
            INSERT INTO work_items (
                user_id, type, content, summary, project_name,
                due_date, start_date, status, priority, tags
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """

            cursor.execute(sql, (
                user_id,
                request.item_type.value,
                request.user_input,
                request.summary,
                request.project_name,
                request.due_date,
                request.start_date,
                request.status.value if request.status else None,
                request.priority,
                json.dumps(request.tags) if request.tags else None
            ))

            # MySQL 使用 lastrowid 获取插入的ID
            item_id = cursor.lastrowid
        
        logger.info(f"成功记录工作事项: {item_id}")
        return ApiResponse(
            message=f"工作事项 '{request.summary}' 已成功记录，ID: {item_id}",
            error=False
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"记录工作事项失败: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"记录工作事项失败: {str(e)}"
        )


@app.post("/query_work_items", response_model=ApiResponse)
async def query_work_items(
    request: QueryWorkItemsRequest,
    http_request: Request,
    db_manager: DatabaseManager = Depends(get_db_manager)
):
    """查询工作事项"""
    try:
        # 获取用户ID
        user_id = get_user_id_from_request(dict(http_request.headers))

        # 调试日志
        logger.info(f"查询请求 - 用户ID: {user_id}")
        logger.info(f"查询请求 - 请求头: {dict(http_request.headers)}")
        logger.info(f"查询请求 - 查询参数: {request}")

        # 构建查询条件
        query_parts = ["user_id = %s"]
        query_params = [user_id]

        # 添加各种查询条件
        if request.item_id:
            query_parts.append("id = %s")
            query_params.append(request.item_id)

        if request.project_name:
            query_parts.append("project_name LIKE %s")
            query_params.append(f"%{request.project_name}%")

        if request.item_type:
            query_parts.append("type = %s")
            query_params.append(request.item_type.value)

        if request.status:
            query_parts.append("status = %s")
            query_params.append(request.status.value)

        if request.keyword:
            query_parts.append("(summary LIKE %s OR content LIKE %s)")
            query_params.extend([f"%{request.keyword}%", f"%{request.keyword}%"])

        # 处理时间范围
        if request.time_range:
            start_date, end_date = get_date_range(request.time_range.value)

            # 对于"最近"查询，使用混合时间逻辑：创建时间 + 截止日期 + 开始日期
            if request.time_range.value == 'recent':
                if start_date and end_date:
                    # 最近：查找在时间范围内创建的，或者截止日期/开始日期在范围内的
                    query_parts.append("""(
                        DATE(created_at) BETWEEN %s AND %s OR
                        due_date BETWEEN %s AND %s OR
                        start_date BETWEEN %s AND %s
                    )""")
                    query_params.extend([start_date, end_date, start_date, end_date, start_date, end_date])
            # 对于"过去"类查询，主要使用创建时间
            elif request.time_range.value in ['past_week', 'past_month']:
                if start_date and end_date:
                    query_parts.append("DATE(created_at) BETWEEN %s AND %s")
                    query_params.extend([start_date, end_date])
                elif start_date:
                    query_parts.append("DATE(created_at) = %s")
                    query_params.append(start_date)
            else:
                # 对于其他时间范围，使用截止日期和开始日期
                if start_date and end_date:
                    query_parts.append("(due_date BETWEEN %s AND %s OR start_date BETWEEN %s AND %s)")
                    query_params.extend([start_date, end_date, start_date, end_date])
                elif start_date:
                    query_parts.append("(due_date = %s OR start_date = %s)")
                    query_params.extend([start_date, start_date])

        # 执行查询
        with db_manager.get_db_cursor() as cursor:
            query_str = """
            SELECT id, type, summary, project_name, due_date, status, priority, created_at, updated_at
            FROM work_items
            """
            if query_parts:
                query_str += " WHERE " + " AND ".join(query_parts)
            query_str += " ORDER BY due_date ASC, created_at DESC LIMIT 20"

            # 调试SQL查询
            logger.info(f"执行SQL: {query_str}")
            logger.info(f"查询参数: {tuple(query_params)}")

            cursor.execute(query_str, tuple(query_params))
            rows = cursor.fetchall()

        # 格式化结果
        result_list = []
        for row in rows:
            result_list.append(WorkItemResponse(
                id=str(row['id']),
                type=row['type'],
                summary=row['summary'],
                project_name=row['project_name'],
                due_date=str(row['due_date']) if row['due_date'] else None,
                status=row['status'],
                priority=row['priority'],
                created_at=str(row['created_at']) if row['created_at'] else None,
                updated_at=str(row['updated_at']) if row['updated_at'] else None
            ))

        if not result_list:
            return ApiResponse(
                message="没有找到符合条件的工作事项",
                data=[],
                error=False
            )

        logger.info(f"查询到 {len(result_list)} 个工作事项")
        return ApiResponse(
            message="查询成功",
            data=result_list,
            error=False
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"查询工作事项失败: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"查询工作事项失败: {str(e)}"
        )


@app.post("/smart_query_work_items", response_model=ApiResponse)
async def smart_query_work_items(
    request: dict,
    http_request: Request,
    db_manager: DatabaseManager = Depends(get_db_manager)
):
    """智能查询工作事项 - 支持自然语言输入"""
    try:
        # 获取用户输入
        user_input = request.get('user_input', '')
        if not user_input:
            raise HTTPException(
                status_code=400,
                detail="请提供查询内容"
            )

        # 获取用户ID
        user_id = get_user_id_from_request(dict(http_request.headers))

        # 调试日志
        logger.info(f"智能查询 - 用户ID: {user_id}")
        logger.info(f"智能查询 - 用户输入: {user_input}")

        # 解析用户输入
        parsed_query = parse_user_query(user_input)
        logger.info(f"智能查询 - 解析结果: {parsed_query}")

        # 构建查询请求
        from models import QueryWorkItemsRequest, TimeRange, ItemType, ItemStatus

        query_request = QueryWorkItemsRequest()

        # 设置时间范围
        if parsed_query['time_range']:
            try:
                query_request.time_range = TimeRange(parsed_query['time_range'])
            except ValueError:
                pass

        # 设置事项类型
        if parsed_query['item_type']:
            try:
                query_request.item_type = ItemType(parsed_query['item_type'])
            except ValueError:
                pass

        # 设置状态
        if parsed_query['status']:
            try:
                query_request.status = ItemStatus(parsed_query['status'])
            except ValueError:
                pass

        # 设置关键词
        if parsed_query['keyword']:
            query_request.keyword = parsed_query['keyword']

        # 如果没有解析到任何条件，使用原始输入作为关键词
        if not any([query_request.time_range, query_request.item_type,
                   query_request.status, query_request.keyword]):
            query_request.keyword = user_input

        # 调用标准查询接口
        return await query_work_items(query_request, http_request, db_manager)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"智能查询失败: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"智能查询失败: {str(e)}"
        )


@app.post("/update_work_item", response_model=ApiResponse)
async def update_work_item(
    request: UpdateWorkItemRequest,
    http_request: Request,
    db_manager: DatabaseManager = Depends(get_db_manager)
):
    """更新工作事项"""
    try:
        # 获取用户ID
        user_id = get_user_id_from_request(dict(http_request.headers))
        target_item_id = request.item_id

        # 如果没有提供item_id，尝试通过关键词或时间上下文查找
        if not target_item_id:
            # 构建查询请求
            query_request = QueryWorkItemsRequest(
                keyword=request.keyword,
                time_range=request.time_context
            )

            # 执行查询
            query_result = await query_work_items(query_request, http_request, db_manager)

            if query_result.data and len(query_result.data) == 1:
                target_item_id = query_result.data[0].id
            elif query_result.data and len(query_result.data) > 1:
                item_summaries = ", ".join([item.summary for item in query_result.data])
                raise HTTPException(
                    status_code=400,
                    detail=f"找到了多个符合条件的工作事项，请提供更具体的描述或ID：{item_summaries}"
                )
            else:
                raise HTTPException(
                    status_code=404,
                    detail="未能找到符合条件的工作事项进行更新"
                )

        # 验证新优先级
        if not validate_priority(request.new_priority):
            raise HTTPException(
                status_code=400,
                detail="优先级必须在1-5之间"
            )

        # 构建更新语句
        update_parts = []
        update_params = []

        if request.new_status:
            update_parts.append("status = %s")
            update_params.append(request.new_status.value)

        if request.new_due_date:
            update_parts.append("due_date = %s")
            update_params.append(request.new_due_date)

        if request.new_priority is not None:
            update_parts.append("priority = %s")
            update_params.append(request.new_priority)

        if request.new_summary:
            update_parts.append("summary = %s")
            update_params.append(request.new_summary)

        if request.new_content:
            update_parts.append("content = %s")
            update_params.append(request.new_content)

        if not update_parts:
            return ApiResponse(
                message="没有提供更新内容",
                error=False
            )

        # 添加更新时间
        update_parts.append("updated_at = NOW()")

        # 执行更新
        with db_manager.get_db_cursor() as cursor:
            sql = f"UPDATE work_items SET {', '.join(update_parts)} WHERE id = %s AND user_id = %s"
            update_params.extend([target_item_id, user_id])

            cursor.execute(sql, tuple(update_params))

            if cursor.rowcount == 0:
                raise HTTPException(
                    status_code=404,
                    detail=f"未能找到ID为 {target_item_id} 的工作事项或无权更新"
                )

        logger.info(f"成功更新工作事项: {target_item_id}")
        return ApiResponse(
            message=f"工作事项 {target_item_id} 已成功更新",
            error=False
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"更新工作事项失败: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"更新工作事项失败: {str(e)}"
        )


if __name__ == "__main__":
    import uvicorn
    from dotenv import load_dotenv

    # 加载环境变量
    load_dotenv()

    # 启动服务
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level="info"
    )
