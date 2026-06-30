/**
 * 腾讯云 CloudBase 云函数
 * AI 智能文档问答助手
 */
const cloud = require('@cloudbase/node-sdk');

// 初始化 CloudBase
const app = cloud.init({
  env: 'cg-work-d3geug43lc211422a'
});

// 获取数据库引用
const db = app.database();
const messagesCollection = db.collection('messages');

/**
 * 云函数主入口
 */
exports.main = async (event, context) => {
  try {
    const { httpMethod, path, body, queryStringParameters } = event;

    // 解析请求体
    let requestData = {};
    if (body) {
      requestData = typeof body === 'string' ? JSON.parse(body) : body;
    }

    // 路由处理
    switch (path) {
      case '/health':
        return successResponse({ status: 'healthy', version: '1.0.0' });

      case '/chat':
        if (httpMethod !== 'POST') {
          return errorResponse(405, 'Method not allowed');
        }
        return await handleChat(requestData);

      case '/history':
        if (httpMethod !== 'GET') {
          return errorResponse(405, 'Method not allowed');
        }
        return await handleGetHistory(queryStringParameters);

      case '/clear':
        if (httpMethod !== 'POST') {
          return errorResponse(405, 'Method not allowed');
        }
        return await handleClearHistory();

      default:
        return errorResponse(404, '接口不存在');
    }

  } catch (error) {
    console.error('云函数错误：', error);
    return errorResponse(500, error.message);
  }
};

/**
 * 处理聊天请求
 */
async function handleChat(body) {
  const { message, collection_name = 'default' } = body;

  if (!message) {
    return errorResponse(400, '消息不能为空');
  }

  // 保存用户消息到数据库
  await saveMessage('user', message);

  // 调用 DeepSeek API 获取回答
  const reply = await callDeepSeekAPI(message);

  // 保存 AI 回复到数据库
  await saveMessage('assistant', reply);

  return successResponse({
    reply: reply,
    sources: [] // 简化版本，不包含来源
  });
}

/**
 * 调用 DeepSeek API
 */
async function callDeepSeekAPI(message) {
  const DEEPSEEK_API_KEY = process.env.DEEPSEEK_API_KEY;
  const DEEPSEEK_BASE_URL = 'https://api.deepseek.com';

  try {
    const response = await fetch(`${DEEPSEEK_BASE_URL}/v1/chat/completions`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${DEEPSEEK_API_KEY}`
      },
      body: JSON.stringify({
        model: 'deepseek-chat',
        messages: [
          {
            role: 'system',
            content: '你是一个专业的 AI 助手，请用中文回答问题。'
          },
          {
            role: 'user',
            content: message
          }
        ],
        temperature: 0.7,
        max_tokens: 2000
      })
    });

    const data = await response.json();

    if (data.choices && data.choices[0]) {
      return data.choices[0].message.content;
    } else {
      throw new Error('API 返回格式错误');
    }

  } catch (error) {
    console.error('调用 DeepSeek API 失败：', error);
    throw new Error('调用 AI 服务失败，请稍后重试');
  }
}

/**
 * 保存消息到数据库
 */
async function saveMessage(role, content) {
  try {
    await messagesCollection.add({
      data: {
        role: role,
        content: content,
        timestamp: db.serverDate()
      }
    });
  } catch (error) {
    console.error('保存消息失败：', error);
  }
}

/**
 * 获取历史消息
 */
async function handleGetHistory(queryParams) {
  const limit = parseInt(queryParams?.limit) || 50;

  try {
    const result = await messagesCollection
      .orderBy('timestamp', 'desc')
      .limit(limit)
      .get();

    const messages = result.data.reverse(); // 按时间正序

    return successResponse({ messages });
  } catch (error) {
    console.error('获取历史失败：', error);
    return errorResponse(500, '获取历史失败');
  }
}

/**
 * 清空历史消息
 */
async function handleClearHistory() {
  try {
    // 获取所有消息 ID
    const result = await messagesCollection.get();
    const ids = result.data.map(item => item._id);

    // 批量删除
    if (ids.length > 0) {
      await messagesCollection.where({
        _id: db.command.in(ids)
      }).remove();
    }

    return successResponse({ message: '历史已清空' });
  } catch (error) {
    console.error('清空历史失败：', error);
    return errorResponse(500, '清空历史失败');
  }
}

/**
 * 成功响应
 */
function successResponse(data) {
  return {
    statusCode: 200,
    headers: {
      'Content-Type': 'application/json',
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type'
    },
    body: JSON.stringify(data)
  };
}

/**
 * 错误响应
 */
function errorResponse(statusCode, message) {
  return {
    statusCode: statusCode,
    headers: {
      'Content-Type': 'application/json',
      'Access-Control-Allow-Origin': '*'
    },
    body: JSON.stringify({ error: message })
  };
}
