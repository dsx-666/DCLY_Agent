import psycopg2
from psycopg2 import OperationalError, ProgrammingError
from typing import List, Dict, Tuple, Optional

from ..sql.SQLConfig import DB_CONFIG,DATABASES,conn


# 核心数据库操作函数



def get_all_schemas() -> List[str]:
    """获取数据库中所有非系统模式"""
    try:
        with conn.cursor() as cur:
            # 排除postgres系统模式，只查用户自定义模式（含public）
            cur.execute("""
                        SELECT schema_name
                        FROM information_schema.schemata
                        WHERE schema_name NOT IN ('pg_catalog', 'information_schema', 'pg_toast')
                        ORDER BY schema_name;
                        """)
            schemas = [row[0] for row in cur.fetchall()]
        return schemas
    except Exception as e:
        return []



def get_table_structure(schema_name: str, table_name: str) -> Tuple[str, List[Dict]]:
    """
    查询指定模式下指定表的完整结构
    :param schema_name: 模式名
    :param table_name: 表名
    :return: 表注释, 字段详情列表
    """


    try:
        with conn.cursor() as cur:
            # 1. 查询表注释
            cur.execute("""
                        SELECT COALESCE(obj_description(pc.oid, 'pg_class'), '无表注释')
                        FROM pg_class pc
                                 JOIN pg_namespace pn ON pc.relnamespace = pn.oid
                        WHERE pn.nspname = %s
                          AND pc.relname = %s;
                        """, (schema_name, table_name))
            table_comment = cur.fetchone()[0]

            # 2. 查询字段完整信息（含主键、可空、默认值、注释）
            cur.execute("""
                        SELECT c.column_name,                                                                         -- 字段名
                               c.data_type,                                                                           -- 字段类型
                               c.character_maximum_length,                                                            -- 字符类型长度（如varchar(20)的20）
                               c.is_nullable,                                                                         -- 是否可为空（YES/NO）
                               COALESCE(c.column_default, '无默认值'),                                                -- 默认值
                               CASE WHEN tc.constraint_type = 'PRIMARY KEY' THEN '是' ELSE '否' END AS is_primary,    -- 是否主键
                               COALESCE(pd.description, '无字段注释')                               AS column_comment -- 字段注释
                        FROM information_schema.columns c
                                 LEFT JOIN information_schema.key_column_usage kcu
                                           ON c.column_name = kcu.column_name
                                               AND c.table_name = kcu.table_name
                                               AND c.table_schema = kcu.table_schema
                                 LEFT JOIN information_schema.table_constraints tc
                                           ON kcu.constraint_name = tc.constraint_name
                                               AND tc.constraint_type = 'PRIMARY KEY'
                                 LEFT JOIN pg_class pc ON pc.relname = c.table_name
                                 LEFT JOIN pg_namespace pn ON pn.oid = pc.relnamespace AND pn.nspname = c.table_schema
                                 LEFT JOIN pg_attribute pa
                                           ON pa.attrelid = pc.oid AND pa.attname = c.column_name AND pa.attnum > 0
                                 LEFT JOIN pg_description pd ON pd.objoid = pa.attrelid AND pd.objsubid = pa.attnum
                        WHERE c.table_schema = %s
                          AND c.table_name = %s
                        ORDER BY c.ordinal_position;
                        """, (schema_name, table_name))

            # 整理字段信息
            fields = []
            for row in cur.fetchall():
                col_name, col_type, col_length, is_nullable, default_val, is_primary, col_comment = row
                # 补充字段长度信息
                if col_length and col_type in ['character varying', 'varchar', 'char', 'character']:
                    col_type = f"{col_type}({col_length})"

                fields.append({
                    "字段名": col_name,
                    "类型": col_type,
                    "是否主键": is_primary,
                    "是否可为空": is_nullable,
                    "默认值": default_val,
                    "注释": col_comment
                })

        return table_comment, fields
    except ProgrammingError as e:
        return f"表不存在或无权限：{str(e)}", []
    except Exception as e:
        return f"查询表结构失败：{str(e)}", []



def get_all_tables_in_schema(schema_name: str) -> List[str]:
    """获取指定模式下所有用户表"""


    try:
        with conn.cursor() as cur:
            cur.execute("""
                        SELECT table_name
                        FROM information_schema.tables
                        WHERE table_schema = %s
                          AND table_type = 'BASE TABLE'
                        ORDER BY table_name;
                        """, (schema_name,))
            tables = [row[0] for row in cur.fetchall()]
        return tables
    except Exception as e:
        return []



# AI提示词生成
def generate_ai_database_prompt() -> str:
    """
    生成适配AI Agent的数据库结构提示词
    :return: 完整的提示词字符串
    """
    # 基础信息头
    prompt_header = f"""
# 【{DATABASES}数据库完整结构说明】
## 适用场景
请基于以下数据库结构，分析业务需求、编写SQL查询、理解数据关系，要求：
1. 所有SQL语句需适配PostgreSQL语法
2. 优先使用字段注释中的业务含义理解字段用途
3. 涉及多表关联时，需明确说明关联字段和关联逻辑
4. 输出SQL时需包含完整的模式名（如public.表名）

## 数据库基础信息
- 数据库名：{DATABASES}
- 数据库类型：PostgreSQL
- 主机：{DB_CONFIG.get('host', '未知')}
- 端口：{DB_CONFIG.get('port', '未知')}
- 用户名：{DB_CONFIG.get('user', '未知')}
- 数据库密码{DB_CONFIG.get('password', '')}
- 字符编码：UTF-8（支持中文注释）

## 完整表结构详情
"""

    # 遍历所有模式和表，生成结构信息
    schemas = get_all_schemas()
    if not schemas:
        return prompt_header + "\n未查询到任何用户模式，请检查数据库连接或权限"

    schema_details = []
    for schema in schemas:
        schema_details.append(f"\n### 模式（Schema）：{schema}")
        tables = get_all_tables_in_schema(schema)

        if not tables:
            schema_details.append(f"  - 该模式下无用户表")
            continue

        for table in tables:
            table_comment, fields = get_table_structure(schema, table)
            schema_details.append(f"\n  #### 表名：{table}")
            schema_details.append(f"     表注释：{table_comment}")
            schema_details.append(f"     字段详情：")

            if not fields:
                schema_details.append(f"       - 无字段信息（查询失败）")
                continue

            # 格式化字段信息
            for field in fields:
                schema_details.append(
                    f"       - {field['字段名']} | 类型：{field['类型']} | 主键：{field['是否主键']} | 可空：{field['是否可为空']} | 默认值：{field['默认值']} | 注释：{field['注释']}"
                )

    # 拼接最终提示词
    full_prompt = prompt_header + "\n".join(schema_details)

    # 补充使用说明
    full_prompt += f"""

## 使用说明
1. 所有表引用需带上模式名，例如：SELECT * FROM {schemas[0]}.表名;
2. 字段注释包含核心业务含义，是编写SQL的重要依据；
3. 若需修改数据，请先确认字段是否可为空、是否有默认值；
4. 主键字段不可重复，且通常用于表关联。
"""
    return full_prompt

# ai_prompt = generate_ai_database_prompt()

if __name__ == "__main__":
    # 生成AI提示词
    ai_prompt = generate_ai_database_prompt()

    # 保存到文件
    file_path = "src/prompt/database_ai_prompt.txt"
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(ai_prompt)
    except Exception as e:
        raise f"保存文件失败：{str(e)}"