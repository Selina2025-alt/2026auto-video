"""
飞书集成测试
测试飞书 API 连接和数据读取
"""
import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from feishu.client import FeishuClient
from feishu.table_handler import TableHandler


async def test_feishu():
    """测试飞书集成"""

    print("=" * 60)
    print("飞书集成测试")
    print("=" * 60)

    # 从环境变量获取配置
    app_id = os.getenv('FEISHU_APP_ID', '')
    app_secret = os.getenv('FEISHU_APP_SECRET', '')
    base_token = os.getenv('FEISHU_BASE_TOKEN', '')
    table_id = os.getenv('FEISHU_TABLE_ID', '')

    if not all([app_id, app_secret]):
        print("✗ 未配置飞书应用凭证")
        print("请设置环境变量:")
        print("  FEISHU_APP_ID")
        print("  FEISHU_APP_SECRET")
        return False

    # 创建客户端
    print("\n1. 创建飞书客户端...")
    client = FeishuClient(app_id, app_secret)

    # 获取访问令牌
    print("2. 获取访问令牌...")
    try:
        token = await client.get_access_token()
        if token:
            print(f"   ✓ 成功获取令牌: {token[:20]}...")
        else:
            print("   ✗ 获取令牌失败")
            return False
    except Exception as e:
        print(f"   ✗ 错误: {str(e)}")
        return False

    # 测试表格操作
    if base_token and table_id:
        print("\n3. 创建表格处理器...")
        table_handler = TableHandler(client, base_token, table_id)

        # 读取表格数据
        print("4. 读取表格数据...")
        try:
            records = await table_handler.get_records()
            print(f"   ✓ 成功读取 {len(records)} 条记录")

            # 显示前3条
            for i, record in enumerate(records[:3], 1):
                print(f"\n   记录 {i}:")
                for key, value in record.get('fields', {}).items():
                    print(f"     {key}: {value}")

        except Exception as e:
            print(f"   ✗ 读取失败: {str(e)}")
            return False

    print("\n" + "=" * 60)
    print("✓ 飞书集成测试完成")
    print("=" * 60)
    return True


if __name__ == "__main__":
    success = asyncio.run(test_feishu())
    sys.exit(0 if success else 1)
